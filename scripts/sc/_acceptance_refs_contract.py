#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Any


SUMMARY_SCHEMA_VERSION = "acceptance-refs.v1"


def validate_anchor_bound_ref_updates(
    *,
    root: Path,
    updates: list[dict[str, Any]],
    read_text=None,
) -> tuple[bool, list[str]]:
    """Validate that refs written by the LLM bind to concrete acceptance anchors."""

    errors: list[str] = []
    reader = read_text or (lambda path: Path(path).read_text(encoding="utf-8", errors="ignore"))
    for update in updates:
        if not isinstance(update, dict):
            errors.append("update_not_object")
            continue
        task_id = str(update.get("task_id") or "").strip()
        view = str(update.get("view") or "").strip() or "unknown"
        index = update.get("index")
        anchor = str(update.get("anchor") or "").strip()
        paths = update.get("paths")
        if not anchor:
            errors.append(f"missing_anchor:{view}[{index}]")
            continue
        if not isinstance(paths, list) or not paths:
            errors.append(f"missing_paths:{view}[{index}]:{anchor}")
            continue
        for raw_path in paths:
            rel = str(raw_path or "").strip().replace("\\", "/")
            if not rel:
                errors.append(f"empty_path:{view}[{index}]:{anchor}")
                continue
            path = root / rel
            if not path.exists() and read_text is None:
                errors.append(f"missing_ref_file:{view}[{index}]:{anchor}:{rel}")
                continue
            try:
                content = str(reader(path))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"read_ref_file_failed:{view}[{index}]:{anchor}:{rel}:{exc}")
                continue
            if anchor not in content:
                errors.append(f"missing_anchor:{view}[{index}]:{anchor}:{rel}")
        if task_id and anchor and not anchor.startswith(f"ACC:T{task_id}."):
            errors.append(f"anchor_task_mismatch:{view}[{index}]:{anchor}:task-{task_id}")
    return not errors, errors


def validate_fill_acceptance_summary(summary: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any]]:
    errors: list[str] = []
    obj = dict(summary or {})
    obj["schema_version"] = SUMMARY_SCHEMA_VERSION

    required = {
        "cmd": str,
        "date": str,
        "write": bool,
        "overwrite_existing": bool,
        "rewrite_placeholders": bool,
        "tasks": int,
        "any_updates": int,
        "results": list,
        "missing_after_write": int,
        "out_dir": str,
        "status": str,
        "consensus_runs": int,
        "prd_source": str,
    }
    for key, typ in required.items():
        if key not in obj:
            errors.append(f"missing:{key}")
            continue
        if not isinstance(obj.get(key), typ):
            errors.append(f"type:{key}")

    status = str(obj.get("status") or "").strip()
    if status not in {"ok", "fail"}:
        errors.append("status_invalid")

    results = obj.get("results")
    if isinstance(results, list):
        for idx, item in enumerate(results, start=1):
            if not isinstance(item, dict):
                errors.append(f"result_not_object:{idx}")
                continue
            if not isinstance(item.get("task_id"), int):
                errors.append(f"result_task_id_type:{idx}")
            item_status = str(item.get("status") or "").strip()
            if item_status not in {"ok", "fail", "skipped"}:
                errors.append(f"result_status_invalid:{idx}")
    else:
        errors.append("results_not_list")
    return not errors, errors, obj


def run_fill_acceptance_refs_self_check(
    *,
    is_allowed_test_path,
    parse_model_items_to_paths,
    validate_summary=validate_fill_acceptance_summary,
) -> tuple[bool, dict[str, Any], str]:
    checks: list[dict[str, Any]] = []

    checks.append({"name": "allowed_path_cs", "ok": bool(is_allowed_test_path("Game.Core.Tests/Domain/FooTests.cs"))})
    checks.append({"name": "reject_docs_path", "ok": not bool(is_allowed_test_path("docs/spec.md"))})

    parsed = parse_model_items_to_paths(
        items=[{"view": "back", "index": 0, "paths": ["Game.Core.Tests/Domain/FooTests.cs"]}],
        max_refs_per_item=2,
    )
    checks.append({"name": "parse_model_items", "ok": bool(parsed.get("back", {}).get(0))})

    summary = {
        "cmd": "sc-llm-fill-acceptance-refs",
        "date": "2026-02-24",
        "write": False,
        "overwrite_existing": False,
        "rewrite_placeholders": False,
        "tasks": 1,
        "any_updates": 0,
        "results": [{"task_id": 1, "status": "ok"}],
        "missing_after_write": 0,
        "out_dir": "logs/ci/2026-02-24/sc-llm-acceptance-refs",
        "status": "ok",
        "consensus_runs": 1,
        "prd_source": ".taskmaster/docs/prd.txt",
    }
    summary_ok, summary_errors, checked = validate_summary(summary)
    checks.append({"name": "summary_contract", "ok": bool(summary_ok), "errors": summary_errors})

    ok = all(bool(item.get("ok")) for item in checks)
    payload = {
        "cmd": "sc-llm-fill-acceptance-refs-self-check",
        "status": "ok" if ok else "fail",
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "checks": checks,
        "summary_schema_version": checked.get("schema_version"),
    }
    report_lines = [
        "# sc-llm-fill-acceptance-refs self-check",
        "",
        f"- status: {payload['status']}",
        f"- schema_version: {payload['schema_version']}",
        "",
        "## Checks",
    ]
    report_lines.extend([f"- {item.get('name')}: {'ok' if item.get('ok') else 'fail'}" for item in checks])
    return ok, payload, "\n".join(report_lines) + "\n"
