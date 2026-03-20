from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _repair_approval import apply_approval_to_recommendations
from _repair_context import build_execution_context
from _repair_markdown import render_repair_guide_markdown
from _repair_recommendations import (
    build_runtime_recommendations,
    build_step_recommendations,
    extend_with_runtime_recommendations,
)


def _load_marathon_state(out_dir: Path) -> dict[str, Any] | None:
    state_path = out_dir / "marathon-state.json"
    if not state_path.exists():
        return None
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def build_repair_guide(
    summary: dict[str, Any],
    *,
    task_id: str,
    out_dir: Path,
    marathon_state: dict[str, Any] | None = None,
    approval_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime_state = marathon_state if isinstance(marathon_state, dict) else _load_marathon_state(out_dir)
    failed_step = next((step for step in summary.get("steps", []) if step.get("status") == "fail"), None)
    if not isinstance(failed_step, dict):
        recommendations = build_runtime_recommendations(task_id=task_id, out_dir=out_dir, runtime_state=runtime_state)
        recommendations, resolved_approval = apply_approval_to_recommendations(
            task_id=task_id,
            out_dir=out_dir,
            recommendations=recommendations,
            approval_state=approval_state,
        )
        return {
            "schema_version": "1.0.0",
            "status": "needs-fix" if recommendations else "not-needed",
            "task_id": task_id,
            "summary_status": str(summary.get("status") or "ok"),
            "failed_step": "",
            "approval": resolved_approval,
            "recommendations": recommendations,
            "generated_from": {"summary_json": str(out_dir / "summary.json")},
        }

    log_path = Path(str(failed_step.get("log") or ""))
    log_text = ""
    if log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            log_text = ""
    step_name = str(failed_step.get("name") or "")
    recommendations = build_step_recommendations(task_id=task_id, step_name=step_name, step=failed_step, log_text=log_text)
    recommendations = extend_with_runtime_recommendations(
        task_id=task_id,
        step=failed_step,
        runtime_state=runtime_state,
        recommendations=recommendations,
    )
    recommendations, resolved_approval = apply_approval_to_recommendations(
        task_id=task_id,
        out_dir=out_dir,
        recommendations=recommendations,
        approval_state=approval_state,
    )
    return {
        "schema_version": "1.0.0",
        "status": "needs-fix",
        "task_id": task_id,
        "summary_status": str(summary.get("status") or "fail"),
        "failed_step": step_name,
        "approval": resolved_approval,
        "recommendations": recommendations,
        "generated_from": {
            "summary_json": str(out_dir / "summary.json"),
            "step_log": str(log_path) if log_path.exists() else "",
            "step_summary_file": str(failed_step.get("summary_file") or ""),
        },
    }
