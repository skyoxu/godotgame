#!/usr/bin/env python3
"""Template-safe local knowledge/impact service helpers.

This module intentionally derives all data from the current repository. It does not
ship business task data and degrades to empty results when a template has not been
initialized yet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

CONFIG = "scripts/python/project_health_knowledge_config.json"
DEFAULT_CONFIG: dict[str, Any] = {
    "schema": "godot-project-knowledge.config.v1",
    "source_paths": [
        ".taskmaster/tasks",
        "docs/prd",
        "docs/adr",
        "docs/architecture",
        "docs/knowledge",
        "Game.Core",
        "Game.Godot",
        "Tests.Godot",
        "scripts/python",
        "workflow.md",
        "AGENTS.md",
    ],
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
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def revision(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD") or "workspace"


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ValueError("config must be an object")
    source_paths = config.get("source_paths", DEFAULT_CONFIG["source_paths"])
    exts = config.get("include_extensions", DEFAULT_CONFIG["include_extensions"])
    if not isinstance(source_paths, list) or not all(isinstance(x, str) and x.strip() for x in source_paths):
        raise ValueError("source_paths must be non-empty strings")
    if not isinstance(exts, list) or not all(isinstance(x, str) and x.startswith(".") for x in exts):
        raise ValueError("include_extensions must contain extensions")
    max_file_bytes = int(config.get("max_file_bytes", DEFAULT_CONFIG["max_file_bytes"]))
    max_results = int(config.get("max_results", DEFAULT_CONFIG["max_results"]))
    if not 1024 <= max_file_bytes <= 5_000_000:
        raise ValueError("max_file_bytes out of range")
    if not 1 <= max_results <= 200:
        raise ValueError("max_results out of range")
    return {
        "schema": "godot-project-knowledge.config.v1",
        "source_paths": source_paths,
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


def _iter_source_files(root: Path, config: dict[str, Any]) -> Iterable[Path]:
    exts = set(config["include_extensions"])
    for entry in config["source_paths"]:
        path = safe_file(root, entry)
        if path.is_file():
            if path.suffix.lower() in exts or path.name in {"workflow.md", "AGENTS.md"}:
                yield path
            continue
        if not path.is_dir():
            continue
        for item in path.rglob("*"):
            if not item.is_file() or item.suffix.lower() not in exts:
                continue
            rel_parts = item.relative_to(root).parts
            if any(p in {".git", ".godot", "bin", "obj", "logs"} for p in rel_parts):
                continue
            yield item


def scan(root: str | Path = ".", config: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = base_dir(root)
    cfg = validate_config(config or load_config(repo))
    records: list[dict[str, Any]] = []
    for path in sorted(set(_iter_source_files(repo, cfg)), key=lambda p: p.as_posix().lower()):
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
        })
    payload = {
        "schema": "godot-project-knowledge.scan.v1",
        "revision": revision(repo),
        "config": cfg,
        "records": records,
        "counts": {"files": len(records)},
    }
    out = repo / "logs/ci/project-health-knowledge/latest.json"
    write_json(out, payload)
    return payload


def latest(root: str | Path = ".") -> dict[str, Any]:
    repo = base_dir(root)
    path = repo / "logs/ci/project-health-knowledge/latest.json"
    if not path.exists():
        return scan(repo)
    return read_json(path)


def query(root: str | Path, text: str, *, limit: int | None = None) -> dict[str, Any]:
    repo = base_dir(root)
    cfg = load_config(repo)
    wanted = [token.lower() for token in re.findall(r"[\w.-]+", text, flags=re.UNICODE) if token.strip()]
    if not wanted:
        return {"schema": "godot-project-knowledge.query.v1", "query": text, "results": []}
    cap = min(int(limit or cfg["max_results"]), cfg["max_results"])
    results: list[dict[str, Any]] = []
    for record in latest(repo).get("records", []):
        path = safe_file(repo, str(record["path"]))
        try:
            body = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        haystack = (record["path"] + "\n" + body).lower()
        score = sum(haystack.count(t) for t in wanted)
        if score <= 0:
            continue
        first = min((haystack.find(t) for t in wanted if haystack.find(t) >= 0), default=0)
        line = haystack[:first].count("\n") + 1
        snippet_lines = body.splitlines()[max(0, line - 2): line + 2]
        results.append({"path": record["path"], "score": score, "line": line, "snippet": "\n".join(snippet_lines)[:1200]})
    results.sort(key=lambda x: (-x["score"], x["path"]))
    return {"schema": "godot-project-knowledge.query.v1", "query": text, "revision": revision(repo), "results": results[:cap]}


def task_details(root: str | Path, task_id: str) -> dict[str, Any]:
    repo = base_dir(root)
    candidates = [
        repo / ".taskmaster/tasks/tasks.json",
        repo / ".taskmaster/tasks/tasks_game.json",
        repo / ".taskmaster/tasks/tasks_prd.json",
    ]
    matches: list[dict[str, Any]] = []
    needle = str(task_id).strip().lower()
    for path in candidates:
        if not path.exists():
            continue
        try:
            data = read_json(path)
        except Exception:
            continue
        blob = json.dumps(data, ensure_ascii=False)
        if needle and needle in blob.lower():
            matches.append({"path": path.relative_to(repo).as_posix(), "contains": True})
    return {"schema": "godot-project-knowledge.task.v1", "task_id": task_id, "initialized": bool(matches), "sources": matches}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("scan")
    q = sub.add_parser("query"); q.add_argument("text")
    t = sub.add_parser("task"); t.add_argument("--task-id", required=True)
    c = sub.add_parser("config"); c.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "scan": result = scan(args.repo_root)
    elif args.command == "query": result = query(args.repo_root, args.text)
    elif args.command == "task": result = task_details(args.repo_root, args.task_id)
    else: result = load_config(args.repo_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
