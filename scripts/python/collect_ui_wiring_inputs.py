#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


TASKS_JSON = Path(".taskmaster/tasks/tasks.json")
TASKS_BACK = Path(".taskmaster/tasks/tasks_back.json")
TASKS_GAMEPLAY = Path(".taskmaster/tasks/tasks_gameplay.json")
TASK_TRIPLET = [TASKS_JSON, TASKS_BACK, TASKS_GAMEPLAY]
UI_GDD_FLOW = Path("docs/gdd/ui-gdd-flow.md")


def _today() -> str:
    return dt.date.today().strftime("%Y-%m-%d")


def _norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _missing_task_files(repo_root: Path) -> list[str]:
    return [_norm(item) for item in TASK_TRIPLET if not (repo_root / item).is_file()]


def _load_master_tasks(repo_root: Path) -> list[dict[str, Any]]:
    payload = _read_json(repo_root / TASKS_JSON)
    tasks = payload.get("master", {}).get("tasks", []) if isinstance(payload, dict) else []
    return [item for item in tasks if isinstance(item, dict)]


def _load_view_tasks(repo_root: Path, rel: Path) -> list[dict[str, Any]]:
    payload = _read_json(repo_root / rel)
    return [item for item in payload if isinstance(item, dict)] if isinstance(payload, list) else []


def _task_id(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _feature_family(
    task: dict[str, Any],
    gameplay_view: dict[str, Any] | None,
    back_view: dict[str, Any] | None,
) -> str:
    title = (
        str(task.get("title") or "")
        + " "
        + str((gameplay_view or {}).get("title") or "")
        + " "
        + str((back_view or {}).get("title") or "")
    )
    labels = {str(x).lower() for x in ((gameplay_view or {}).get("labels") or [])}
    text = title.lower()
    if "reward" in labels or "reward" in text:
        return "reward"
    if "rest" in labels or "rest" in text or "camp" in text:
        return "rest"
    if "shop" in labels or "shop" in text:
        return "shop"
    if "event" in labels or "event" in text:
        return "event"
    if "combat" in labels or "combat" in text or "battle" in text:
        return "combat"
    if "map" in labels or "map" in text:
        return "map"
    if "menu" in text or "difficulty" in text or "character" in text or "run" in text:
        return "run-entry"
    if "translation" in text or "localization" in text or "i18n" in labels:
        return "text-localization"
    if "hud" in text or "ui" in labels or "screen" in text:
        return "ui-shell"
    return "system-support"


def _merge_refs(*refs_lists: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for refs in refs_lists:
        for item in refs:
            value = str(item).strip()
            if not value or value in seen:
                continue
            seen.add(value)
            merged.append(value)
    return merged


def _by_taskmaster_id(items: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    by_id: dict[int, list[dict[str, Any]]] = {}
    for item in items:
        taskmaster_id = _task_id(item.get("taskmaster_id"))
        if taskmaster_id is not None:
            by_id.setdefault(taskmaster_id, []).append(item)
    return by_id


def _skipped_summary(repo_root: Path, missing: list[str]) -> dict[str, Any]:
    return {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "action": "collect-ui-wiring-inputs",
        "status": "skipped",
        "reason": "missing_task_triplet",
        "repo_root": _norm(repo_root),
        "source_files": [_norm(item) for item in TASK_TRIPLET],
        "missing_source_files": missing,
        "completed_master_tasks_count": 0,
        "needed_wiring_features_count": 0,
        "feature_family_counts": {},
        "missing_gameplay_view_task_ids": [],
        "missing_back_view_task_ids": [],
        "needed_wiring_features": [],
    }


def build_summary(*, repo_root: Path) -> dict[str, Any]:
    missing = _missing_task_files(repo_root)
    if missing:
        return _skipped_summary(repo_root, missing)

    master_tasks = _load_master_tasks(repo_root)
    done_master = [task for task in master_tasks if str(task.get("status") or "").lower() == "done"]
    back_tasks = _load_view_tasks(repo_root, TASKS_BACK)
    gameplay_tasks = _load_view_tasks(repo_root, TASKS_GAMEPLAY)
    back_by_tm = _by_taskmaster_id(back_tasks)
    gameplay_by_tm = _by_taskmaster_id(gameplay_tasks)

    needed: list[dict[str, Any]] = []
    missing_gameplay: list[int] = []
    missing_back: list[int] = []
    for task in done_master:
        task_id = _task_id(task.get("id"))
        if task_id is None:
            continue
        gameplay_views = gameplay_by_tm.get(task_id, [])
        back_views = back_by_tm.get(task_id, [])
        if not gameplay_views:
            missing_gameplay.append(task_id)
        if not back_views:
            missing_back.append(task_id)
        gameplay_view = gameplay_views[0] if gameplay_views else None
        back_view = back_views[0] if back_views else None
        merged_view_rows = [*gameplay_views, *back_views]
        needed.append(
            {
                "task_id": task_id,
                "task_ref": f"T{task_id}",
                "task_title": str(task.get("title") or ""),
                "feature_family": _feature_family(task, gameplay_view, back_view),
                "gameplay_view_ids": [
                    str(item.get("id") or "") for item in gameplay_views if str(item.get("id") or "").strip()
                ],
                "back_view_ids": [str(item.get("id") or "") for item in back_views if str(item.get("id") or "").strip()],
                "status_master": str(task.get("status") or ""),
                "status_views": sorted(
                    {str(item.get("status") or "") for item in merged_view_rows if str(item.get("status") or "").strip()}
                ),
                "labels": sorted({str(x).lower() for item in gameplay_views for x in (item.get("labels") or [])}),
                "test_refs": _merge_refs(*[item.get("test_refs") or [] for item in merged_view_rows]),
                "acceptance": _merge_refs(*[item.get("acceptance") or [] for item in merged_view_rows]),
                "contract_refs": _merge_refs(*[item.get("contractRefs") or [] for item in merged_view_rows]),
            }
        )

    families: dict[str, int] = {}
    for item in needed:
        families[item["feature_family"]] = families.get(item["feature_family"], 0) + 1

    return {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
        "action": "collect-ui-wiring-inputs",
        "status": "ok",
        "repo_root": _norm(repo_root),
        "source_files": [_norm(item) for item in TASK_TRIPLET],
        "missing_source_files": [],
        "completed_master_tasks_count": len(done_master),
        "needed_wiring_features_count": len(needed),
        "feature_family_counts": families,
        "missing_gameplay_view_task_ids": sorted(missing_gameplay),
        "missing_back_view_task_ids": sorted(missing_back),
        "needed_wiring_features": needed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect completed task triplet inputs for Chapter 7 UI wiring flow.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    payload = build_summary(repo_root=repo_root)
    out = Path(args.out) if args.out else (repo_root / "logs" / "ci" / _today() / "chapter7-ui-wiring-inputs" / "summary.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "CHAPTER7_UI_WIRING_INPUTS "
        f"status={payload['status']} tasks={payload['needed_wiring_features_count']} out={_norm(out)}"
    )
    if payload["status"] == "skipped":
        print(f" - reason={payload['reason']} missing_source_files={payload['missing_source_files']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
