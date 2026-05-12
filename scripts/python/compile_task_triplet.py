#!/usr/bin/env python3
"""Compile task candidates into Taskmaster triplet view files.

Default mode writes a patch preview only. Use --write to update tasks_back.json or
tasks_gameplay.json, then run build_taskmaster_tasks.py and Chapter 3.3 validators.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASKS_DIR = Path(".taskmaster/tasks")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def iter_task_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        master = payload.get("master")
        if isinstance(master, dict):
            tasks = master.get("tasks")
            if isinstance(tasks, list):
                return [item for item in tasks if isinstance(item, dict)]
    return []


def existing_task_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    for name in ("tasks_back.json", "tasks_gameplay.json", "tasks.json"):
        for task in iter_task_records(load_json(root / TASKS_DIR / name, [])):
            value = task.get("id")
            if value is not None:
                ids.add(str(value))
    return ids


def split_task_number(task_id: str) -> tuple[str, int] | None:
    head, sep, tail = task_id.rpartition("-")
    if not sep or not tail.isdigit():
        return None
    return head, int(tail)


def dominant_id_prefix(candidates: list[dict[str, Any]]) -> str:
    for candidate in candidates:
        parsed = split_task_number(str(candidate.get("id") or ""))
        if parsed:
            return parsed[0]
    return "GEN"


def max_task_number(ids: set[str], prefix: str) -> int:
    max_seen = 0
    for tid in ids:
        parsed = split_task_number(tid)
        if parsed and parsed[0] == prefix:
            max_seen = max(max_seen, parsed[1])
    return max_seen


def renumber_candidates_for_add(candidates: list[dict[str, Any]], existing_ids: set[str]) -> list[dict[str, Any]]:
    prefix = dominant_id_prefix(candidates)
    next_number = max_task_number(existing_ids, prefix) + 1
    used = set(existing_ids)
    remap: dict[str, str] = {}
    renumbered: list[dict[str, Any]] = []
    for candidate in candidates:
        old_id = str(candidate.get("id") or "")
        new_id = f"{prefix}-{next_number:04d}"
        while new_id in used:
            next_number += 1
            new_id = f"{prefix}-{next_number:04d}"
        updated = dict(candidate)
        updated["id"] = new_id
        updated["previous_candidate_id"] = old_id
        used.add(new_id)
        remap[old_id] = new_id
        renumbered.append(updated)
        next_number += 1
    for candidate in renumbered:
        candidate["depends_on"] = [remap.get(str(dep), str(dep)) for dep in candidate.get("depends_on", [])]
    return renumbered


def assert_no_candidate_conflicts(
    candidates: list[dict[str, Any]], existing_ids: set[str] | None = None, *, check_existing: bool = False
) -> None:
    existing = existing_ids or set()
    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    conflicting_ids: set[str] = set()
    for candidate in candidates:
        tid = str(candidate.get("id") or "")
        if not tid:
            continue
        if tid in seen:
            duplicate_ids.add(tid)
        if check_existing and tid in existing:
            conflicting_ids.add(tid)
        seen.add(tid)
    if duplicate_ids or conflicting_ids:
        detail = {
            "duplicate_candidate_ids": sorted(duplicate_ids),
            "conflicting_existing_task_ids": sorted(conflicting_ids),
        }
        raise SystemExit("candidate id conflict before triplet write: " + json.dumps(detail, ensure_ascii=False))


def normalize_task(candidate: dict[str, Any], target: str) -> dict[str, Any]:
    task = {
        "id": str(candidate.get("id")),
        "story_id": str(candidate.get("story_id") or "TASK-GENERATION"),
        "title": str(candidate.get("title") or candidate.get("id")),
        "description": str(candidate.get("description") or ""),
        "status": str(candidate.get("status") or "pending"),
        "priority": str(candidate.get("priority") or "P2"),
        "layer": str(candidate.get("layer") or "feature"),
        "depends_on": list(candidate.get("depends_on") or []),
        "adr_refs": list(candidate.get("adr_refs") or []),
        "chapter_refs": list(candidate.get("chapter_refs") or []),
        "overlay_refs": list(candidate.get("overlay_refs") or []),
        "labels": sorted(set(list(candidate.get("labels") or []) + [target, "generated"])),
        "owner": str(candidate.get("owner") or ("gameplay" if target == "gameplay" else "architecture")),
        "test_refs": list(candidate.get("test_refs") or []),
        "acceptance": list(candidate.get("acceptance") or []),
        "test_strategy": list(candidate.get("test_strategy") or []),
        "contractRefs": list(candidate.get("contractRefs") or []),
        "evidence_refs": list(candidate.get("evidence_refs") or []),
        "source_refs": list(candidate.get("source_refs") or []),
        "requirement_ids": list(candidate.get("requirement_ids") or []),
        "taskmaster_exported": False,
        "semantic_review_tier": "targeted",
    }
    return task


def target_for(candidate: dict[str, Any]) -> str:
    owner = str(candidate.get("owner", "")).lower()
    labels = {str(x).lower() for x in candidate.get("labels", [])}
    if owner == "gameplay" or "gdd" in labels or "gameplay" in labels:
        return "gameplay"
    return "back"


def append_unique(existing: list[dict[str, Any]], new_tasks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    by_id = {str(t.get("id")): t for t in existing}
    added: list[str] = []
    for task in new_tasks:
        tid = str(task.get("id"))
        if tid in by_id:
            by_id[tid].update(task)
        else:
            existing.append(task)
            added.append(tid)
    return existing, added


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile task candidates into task triplet view files.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--candidates", default="logs/ci/task-generation/task-candidates.enriched.json")
    parser.add_argument("--coverage", default="logs/ci/task-generation/coverage-report.json")
    parser.add_argument("--mode", choices=["init", "add"], default="add")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default="logs/ci/task-generation/task-triplet.patch.json")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    candidates = load_json(root / args.candidates, {}).get("candidates", [])
    coverage = load_json(root / args.coverage, {"status": "unknown"})
    if coverage.get("status") != "ok":
        raise SystemExit("coverage report is not ok; refusing to compile triplet")
    ids = existing_task_ids(root)
    if args.mode == "add":
        candidates = renumber_candidates_for_add(candidates, ids)
    assert_no_candidate_conflicts(candidates, ids, check_existing=args.mode == "add")
    back_new: list[dict[str, Any]] = []
    gameplay_new: list[dict[str, Any]] = []
    for candidate in candidates:
        target = target_for(candidate)
        if target == "gameplay":
            gameplay_new.append(normalize_task(candidate, "gameplay"))
        else:
            back_new.append(normalize_task(candidate, "back"))
    patch = {
        "schema": "task-generation.triplet-patch.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": args.mode,
        "write": args.write,
        "tasks_back_add_or_update": back_new,
        "tasks_gameplay_add_or_update": gameplay_new,
        "next_commands": [
            "py -3 scripts/python/build_taskmaster_tasks.py --tasks-file .taskmaster/tasks/tasks_back.json --tasks-file .taskmaster/tasks/tasks_gameplay.json",
            "py -3 scripts/python/task_links_validate.py",
            "py -3 scripts/python/check_tasks_all_refs.py",
            "py -3 scripts/python/validate_task_master_triplet.py",
            "py -3 scripts/python/backfill_semantic_review_tier.py --mode conservative --write",
            "py -3 scripts/python/validate_semantic_review_tier.py --mode conservative",
        ],
    }
    out = root / args.out
    write_json(out, patch)
    if args.write:
        tasks_dir = root / TASKS_DIR
        back_path = tasks_dir / "tasks_back.json"
        gameplay_path = tasks_dir / "tasks_gameplay.json"
        back_existing = load_json(back_path, [])
        gameplay_existing = load_json(gameplay_path, [])
        if not isinstance(back_existing, list) or not isinstance(gameplay_existing, list):
            raise SystemExit("task view files must be JSON lists")
        assert_no_candidate_conflicts(back_new + gameplay_new, existing_task_ids(root), check_existing=args.mode == "add")
        back_updated, back_added = append_unique(back_existing, back_new)
        gameplay_updated, gameplay_added = append_unique(gameplay_existing, gameplay_new)
        write_json(back_path, back_updated)
        write_json(gameplay_path, gameplay_updated)
        print(f"wrote back={len(back_added)} gameplay={len(gameplay_added)}")
    print(f"triplet_patch={out} back_candidates={len(back_new)} gameplay_candidates={len(gameplay_new)} write={args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

