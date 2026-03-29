#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge split workflow 5.1 summaries into one transparent merged report."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _today() -> str:
    return dt.date.today().strftime("%Y-%m-%d")


def _default_logs_root(root: Path, date_str: str) -> Path:
    return root / "logs" / "ci" / date_str


def _default_out_dir(root: Path, date_str: str) -> Path:
    return _default_logs_root(root, date_str) / "single-task-light-lane-v2-merged"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _summary_declared_task_ids(summary: dict[str, Any]) -> list[int]:
    resume_scope = summary.get("resume_scope")
    if isinstance(resume_scope, dict):
        task_ids = []
        for item in resume_scope.get("task_ids") or []:
            raw = str(item).strip()
            if raw.isdigit():
                task_ids.append(int(raw))
        if task_ids:
            return sorted(set(task_ids))
    start = summary.get("task_id_start")
    end = summary.get("task_id_end")
    if start is not None and end is not None:
        try:
            start_i = int(start)
            end_i = int(end)
        except Exception:
            return []
        if start_i <= end_i:
            return list(range(start_i, end_i + 1))
    return []


def _discover_inputs(logs_root: Path, pattern: str) -> list[Path]:
    out: list[Path] = []
    for path in sorted(logs_root.glob(pattern)):
        summary_path = path / "summary.json" if path.is_dir() else path
        if not summary_path.is_file():
            continue
        if "-merged" in summary_path.as_posix():
            continue
        out.append(summary_path)
    return out


def _source_meta(root: Path, summary_path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    declared = _summary_declared_task_ids(summary)
    result_ids = []
    for row in summary.get("results", []) or []:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("task_id") or "").strip()
        if raw.isdigit():
            result_ids.append(int(raw))
    return {
        "path": str(summary_path.relative_to(root)).replace("\\", "/"),
        "status": summary.get("status"),
        "generated_at": summary.get("finished_at") or summary.get("last_updated_at") or summary.get("started_at"),
        "task_id_start": summary.get("task_id_start"),
        "task_id_end": summary.get("task_id_end"),
        "declared_task_count": len(declared),
        "result_task_count": len(set(result_ids)),
        "processed_tasks": summary.get("processed_tasks"),
        "passed_tasks": summary.get("passed_tasks"),
        "failed_tasks": summary.get("failed_tasks"),
        "delivery_profile": summary.get("delivery_profile"),
        "fill_refs_mode_resolved": summary.get("fill_refs_mode_resolved"),
        "downstream_on_extract_fail_resolved": summary.get("downstream_on_extract_fail_resolved"),
        "batch_lane_resolved": summary.get("batch_lane_resolved"),
    }


def _row_sort_key(summary_path: Path, row: dict[str, Any]) -> tuple[float, int]:
    try:
        mtime = summary_path.stat().st_mtime
    except Exception:
        mtime = 0.0
    task_raw = str(row.get("task_id") or "").strip()
    task_id = int(task_raw) if task_raw.isdigit() else 0
    return (mtime, task_id)


