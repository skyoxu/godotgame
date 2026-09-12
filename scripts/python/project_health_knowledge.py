#!/usr/bin/env python3
"""Template-safe local Knowledge / Impact service helpers.

All data is derived from the current repository. The template ships policy and
schema only: it never seeds sibling-repository task IDs, gameplay entities,
asset mappings, hashes, or runtime evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

CONFIG = "scripts/python/project_health_knowledge_config.json"
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
    "schema": "godot-project-knowledge.config.v2",
    "source_paths": list(DEFAULT_SOURCE_BINDINGS.values()),
    "source_path_bindings": DEFAULT_SOURCE_BINDINGS,
    "gdd_paths": ["docs/gdd"],
    "task_scene_bindings": [],
    "query_aliases": {},
    "include_extensions": [".md", ".json", ".cs", ".gd", ".tscn", ".tres", ".cfg", ".toml", ".yml", ".yaml"],
    "max_file_bytes": 512000,
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


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False, encoding="utf-8", errors="replace")
    return proc.stdout.strip() if proc.returncode == 0 else ""


def revision(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD") or "workspace"


def _string_list(value: Any, name: str, *, allow_empty: bool = True) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{name} must be a list of strings")
    result = [item.strip() for item in value if item.strip()]
    if not allow_empty and not result:
        raise ValueError(f"{name} must contain at least one path")
    return result


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    raw_bindings = config.get("source_path_bindings", DEFAULT_SOURCE_BINDINGS)
    if not isinstance(raw_bindings, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in raw_bindings.items()):
        raise ValueError("source_path_bindings must be a string-to-string object")
    bindings = {str(key): value.strip() for key, value in raw_bindings.items() if value.strip()}
    source_paths = _string_list(config.get("source_paths", list(bindings.values())), "source_paths")
    if not source_paths:
        source_paths = list(bindings.values())
    gdd_paths = _string_list(config.get("gdd_paths", DEFAULT_CONFIG["gdd_paths"]), "gdd_paths")
    exts = _string_list(config.get("include_extensions", DEFAULT_CONFIG["include_extensions"]), "include_extensions", allow_empty=False)
    if not all(item.startswith(".") for item in exts):
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
        if isinstance(value, str):
            aliases = [value.strip()] if value.strip() else []
        else:
            aliases = _string_list(value, f"query_aliases[{key!r}]")
        normalized_aliases[key.strip()] = aliases
    max_file_bytes = int(config.get("max_file_bytes", DEFAULT_CONFIG["max_file_bytes"]))
    max_results = int(config.get("max_results", DEFAULT_CONFIG["max_results"]))
    if not 1024 <= max_file_bytes <= 5_000_000:
        raise ValueError("max_file_bytes out of range")
    if not 1 <= max_results <= 200:
        raise ValueError("max_results out of range")
    return {
        "schema": "godot-project-knowledge.config.v2",
        "source_paths": source_paths,
        "source_path_bindings": bindings,
        "gdd_paths": gdd_paths,
        "task_scene_bindings": task_scene_bindings,
        "query_aliases": normalized_aliases,
        "include_extensions": exts,
        "max_file_bytes": max_file_bytes,
        "max_results": max_results,
    }


def load_config(root: str | Path = ".") -> dict[str, Any]:
    repo = base_dir(root)
    path = repo / CONFIG
    if not path.exists():
        return validate_config(DEFAULT_CONFIG.copy())
    return validate_config(read_json(path))


def save_config(root: str | Path, config: dict[str, Any]) -> dict[str, Any]:
    repo = base_dir(root)
    validated = validate_config(config)
    write_json(repo / CONFIG, validated)
    return validated


def safe_file(root: Path, rel: str) -> Path:
    posix = PurePosixPath(rel.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError("unsafe path")
    candidate = (root / Path(*posix.parts)).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("path escapes repository")
    return candidate


def _configured_paths(config: dict[str, Any]) -> list[str]:
    values = [*config["source_paths"], *config.get("gdd_paths", [])]
    return list(dict.fromkeys(item for item in values if item))


def _iter_source_files(root: Path, config: dict[str, Any]) -> Iterable[Path]:
    exts = set(config["include_extensions"])
    for entry in _configured_paths(config):
        path = safe_file(root, entry)
        if path.is_file():
            if path.suffix.lower() in exts or path.name in {"workflow.md", "AGENTS.md", "README.md", "DELIVERY_PROFILE.md"}:
                yield path
            continue
        if not path.is_dir():
            continue
        for item in path.rglob("*"):
            if not item.is_file() or item.suffix.lower() not in exts:
                continue
            rel_parts = item.relative_to(root).parts
            if any(part in {".git", ".godot", "bin", "obj", "logs"} for part in rel_parts):
                continue
            yield item


def scan(root: str | Path = ".", config: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = base_dir(root)
    cfg = validate_config(config or load_config(repo))
    records: list[dict[str, Any]] = []
    for path in sorted(set(_iter_source_files(repo, cfg)), key=lambda item: item.as_posix().lower()):
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if len(raw) > cfg["max_file_bytes"]:
            continue
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(repo).as_posix()
        records.append({
            "path": rel,
            "kind": path.suffix.lower().lstrip(".") or "text",
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "lines": text.count("\n") + 1,
            "source_binding": next((key for key, value in cfg["source_path_bindings"].items() if rel == value or rel.startswith(value.rstrip("/") + "/")), None),
            "gdd_supplement": any(rel == value or rel.startswith(value.rstrip("/") + "/") for value in cfg["gdd_paths"]),
        })
    payload = {
        "schema": "godot-project-knowledge.scan.v2",
        "revision": revision(repo),
        "config": cfg,
        "records": records,
        "counts": {"files": len(records)},
        "configured_gdd_sources": cfg["gdd_paths"],
    }
    write_json(repo / "logs/ci/project-health-knowledge/latest.json", payload)
    return payload


def latest(root: str | Path = ".") -> dict[str, Any]:
    repo = base_dir(root)
    path = repo / "logs/ci/project-health-knowledge/latest.json"
    if not path.exists():
        return scan(repo)
    return read_json(path)


def _query_terms(config: dict[str, Any], text: str) -> tuple[list[str], list[str]]:
    queries = [text.strip()] if text.strip() else []
    folded = text.casefold()
    for key, aliases in config.get("query_aliases", {}).items():
        if key.casefold() in folded:
            queries.extend(aliases)
    queries = list(dict.fromkeys(query for query in queries if query))
    tokens = [token.lower() for query_text in queries for token in re.findall(r"[\w.-]+", query_text, flags=re.UNICODE) if token.strip()]
    return queries, list(dict.fromkeys(tokens))


def _action_kind(path: str) -> str:
    lowered = path.lower()
    if lowered.startswith(".taskmaster/tasks/"):
        return "tasks"
    if lowered.endswith((".cfg", ".toml", ".json", ".tres")) and not lowered.startswith(".taskmaster/tasks/"):
        return "configuration"
    if "test" in lowered or lowered.startswith("tests.godot/") or lowered.startswith("game.core.tests/"):
        return "tests"
    if lowered.endswith((".cs", ".gd", ".tscn")) or lowered.startswith(("game.core/", "game.godot/")):
        return "code"
    return "secondary"


def query(root: str | Path, text: str, *, limit: int | None = None) -> dict[str, Any]:
    repo = base_dir(root)
    cfg = load_config(repo)
    queries, wanted = _query_terms(cfg, text)
    if not wanted:
        return {"schema": "godot-project-knowledge.query.v2", "query": text, "queries": queries, "results": [], "actionable": {"tasks": [], "configuration": [], "code": [], "tests": [], "secondary": []}}
    cap = min(int(limit or cfg["max_results"]), cfg["max_results"])
    results: list[dict[str, Any]] = []
    for record in latest(repo).get("records", []):
        path = safe_file(repo, str(record["path"]))
        try:
            body = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        haystack = (record["path"] + "\n" + body).lower()
        score = sum(haystack.count(term) for term in wanted)
        if score <= 0:
            continue
        first = min((haystack.find(term) for term in wanted if haystack.find(term) >= 0), default=0)
        line = haystack[:first].count("\n") + 1
        snippet_lines = body.splitlines()[max(0, line - 2): line + 2]
        results.append({
            "path": record["path"],
            "score": score,
            "line": line,
            "snippet": "\n".join(snippet_lines)[:1200],
            "category": _action_kind(str(record["path"])),
            "source_binding": record.get("source_binding"),
            "gdd_supplement": bool(record.get("gdd_supplement")),
        })
    results.sort(key=lambda item: (-item["score"], item["path"]))
    limited = results[:cap]
    actionable = {key: [] for key in ("tasks", "configuration", "code", "tests", "secondary")}
    for item in limited:
        actionable[item["category"]].append(item)
    return {
        "schema": "godot-project-knowledge.query.v2",
        "query": text,
        "queries": queries,
        "revision": revision(repo),
        "results": limited,
        "actionable": actionable,
        "gdd_supplements": [item for item in limited if item.get("gdd_supplement")],
    }


def _walk_tasks(value: Any):
    if isinstance(value, dict):
        if "id" in value and ("title" in value or "status" in value):
            yield value
        for child in value.values():
            yield from _walk_tasks(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_tasks(child)


def task_details(root: str | Path, task_id: str) -> dict[str, Any]:
    repo = base_dir(root)
    needle = str(task_id).strip()
    matches: list[dict[str, Any]] = []
    task_dir = repo / ".taskmaster/tasks"
    if task_dir.exists():
        for path in sorted(task_dir.glob("*.json")):
            try:
                data = read_json(path)
            except Exception:
                continue
            rows = [row for row in _walk_tasks(data) if str(row.get("id") or "").strip() == needle]
            if rows:
                matches.append({"path": path.relative_to(repo).as_posix(), "tasks": rows})
    cfg = load_config(repo)
    scene_bindings = [item for item in cfg.get("task_scene_bindings", []) if str(item.get("task_id", item.get("taskmaster_id", ""))).strip() == needle]
    return {
        "schema": "godot-project-knowledge.task.v2",
        "task_id": needle,
        "initialized": bool(matches),
        "sources": matches,
        "scene_bindings": scene_bindings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan")
    q = sub.add_parser("query"); q.add_argument("text")
    t = sub.add_parser("task"); t.add_argument("--task-id", required=True)
    sub.add_parser("config")
    args = parser.parse_args(argv)
    if args.command == "scan":
        result = scan(args.repo_root)
    elif args.command == "query":
        result = query(args.repo_root, args.text)
    elif args.command == "task":
        result = task_details(args.repo_root, args.task_id)
    else:
        result = load_config(args.repo_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
