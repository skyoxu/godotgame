#!/usr/bin/env python3
"""Generate task-to-resource knowledge links from the latest Project Health snapshot.

The generator is template-safe: every association must be reconstructed from the
current repository snapshot and task evidence. It does not ship sibling-project
identities or infer business authority from filenames.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_health_godot import build_navigation
from project_health_knowledge import latest, load_config, read_json, task_rows, write_json


def _task_test_refs(row: dict[str, Any]) -> list[str]:
    task = row.get("task") if isinstance(row.get("task"), dict) else {}
    refs: list[str] = []
    for key in ("test_refs", "testRefs", "tests"):
        value = task.get(key)
        if isinstance(value, list):
            refs.extend(str(item) for item in value if isinstance(item, str) and item.strip())
    return sorted(set(refs))


def _entry_kind(group: str) -> str:
    return {"configs": "config", "assets": "asset", "scenes": "scene", "code": "code"}[group]


def _confidence(resource: dict[str, Any]) -> str:
    if resource.get("focus") == "core":
        return "confirmed"
    if resource.get("readers") or resource.get("nodes") or resource.get("users"):
        return "confirmed"
    return "inferred"


def _role(path: str, kind: str) -> str:
    suffix = Path(path).suffix.casefold()
    if kind == "config":
        return f"Configuration resource ({suffix or 'text'})"
    return {
        "asset": "Runtime asset",
        "scene": "Godot scene",
        "code": "Implementation code",
    }.get(kind, "Related resource")


def _read_previous(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"generated": []}
    try:
        value = read_json(path)
    except (OSError, json.JSONDecodeError):
        return {"generated": []}
    return value if isinstance(value, dict) else {"generated": []}


def _write_task_refs(root: Path, selected: set[str], by_task: dict[str, list[str]], revision: str | None) -> int:
    path = root / ".taskmaster/tasks/tasks_gameplay.json"
    if not path.is_file():
        return 0
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return 0
    if not isinstance(rows, list):
        return 0
    updated = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        task_id = str(row.get("taskmaster_id", row.get("id", ""))).strip()
        if task_id not in selected:
            continue
        row["knowledge_entry_ids"] = sorted(set(by_task.get(task_id, [])))
        row["knowledge_scan_revision"] = revision
        updated += 1
    if updated:
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return updated


def generate(root: Path, task_ids: set[str] | None = None, write_task_refs: bool = False) -> dict[str, Any]:
    root = root.resolve()
    state = latest(root)
    rows = task_rows(root, state)
    available = {str(row.get("id")) for row in rows}
    selected = {str(value) for value in (task_ids or set()) if str(value).strip()}
    if selected and not selected <= available:
        missing = sorted(selected - available)
        raise ValueError("selected task is absent from the scanned snapshot: " + ", ".join(missing))

    config = state.get("config") if isinstance(state.get("config"), dict) else load_config(root)
    bindings = config.get("task_scene_bindings", [])
    entries: list[dict[str, Any]] = []
    by_task: dict[str, list[str]] = {}

    for row in rows:
        task_id = str(row.get("id"))
        if selected and task_id not in selected:
            continue
        task = row.get("task") if isinstance(row.get("task"), dict) else {}
        navigation = build_navigation(
            root,
            task_id,
            task=task,
            mappings=row.get("mappings"),
            bindings=bindings,
            state=state,
        )
        title = str(row.get("title") or task.get("title") or "")
        test_refs = _task_test_refs(row)
        for group in ("configs", "assets", "scenes", "code"):
            for resource in navigation.get(group, []):
                if not isinstance(resource, dict) or not resource.get("path"):
                    continue
                kind = _entry_kind(group)
                path = str(resource["path"])
                entry_id = f"{kind}:{task_id}:{path}"
                parameters = resource.get("confirmed_fields") or resource.get("fields", []) if kind == "config" else []
                entry = {
                    "id": entry_id,
                    "task_id": task_id,
                    "task_title": title,
                    "path": path,
                    "kind": kind,
                    "role": _role(path, kind),
                    "semantic_role": f"{kind} association for {title or ('task ' + task_id)}",
                    "parameters": parameters if isinstance(parameters, list) else [],
                    "readers": resource.get("readers", []) if isinstance(resource.get("readers"), list) else [],
                    "bindings": (resource.get("nodes") or resource.get("users") or []) if kind in {"scene", "asset"} else [],
                    "confidence": _confidence(resource),
                    "reconstruction": "static_repository_evidence",
                    "test_refs": test_refs,
                    "source_revision": state.get("revision"),
                    "evidence": [{
                        "path": path,
                        "focus": resource.get("focus"),
                        "evidence_kind": resource.get("evidence_kind"),
                        "chain": resource.get("chain", []),
                    }],
                }
                entries.append(entry)
                by_task.setdefault(task_id, []).append(entry_id)

    out = root / "docs/knowledge/generated/task-resource-links.json"
    previous = _read_previous(out)
    if selected:
        retained = [
            item for item in previous.get("generated", [])
            if isinstance(item, dict) and str(item.get("task_id")) not in selected
        ]
        entries = retained + entries
    revisions = {entry.get("source_revision") for entry in entries}
    payload = {
        "schema": "godot-project-knowledge.task-resource-links.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_revision": state.get("revision") if len(revisions) <= 1 else None,
        "task_ids": sorted({str(entry.get("task_id")) for entry in entries if entry.get("task_id")}),
        "generated": entries,
    }
    write_json(out, payload)

    updated = _write_task_refs(root, selected or set(by_task), by_task, state.get("revision")) if write_task_refs else 0
    return {
        "status": "ok",
        "entries": len(entries),
        "updated_tasks": updated,
        "path": out.relative_to(root).as_posix(),
        "source_revision": state.get("revision"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--write-task-refs", action="store_true")
    args = parser.parse_args(argv)
    result = generate(args.repo_root.resolve(), set(args.task_ids or []), args.write_task_refs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