def merge_summaries(root: Path, input_paths: list[Path]) -> dict[str, Any]:
    source_entries: list[dict[str, Any]] = []
    all_declared_ids: set[int] = set()
    chosen_rows: dict[int, dict[str, Any]] = {}
    chosen_sources: dict[int, str] = {}
    candidate_sources: dict[int, list[str]] = {}

    for summary_path in input_paths:
        summary = _load_json(summary_path)
        if not isinstance(summary, dict):
            continue
        source_entries.append(_source_meta(root, summary_path, summary))
        declared_ids = _summary_declared_task_ids(summary)
        all_declared_ids.update(declared_ids)
        source_rel = str(summary_path.relative_to(root)).replace("\\", "/")
        for row in summary.get("results", []) or []:
            if not isinstance(row, dict):
                continue
            raw = str(row.get("task_id") or "").strip()
            if not raw.isdigit():
                continue
            task_id = int(raw)
            candidate_sources.setdefault(task_id, []).append(source_rel)
            current = chosen_rows.get(task_id)
            if current is None:
                chosen_rows[task_id] = dict(row)
                chosen_sources[task_id] = source_rel
                continue
            current_source = root / chosen_sources[task_id]
            if _row_sort_key(summary_path, row) >= _row_sort_key(current_source, current):
                chosen_rows[task_id] = dict(row)
                chosen_sources[task_id] = source_rel

    covered_ids = sorted(chosen_rows.keys())
    missing_ids = sorted(all_declared_ids.difference(set(covered_ids)))
    passed_ids: list[int] = []
    failed_ids: list[int] = []
    failed_first_step_counter: dict[str, int] = {"extract": 0, "align": 0, "coverage": 0, "semantic_gate": 0, "other": 0}

    results: list[dict[str, Any]] = []
    for task_id in covered_ids:
        row = dict(chosen_rows[task_id])
        row["merged_source"] = chosen_sources.get(task_id, "")
        row["merged_source_candidates"] = list(candidate_sources.get(task_id) or [])
        results.append(row)
        if bool(row.get("ok")):
            passed_ids.append(task_id)
        else:
            failed_ids.append(task_id)
            first_failed = str(row.get("first_failed_step") or "").strip()
            bucket = first_failed if first_failed in {"extract", "align", "coverage", "semantic_gate"} else "other"
            failed_first_step_counter[bucket] = failed_first_step_counter.get(bucket, 0) + 1

    overridden_task_ids = sorted(task_id for task_id, sources in candidate_sources.items() if len(set(sources)) > 1)
    merged = {
        "cmd": "merge-single-task-light-lane-summaries",
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "range": {
            "task_id_start": min(all_declared_ids) if all_declared_ids else None,
            "task_id_end": max(all_declared_ids) if all_declared_ids else None,
        },
        "source_summaries": source_entries,
        "task_source_map": {str(task_id): chosen_sources.get(task_id, "") for task_id in covered_ids},
        "task_source_candidates": {str(task_id): list(candidate_sources.get(task_id) or []) for task_id in sorted(candidate_sources)},
        "overridden_task_ids": overridden_task_ids,
        "covered_count": len(covered_ids),
        "missing_count": len(missing_ids),
        "missing_task_ids": missing_ids,
        "passed_count": len(passed_ids),
        "failed_count": len(failed_ids),
        "passed_task_ids": passed_ids,
        "failed_task_ids": failed_ids,
        "failed_first_step_counter": failed_first_step_counter,
        "results": results,
    }
    return merged


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge split workflow 5.1 summaries into one transparent summary.")
    parser.add_argument("--date", default=_today(), help="Logs date folder under logs/ci/YYYY-MM-DD")
    parser.add_argument("--logs-root", default="", help="Override logs root. Default: logs/ci/<date>")
    parser.add_argument(
        "--pattern",
        default="single-task-light-lane-v2*/summary.json",
        help="Glob pattern under logs root. Merged summaries are ignored automatically.",
    )
    parser.add_argument("--input", action="append", default=[], help="Explicit summary.json path(s). Can be passed multiple times.")
    parser.add_argument("--out-dir", default="", help="Output directory. Default: logs/ci/<date>/single-task-light-lane-v2-merged")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = _repo_root()
    logs_root = Path(args.logs_root) if str(args.logs_root).strip() else _default_logs_root(root, str(args.date))
    input_paths = [Path(item) for item in list(args.input or []) if str(item).strip()]
    if not input_paths:
        input_paths = _discover_inputs(logs_root, str(args.pattern))
    input_paths = [path for path in input_paths if path.is_file()]
    if not input_paths:
        print("MERGE_SINGLE_TASK_LIGHT_LANE status=fail reason=no_inputs")
        return 2

    out_dir = Path(args.out_dir) if str(args.out_dir).strip() else _default_out_dir(root, str(args.date))
    out_dir.mkdir(parents=True, exist_ok=True)
    merged = merge_summaries(root, input_paths)
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "MERGE_SINGLE_TASK_LIGHT_LANE "
        f"status=ok sources={len(input_paths)} covered={merged.get('covered_count', 0)} "
        f"missing={merged.get('missing_count', 0)} out={str(summary_path).replace('\\', '/')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
