#!/usr/bin/env python3
"""Template-safe local-main Knowledge / Impact service helpers.

A Git-backed scan reads the local ``refs/heads/main`` snapshot without checking
it out. A non-Git fixture falls back to the current directory so tests can stay
self-contained. The template ships capability and policy only; it never seeds
sibling-repository business records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

CONFIG = "scripts/python/project_health_knowledge_config.json"
LATEST = "logs/ci/project-health-knowledge/latest.json"
ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".svg", ".webp", ".ogg", ".wav", ".mp3",
    ".ttf", ".otf", ".glb",
}
SPECIAL_TEXT_NAMES = {"workflow.md", "AGENTS.md", "README.md", "DELIVERY_PROFILE.md"}
DEFAULT_SOURCE_BINDINGS = {
    "tasks": ".taskmaster/tasks",
    "product_requirements": "docs/prd",
    "architecture_decisions": "docs/adr",
    "architecture": "docs/architecture",
    "agent_rules": "docs/agents",
    "workflows": "docs/workflows",
    "domain_code": "Game.Core",
    "engine_code": "Game.Godot",
    "domain_tests": "Game.Core.Tests",
    "engine_tests": "Tests.Godot",
    "project_entry": "README.md",
    "repository_rules": "AGENTS.md",
    "delivery_profile": "DELIVERY_PROFILE.md",
    "root_workflow": "workflow.md",
    "testing_rules": "docs/testing-framework.md",
}
DEFAULT_CONFIG: dict[str, Any] = {
    "schema": "godot-project-knowledge.config.v3",
    "source_paths": list(DEFAULT_SOURCE_BINDINGS.values()),
    "source_path_bindings": DEFAULT_SOURCE_BINDINGS,
    "gdd_paths": ["docs/gdd"],
    "task_scene_bindings": [],
    "query_aliases": {},
    "include_extensions": [
        ".md", ".txt", ".json", ".cs", ".gd", ".tscn", ".tres", ".cfg",
        ".ini", ".csv", ".toml", ".yml", ".yaml",
    ],
    "max_file_bytes": 512000,
    "max_asset_bytes": 16 * 1024 * 1024,
    "max_results": 50,
}


def base_dir(root: str | Path = ".") -> Path:
    return Path(root).resolve()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _git_process(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    kwargs: dict[str, Any] = {"cwd": root, "capture_output": True, "check": False, "timeout": 120}
    if text:
        kwargs.update({"text": True, "encoding": "utf-8", "errors": "replace"})
    return subprocess.run(["git", *args], **kwargs)


def _git(root: Path, *args: str) -> str:
    proc = _git_process(root, *args)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _git_bytes(root: Path, *args: str) -> bytes:
    proc = _git_process(root, *args, text=False)
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(detail or "Git snapshot read failed")
    return proc.stdout


def revision(root: Path) -> str:
    """Return current workspace HEAD for callers that explicitly need it."""
    return _git(root, "rev-parse", "HEAD") or "workspace"


def main_revision(root: Path) -> str | None:
    value = _git(root, "rev-parse", "--verify", "refs/heads/main")
    return value if re.fullmatch(r"[0-9a-f]{40}", value or "") else None


def _string_list(value: Any, name: str, *, allow_empty: bool = True) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{name} must be a list of strings")
    result = [item.strip().replace("\\", "/") for item in value if item.strip()]
    if not allow_empty and not result:
        raise ValueError(f"{name} must contain at least one path")
    return result


def _validate_relative(value: str, name: str) -> str:
    text = value.strip().replace("\\", "/")
    posix = PurePosixPath(text)
    if not text or text == "." or posix.is_absolute() or ".." in posix.parts or ":" in text or any(part in {"", "."} for part in posix.parts):
        raise ValueError(f"{name} contains an unsafe repository path: {value!r}")
    return text


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    raw_bindings = config.get("source_path_bindings", DEFAULT_SOURCE_BINDINGS)
    if not isinstance(raw_bindings, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in raw_bindings.items()):
        raise ValueError("source_path_bindings must be a string-to-string object")
    bindings = {str(key): _validate_relative(value, f"source_path_bindings[{key!r}]") for key, value in raw_bindings.items() if value.strip()}
    source_paths = _string_list(config.get("source_paths", list(bindings.values())), "source_paths")
    if not source_paths:
        source_paths = list(bindings.values())
    source_paths = [_validate_relative(item, "source_paths") for item in source_paths]
    gdd_paths = [_validate_relative(item, "gdd_paths") for item in _string_list(config.get("gdd_paths", DEFAULT_CONFIG["gdd_paths"]), "gdd_paths")]
    exts = [item.casefold() for item in _string_list(config.get("include_extensions", DEFAULT_CONFIG["include_extensions"]), "include_extensions", allow_empty=False)]
    if not all(item.startswith(".") and "/" not in item for item in exts):
        raise ValueError("include_extensions must contain extensions")
    task_scene_bindings = config.get("task_scene_bindings", [])
    if not isinstance(task_scene_bindings, list) or not all(isinstance(item, dict) for item in task_scene_bindings):
        raise ValueError("task_scene_bindings must be an array of objects")
    query_aliases = config.get("query_aliases", {})
    if not isinstance(query_aliases, dict):
        raise ValueError("query_aliases must be an object")
    normalized_aliases: dict[str, list[str]] = {}
    for key, value in query_aliases.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("query alias keys must be non-empty strings")
        aliases = [value.strip()] if isinstance(value, str) and value.strip() else (_string_list(value, f"query_aliases[{key!r}]") if not isinstance(value, str) else [])
        if any(len(item) > 500 for item in aliases):
            raise ValueError("query aliases are limited to 500 characters")
        normalized_aliases[key.strip()] = aliases
    max_file_bytes = int(config.get("max_file_bytes", DEFAULT_CONFIG["max_file_bytes"]))
    max_asset_bytes = int(config.get("max_asset_bytes", DEFAULT_CONFIG["max_asset_bytes"]))
    max_results = int(config.get("max_results", DEFAULT_CONFIG["max_results"]))
    if not 1024 <= max_file_bytes <= 5_000_000:
        raise ValueError("max_file_bytes out of range")
    if not 1024 <= max_asset_bytes <= 64 * 1024 * 1024:
        raise ValueError("max_asset_bytes out of range")
    if not 1 <= max_results <= 200:
        raise ValueError("max_results out of range")
    return {
        "schema": "godot-project-knowledge.config.v3",
        "source_paths": list(dict.fromkeys(source_paths)),
        "source_path_bindings": bindings,
        "gdd_paths": list(dict.fromkeys(gdd_paths)),
        "task_scene_bindings": task_scene_bindings,
        "query_aliases": normalized_aliases,
        "include_extensions": list(dict.fromkeys(exts)),
        "max_file_bytes": max_file_bytes,
        "max_asset_bytes": max_asset_bytes,
        "max_results": max_results,
    }


def load_config(root: str | Path = ".") -> dict[str, Any]:
    repo = base_dir(root)
    path = repo / CONFIG
    return validate_config(read_json(path) if path.exists() else DEFAULT_CONFIG.copy())


def save_config(root: str | Path, config: dict[str, Any]) -> dict[str, Any]:
    repo = base_dir(root)
    validated = validate_config(config)
    write_json(repo / CONFIG, validated)
    return validated


def safe_file(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel or "\\" in rel or ":" in rel:
        raise ValueError("unsafe path")
    posix = PurePosixPath(rel)
    if posix.is_absolute() or rel == "." or ".." in posix.parts:
        raise ValueError("unsafe path")
    candidate = (root / Path(*posix.parts)).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("path escapes repository")
    return candidate


def _configured_paths(config: dict[str, Any]) -> list[str]:
    values = [*config["source_paths"], *config.get("gdd_paths", [])]
    return list(dict.fromkeys(item.rstrip("/") for item in values if item))


def _in_scope(rel: str, config: dict[str, Any]) -> bool:
    return any(rel == prefix or rel.startswith(prefix + "/") for prefix in _configured_paths(config))


def _is_supported(rel: str, config: dict[str, Any]) -> bool:
    suffix = PurePosixPath(rel).suffix.casefold()
    return suffix in set(config["include_extensions"]) or suffix in ASSET_EXTENSIONS or PurePosixPath(rel).name in SPECIAL_TEXT_NAMES


def _workspace_paths(root: Path, config: dict[str, Any]) -> Iterable[str]:
    for entry in _configured_paths(config):
        path = safe_file(root, entry)
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if _is_supported(rel, config):
                yield rel
            continue
        if not path.is_dir():
            continue
        for item in path.rglob("*"):
            if not item.is_file():
                continue
            rel_parts = item.relative_to(root).parts
            if any(part in {".git", ".godot", "bin", "obj", "logs", "__pycache__"} for part in rel_parts):
                continue
            rel = item.relative_to(root).as_posix()
            if _is_supported(rel, config):
                yield rel


def _main_paths(root: Path, config: dict[str, Any], revision_id: str) -> list[str]:
    proc = _git_process(root, "ls-tree", "-r", "--name-only", revision_id)
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or "Unable to enumerate local main")
    return [rel for rel in proc.stdout.splitlines() if _in_scope(rel, config) and _is_supported(rel, config)]


def _read_at(root: Path, rel: str, snapshot_mode: str, revision_id: str) -> bytes:
    if snapshot_mode == "main":
        return _git_bytes(root, "show", f"{revision_id}:{rel}")
    return safe_file(root, rel).read_bytes()


def _binding_for(rel: str, config: dict[str, Any]) -> str | None:
    return next((key for key, value in config["source_path_bindings"].items() if rel == value.rstrip("/") or rel.startswith(value.rstrip("/") + "/")), None)


def _is_gdd(rel: str, config: dict[str, Any]) -> bool:
    return any(rel == value.rstrip("/") or rel.startswith(value.rstrip("/") + "/") for value in config["gdd_paths"])


def scan(root: str | Path = ".", config: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = base_dir(root)
    cfg = validate_config(config or load_config(repo))
    lock = repo / "logs/ci/project-health-knowledge/scan.lock"
    try:
        lock.mkdir(parents=True)
    except FileExistsError as exc:
        raise RuntimeError("Knowledge scan is already active") from exc
    try:
        main = main_revision(repo)
        snapshot_mode = "main" if main else "workspace"
        revision_id = main or revision(repo)
        paths = _main_paths(repo, cfg, revision_id) if snapshot_mode == "main" else sorted(set(_workspace_paths(repo, cfg)))
        records: list[dict[str, Any]] = []
        for rel in sorted(set(paths), key=str.casefold):
            try:
                raw = _read_at(repo, rel, snapshot_mode, revision_id)
            except (OSError, ValueError):
                continue
            suffix = PurePosixPath(rel).suffix.casefold()
            is_asset = suffix in ASSET_EXTENSIONS
            if len(raw) > (cfg["max_asset_bytes"] if is_asset else cfg["max_file_bytes"]):
                continue
            text = None
            if not is_asset:
                try:
                    text = raw.decode("utf-8-sig")
                except UnicodeDecodeError:
                    continue
            records.append({
                "path": rel, "kind": suffix.lstrip(".") or "text", "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(), "lines": text.count("\n") + 1 if text is not None else None,
                "searchable": text is not None, "asset": is_asset, "source_binding": _binding_for(rel, cfg),
                "gdd_supplement": _is_gdd(rel, cfg),
            })
        record_paths = {record["path"] for record in records}
        payload = {
            "schema": "godot-project-knowledge.scan.v3", "revision": revision_id,
            "branch": "main" if snapshot_mode == "main" else "workspace", "snapshot_mode": snapshot_mode,
            "scanned_at": datetime.now(timezone.utc).isoformat(), "config": cfg, "records": records,
            "counts": {"files": len(records), "searchable": sum(bool(record["searchable"]) for record in records), "assets": sum(bool(record["asset"]) for record in records)},
            "configured_gdd_sources": cfg["gdd_paths"],
            "gdd_files": [{"path": path, "available": path in record_paths, "role": "supplementary-design-source"} for path in cfg["gdd_paths"]],
            "publication": {"matches_scan": False, "note": "Exploratory scan only; it is not a frozen Knowledge publication."},
        }
        write_json(repo / LATEST, payload)
        return payload
    finally:
        try:
            lock.rmdir()
        except OSError:
            pass


def latest(root: str | Path = ".") -> dict[str, Any]:
    repo = base_dir(root)
    path = repo / LATEST
    return read_json(path) if path.exists() else scan(repo)


def snapshot_bytes(root: str | Path, rel: str, state: dict[str, Any] | None = None) -> bytes:
    repo = base_dir(root)
    snapshot = state or latest(repo)
    record = next((item for item in snapshot.get("records", []) if item.get("path") == rel), None)
    if record is None:
        raise ValueError("path is not in the scanned manifest")
    raw = _read_at(repo, rel, str(snapshot.get("snapshot_mode") or "workspace"), str(snapshot.get("revision") or ""))
    if hashlib.sha256(raw).hexdigest() != record.get("sha256"):
        raise ValueError("snapshot content does not match the scan manifest; scan again")
    return raw


def snapshot_text(root: str | Path, rel: str, state: dict[str, Any] | None = None) -> str:
    snapshot = state or latest(root)
    record = next((item for item in snapshot.get("records", []) if item.get("path") == rel), None)
    if record is None or not record.get("searchable", False):
        raise ValueError("path is not a scanned UTF-8 text source")
    return snapshot_bytes(root, rel, snapshot).decode("utf-8-sig")


def _query_terms(config: dict[str, Any], text: str) -> tuple[list[str], list[str]]:
    queries = [text.strip()] if text.strip() else []
    folded = text.casefold()
    for key, aliases in config.get("query_aliases", {}).items():
        if key.casefold() in folded:
            queries.extend(aliases)
    queries = list(dict.fromkeys(query for query in queries if query))
    tokens = [token.casefold() for query_text in queries for token in re.findall(r"[\w.-]+", query_text, flags=re.UNICODE) if token.strip()]
    return queries, list(dict.fromkeys(tokens))


def _action_kind(path: str) -> str:
    lowered = path.casefold()
    if lowered.startswith(".taskmaster/tasks/"):
        return "tasks"
    if lowered.endswith((".cfg", ".ini", ".toml", ".json", ".tres", ".csv", ".yaml", ".yml")):
        return "configuration"
    if "test" in lowered or lowered.startswith(("tests.godot/", "game.core.tests/")):
        return "tests"
    if lowered.endswith((".cs", ".gd", ".tscn")) or lowered.startswith(("game.core/", "game.godot/")):
        return "code"
    return "secondary"


def query(root: str | Path, text: str, *, limit: int | None = None) -> dict[str, Any]:
    repo = base_dir(root)
    state = latest(repo)
    cfg = validate_config(state.get("config") or load_config(repo))
    queries, wanted = _query_terms(cfg, text)
    empty = {"schema": "godot-project-knowledge.query.v3", "query": text, "queries": queries, "revision": state.get("revision"), "results": [], "actionable": {"tasks": [], "configuration": [], "code": [], "tests": [], "secondary": []}, "gdd_supplements": []}
    if not wanted:
        return empty
    cap = min(int(limit or cfg["max_results"]), cfg["max_results"])
    results: list[dict[str, Any]] = []
    for record in state.get("records", []):
        if not record.get("searchable"):
            continue
        rel = str(record["path"])
        try:
            body = snapshot_text(repo, rel, state)
        except (ValueError, UnicodeDecodeError):
            continue
        haystack = (rel + "\n" + body).casefold()
        score = sum(haystack.count(term) for term in wanted)
        if score <= 0:
            continue
        positions = [haystack.find(term) for term in wanted if haystack.find(term) >= 0]
        first = min(positions) if positions else 0
        line = haystack[:first].count("\n") + 1
        snippet_lines = body.splitlines()[max(0, line - 2): line + 2]
        results.append({"path": rel, "score": score, "line": line, "snippet": "\n".join(snippet_lines)[:1200], "category": _action_kind(rel), "source_binding": record.get("source_binding"), "gdd_supplement": bool(record.get("gdd_supplement"))})
    results.sort(key=lambda item: (-item["score"], item["path"]))
    limited = results[:cap]
    actionable = {key: [] for key in ("tasks", "configuration", "code", "tests", "secondary")}
    for item in limited:
        actionable[item["category"]].append(item)
    return {**empty, "results": limited, "actionable": actionable, "gdd_supplements": [item for item in limited if item.get("gdd_supplement")]}


def _walk_rows(value: Any):
    if isinstance(value, dict):
        if ("id" in value or "taskmaster_id" in value) and any(key in value for key in ("title", "status", "acceptance", "acceptance_criteria", "test_refs", "testStrategy", "test_strategy")):
            yield value
        for child in value.values():
            yield from _walk_rows(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_rows(child)


def _task_payloads(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for record in state.get("records", []):
        rel = str(record.get("path") or "")
        if not rel.startswith(".taskmaster/tasks/") or not rel.endswith(".json") or not record.get("searchable"):
            continue
        try:
            payloads[rel] = json.loads(snapshot_text(root, rel, state))
        except (ValueError, json.JSONDecodeError):
            continue
    return payloads


def task_rows(root: str | Path, state: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    repo = base_dir(root)
    snapshot = state or latest(repo)
    payloads = _task_payloads(repo, snapshot)
    master: list[dict[str, Any]] = []
    payload = payloads.get(".taskmaster/tasks/tasks.json")
    if isinstance(payload, dict) and isinstance(payload.get("master"), dict) and isinstance(payload["master"].get("tasks"), list):
        master = [row for row in payload["master"]["tasks"] if isinstance(row, dict) and str(row.get("id") or "").strip()]
    if not master:
        seen: set[str] = set()
        for data in payloads.values():
            for row in _walk_rows(data):
                task_id = str(row.get("id") or "").strip()
                if task_id and task_id not in seen:
                    seen.add(task_id)
                    master.append(row)
    result: list[dict[str, Any]] = []
    for task in master:
        task_id = str(task.get("id") or "").strip()
        sources: list[str] = []
        mappings: dict[str, list[dict[str, Any]]] = {}
        for source, data in payloads.items():
            matched = [row for row in _walk_rows(data) if str(row.get("id", row.get("taskmaster_id", ""))).strip() == task_id]
            if matched:
                sources.append(source)
                mappings[source] = matched
        deps = task.get("dependencies") or []
        result.append({"id": task_id, "title": str(task.get("title") or ""), "status": str(task.get("status") or ""), "dependencies": [str(value) for value in deps] if isinstance(deps, list) else [], "recommendedSubtasks": task.get("recommendedSubtasks"), "sources": sorted(set(sources)), "task": task, "mappings": mappings})
    return sorted(result, key=lambda row: (not row["id"].isdigit(), int(row["id"]) if row["id"].isdigit() else row["id"]))


def task_details(root: str | Path, task_id: str) -> dict[str, Any]:
    repo = base_dir(root)
    state = latest(repo)
    needle = str(task_id).strip()
    row = next((item for item in task_rows(repo, state) if item["id"] == needle), None)
    cfg = validate_config(state.get("config") or load_config(repo))
    scene_bindings = [item for item in cfg.get("task_scene_bindings", []) if str(item.get("task_id", item.get("taskmaster_id", ""))).strip() == needle]
    sources = [{"path": path, "tasks": rows} for path, rows in row["mappings"].items()] if row else []
    return {"schema": "godot-project-knowledge.task.v3", "task_id": needle, "revision": state.get("revision"), "initialized": row is not None, "task": row["task"] if row else None, "sources": sources, "scene_bindings": scene_bindings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan")
    q = sub.add_parser("query"); q.add_argument("text")
    t = sub.add_parser("task"); t.add_argument("--task-id", required=True)
    sub.add_parser("config")
    args = parser.parse_args(argv)
    if args.command == "scan": result = scan(args.repo_root)
    elif args.command == "query": result = query(args.repo_root, args.text)
    elif args.command == "task": result = task_details(args.repo_root, args.task_id)
    else: result = load_config(args.repo_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
