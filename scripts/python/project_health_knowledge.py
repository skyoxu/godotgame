#!/usr/bin/env python3
"""Template-safe Knowledge + Impact backend for the local project-health UI.

The module intentionally treats repository sources as authoritative. It does not
invent task data and it stays useful when a freshly copied template has no
.taskmaster/tasks files yet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TEXT_SUFFIXES = {
    ".cs", ".gd", ".gdshader", ".tscn", ".tres", ".json", ".md", ".txt",
    ".py", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".xml", ".csproj",
    ".sln", ".props", ".targets", ".sh", ".ps1", ".js", ".ts", ".html",
    ".css",
}
DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": "godot-project-knowledge.config.v1",
    "source_paths": [
        ".taskmaster/tasks",
        "docs",
        "scripts",
        "Game.Core",
        "Game.Godot",
        "Game.Core.Tests",
        "Game.Godot.Tests",
    ],
    "gdd_paths": [],
    "query_aliases": {},
    "task_scene_bindings": [],
}
CONSUMERS = {"repository-session", "chapter4", "chapter5", "chapter6", "review"}
MAX_TEXT_BYTES = 512 * 1024
MAX_SOURCES = 5000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _run_git(root: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, text=True, encoding="utf-8",
        capture_output=True, check=False,
    )
    if check and completed.returncode:
        raise RuntimeError((completed.stderr or completed.stdout).strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def _repo_root(root: Path | str) -> Path:
    resolved = Path(root).resolve()
    top = _run_git(resolved, "rev-parse", "--show-toplevel")
    return Path(top).resolve()


def _logs_dir(root: Path) -> Path:
    path = root / "logs" / "ci" / "project-health-knowledge"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path(root: Path) -> Path:
    return root / "scripts" / "python" / "project_health_knowledge_config.json"


def load_config(root: Path) -> dict[str, Any]:
    path = config_path(root)
    if not path.is_file():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("project health knowledge config must be a JSON object")
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    merged.update(payload)
    for key in ("source_paths", "gdd_paths", "task_scene_bindings"):
        if not isinstance(merged.get(key), list):
            raise ValueError(f"config.{key} must be an array")
    if not isinstance(merged.get("query_aliases"), dict):
        raise ValueError("config.query_aliases must be an object")
    return merged


def save_config(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    candidate = json.loads(json.dumps(DEFAULT_CONFIG))
    candidate.update(payload)
    # Reuse validation and keep config repository-relative only.
    for key in ("source_paths", "gdd_paths"):
        values = candidate.get(key)
        if not isinstance(values, list):
            raise ValueError(f"config.{key} must be an array")
        normalized: list[str] = []
        for value in values:
            text = str(value).replace("\\", "/").strip().strip("/")
            if not text or text.startswith("../") or "/../" in f"/{text}/" or Path(text).is_absolute():
                raise ValueError(f"config.{key} contains unsafe path: {value!r}")
            normalized.append(text)
        candidate[key] = normalized
    if not isinstance(candidate.get("query_aliases"), dict):
        raise ValueError("config.query_aliases must be an object")
    if not isinstance(candidate.get("task_scene_bindings"), list):
        raise ValueError("config.task_scene_bindings must be an array")
    path = config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return candidate


def _main_revision(root: Path, *, fetch: bool) -> tuple[str, str, str | None]:
    fetch_error: str | None = None
    if fetch:
        completed = subprocess.run(
            ["git", "fetch", "--quiet", "origin", "main"], cwd=root,
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        if completed.returncode:
            fetch_error = (completed.stderr or completed.stdout).strip() or "git fetch origin main failed"
    for ref in ("refs/remotes/origin/main", "refs/heads/main", "HEAD"):
        completed = subprocess.run(
            ["git", "rev-parse", "--verify", ref], cwd=root,
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            return completed.stdout.strip(), ref, fetch_error
    raise RuntimeError("unable to resolve a repository revision")


def _paths_for_revision(root: Path, revision: str, configured_paths: Iterable[str]) -> list[str]:
    args = ["ls-tree", "-r", "--name-only", revision, "--"]
    configured = [str(value) for value in configured_paths if str(value).strip()]
    args.extend(configured or ["."])
    output = _run_git(root, *args)
    paths = []
    for line in output.splitlines():
        path = line.strip().replace("\\", "/")
        if path and Path(path).suffix.lower() in TEXT_SUFFIXES:
            paths.append(path)
        if len(paths) >= MAX_SOURCES:
            break
    return sorted(dict.fromkeys(paths))


def _read_at(root: Path, revision: str, path: str) -> str | None:
    completed = subprocess.run(
        ["git", "show", f"{revision}:{path}"], cwd=root,
        capture_output=True, check=False,
    )
    if completed.returncode or len(completed.stdout) > MAX_TEXT_BYTES:
        return None
    try:
        return completed.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _load_json_at(root: Path, revision: str, path: str) -> Any:
    text = _read_at(root, revision, path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _task_rows(root: Path, revision: str) -> list[dict[str, Any]]:
    payload = _load_json_at(root, revision, ".taskmaster/tasks/tasks.json")
    if not isinstance(payload, dict):
        return []
    master = payload.get("master")
    rows = master.get("tasks") if isinstance(master, dict) else None
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def latest_state(root: Path) -> dict[str, Any]:
    path = _logs_dir(root) / "latest.json"
    if not path.is_file():
        return {
            "schema_version": "godot-project-knowledge.snapshot.v1",
            "status": "uninitialized",
            "message": "No knowledge scan exists yet. Run scan to index main.",
            "tasks": {"total": 0, "initialized": False},
            "sources": [],
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "invalid", "message": "latest.json is unreadable", "tasks": {"total": 0}, "sources": []}
    return payload if isinstance(payload, dict) else {"status": "invalid", "tasks": {"total": 0}, "sources": []}


def scan(root: Path, *, fetch: bool = True) -> dict[str, Any]:
    root = _repo_root(root)
    config = load_config(root)
    revision, revision_ref, fetch_error = _main_revision(root, fetch=fetch)
    source_paths = _paths_for_revision(root, revision, config.get("source_paths", []))
    tasks = _task_rows(root, revision)
    head = _run_git(root, "rev-parse", "HEAD")
    available_roots: list[str] = []
    missing_roots: list[str] = []
    tree_names = set(_run_git(root, "ls-tree", "-r", "--name-only", revision).splitlines())
    for configured in config.get("source_paths", []):
        prefix = str(configured).rstrip("/") + "/"
        if configured in tree_names or any(name.startswith(prefix) for name in tree_names):
            available_roots.append(configured)
        else:
            missing_roots.append(configured)
    payload = {
        "schema_version": "godot-project-knowledge.snapshot.v1",
        "status": "ok",
        "revision": revision,
        "revision_ref": revision_ref,
        "workspace_head": head,
        "snapshot_stale": revision != head,
        "scanned_at": _now(),
        "fetch_error": fetch_error,
        "source_roots": {"available": available_roots, "missing": missing_roots},
        "sources": source_paths,
        "source_count": len(source_paths),
        "tasks": {"total": len(tasks), "initialized": bool(tasks)},
        "config": config,
    }
    path = _logs_dir(root) / "latest.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _tokens(query: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[A-Za-z0-9_.:/\\-]+|[\u4e00-\u9fff]+", query) if len(token.strip()) >= 2]


def _score(path: str, text: str, tokens: list[str]) -> tuple[int, list[str]]:
    path_l = path.lower()
    text_l = text.lower()
    score = 0
    evidence: list[str] = []
    for token in tokens:
        if token in path_l:
            score += 12
            evidence.append(f"path:{token}")
        count = min(text_l.count(token), 6)
        if count:
            score += count * 2
            evidence.append(f"text:{token}:{count}")
    if path.endswith((".json", ".cfg", ".ini", ".tres")):
        score += 1
    return score, evidence


def _kind(path: str) -> str:
    lower = path.lower()
    if "/test" in lower or lower.endswith("test.py") or ".tests/" in lower:
        return "tests"
    if lower.endswith((".json", ".cfg", ".ini", ".tres")) or "/config" in lower:
        return "configuration"
    if lower.endswith((".cs", ".gd", ".py", ".js", ".ts")):
        return "code"
    return "knowledge"


def _task_matches(tasks: list[dict[str, Any]], tokens: list[str]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for task in tasks:
        haystack = " ".join(str(task.get(key) or "") for key in ("id", "title", "description", "details")).lower()
        score = sum(10 for token in tokens if token in haystack)
        if score:
            matches.append({"task_id": task.get("id"), "title": task.get("title"), "status": task.get("status"), "score": score})
    return sorted(matches, key=lambda item: (-int(item["score"]), str(item.get("task_id"))))[:20]


def _impact_preview(root: Path, revision: str, target_path: str, sources: list[str]) -> dict[str, Any]:
    target_path = target_path.replace("\\", "/")
    if target_path not in sources:
        return {"target": target_path, "status": "not-in-snapshot", "references": [], "omissions": []}
    stem = Path(target_path).stem.lower()
    filename = Path(target_path).name.lower()
    references: list[dict[str, Any]] = []
    for path in sources:
        if path == target_path:
            continue
        text = _read_at(root, revision, path)
        if not text:
            continue
        lower = text.lower()
        count = lower.count(filename) + (lower.count(stem) if stem != filename else 0)
        if count:
            references.append({"path": path, "matches": min(count, 99), "kind": _kind(path)})
    references.sort(key=lambda item: (-int(item["matches"]), str(item["path"])))
    return {
        "schema_version": "godot-project-knowledge.impact-preview.v1",
        "handoff_eligible": False,
        "target": target_path,
        "status": "ok",
        "references": references[:50],
        "omissions": [],
    }


def query(root: Path, request: dict[str, Any]) -> dict[str, Any]:
    root = _repo_root(root)
    state = latest_state(root)
    if state.get("status") != "ok":
        state = scan(root, fetch=False)
    revision = str(state["revision"])
    raw_query = str(request.get("query") or "").strip()
    if not raw_query:
        raise ValueError("query is required")
    consumer = str(request.get("consumer") or "repository-session")
    if consumer not in CONSUMERS:
        raise ValueError(f"unsupported consumer: {consumer}")
    config = load_config(root)
    aliases = config.get("query_aliases", {})
    expanded = [raw_query]
    extra = aliases.get(raw_query) if isinstance(aliases, dict) else None
    if isinstance(extra, list):
        expanded.extend(str(value) for value in extra if str(value).strip())
    tokens = _tokens(" ".join(expanded))
    sources = [str(path) for path in state.get("sources", [])]
    scored: list[dict[str, Any]] = []
    for path in sources:
        text = _read_at(root, revision, path)
        if text is None:
            continue
        score, evidence = _score(path, text, tokens)
        if score:
            scored.append({"path": path, "score": score, "kind": _kind(path), "evidence": evidence[:8]})
    scored.sort(key=lambda item: (-int(item["score"]), str(item["path"])))
    tasks = _task_rows(root, revision)
    actionable = {
        "tasks": _task_matches(tasks, tokens),
        "configuration": [item for item in scored if item["kind"] == "configuration"][:20],
        "code": [item for item in scored if item["kind"] == "code"][:20],
        "tests": [item for item in scored if item["kind"] == "tests"][:20],
    }
    target = request.get("target")
    target_path = ""
    if isinstance(target, dict) and target.get("type") == "file":
        target_path = str(target.get("id") or "")
    if not target_path and scored:
        target_path = str(scored[0]["path"])
    impact = _impact_preview(root, revision, target_path, sources) if target_path else None
    response = {
        "schema_version": "godot-project-knowledge.query.v1",
        "consumer": consumer,
        "query": raw_query,
        "executed_queries": expanded,
        "revision": revision,
        "workspace_head": state.get("workspace_head"),
        "snapshot_stale": bool(state.get("snapshot_stale")),
        "knowledge": scored[:30],
        "actionable_results": actionable,
        "impact_targets": [{"type": "file", "id": item["path"], "score": item["score"]} for item in scored[:30]],
        "impact_preview": impact,
        "handoff_eligible": False,
        "task_data_initialized": bool(tasks),
    }
    queries_dir = _logs_dir(root) / "queries"
    queries_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    (queries_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{digest}.json").write_text(
        json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return response


def tasks_page(root: Path, page: int = 1, page_size: int = 20) -> dict[str, Any]:
    root = _repo_root(root)
    state = latest_state(root)
    if state.get("status") != "ok":
        state = scan(root, fetch=False)
    rows = _task_rows(root, str(state["revision"]))
    page_size = max(1, min(int(page_size), 100))
    pages = max(1, (len(rows) + page_size - 1) // page_size)
    page = max(1, min(int(page), pages))
    start = (page - 1) * page_size
    return {
        "page": page, "pages": pages, "page_size": page_size, "total": len(rows),
        "initialized": bool(rows), "items": rows[start:start + page_size],
    }


def task_detail(root: Path, task_id: str) -> dict[str, Any]:
    page = tasks_page(root, 1, 100000)
    for row in page["items"]:
        if str(row.get("id")) == str(task_id):
            return {"status": "ok", "task": row}
    return {"status": "not-found", "task_id": str(task_id), "initialized": bool(page.get("initialized"))}


def runtime_verify(root: Path, task_ids: list[str]) -> dict[str, Any]:
    # The template must not invent executable task commands. Preserve the same UI
    # operation with an explicit evidence-only result until a business repo wires
    # task-specific runtime assertions.
    return {
        "schema_version": "godot-project-knowledge.runtime.v1",
        "status": "not-configured",
        "task_ids": [str(value) for value in task_ids],
        "results": [
            {"task_id": str(value), "status": "not-configured", "reason": "No task runtime command is declared by the template."}
            for value in task_ids
        ],
    }


def _print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Template-safe project-health Knowledge + Impact CLI")
    parser.add_argument("action", choices=("scan", "status", "query", "tasks", "task", "config", "runtime"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--task-id")
    parser.add_argument("--no-fetch", action="store_true")
    args = parser.parse_args(argv)
    root = _repo_root(args.repo_root)
    try:
        if args.action == "scan":
            _print(scan(root, fetch=not args.no_fetch))
        elif args.action == "status":
            _print(latest_state(root))
        elif args.action == "tasks":
            _print(tasks_page(root, args.page))
        elif args.action == "task":
            if not args.task_id:
                raise ValueError("--task-id is required")
            _print(task_detail(root, args.task_id))
        elif args.action == "config":
            _print(load_config(root))
        elif args.action == "query":
            _print(query(root, json.load(sys.stdin)))
        elif args.action == "runtime":
            payload = json.load(sys.stdin)
            ids = payload.get("task_ids", []) if isinstance(payload, dict) else []
            _print(runtime_verify(root, [str(value) for value in ids]))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        _print({"status": "error", "error": str(exc)})
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
