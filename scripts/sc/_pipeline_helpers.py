from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any, Callable

from _approval_contract import approval_request_path, approval_response_path
from _harness_capabilities import harness_capabilities_path
from _pipeline_events import run_events_path
from _util import repo_root, today_str, write_json, write_text


def pipeline_run_dir(task_id: str, run_id: str) -> Path:
    return repo_root() / "logs" / "ci" / today_str() / f"sc-review-pipeline-task-{task_id}-{run_id}"


def pipeline_latest_index_path(task_id: str) -> Path:
    return repo_root() / "logs" / "ci" / today_str() / f"sc-review-pipeline-task-{task_id}" / "latest.json"


def write_latest_index(
    *,
    task_id: str,
    run_id: str,
    out_dir: Path,
    status: str,
    latest_index_path_fn: Callable[[str], Path],
) -> None:
    path = latest_index_path_fn(task_id)
    payload = {
        "task_id": task_id,
        "run_id": run_id,
        "status": status,
        "date": today_str(),
        "latest_out_dir": str(out_dir),
        "summary_path": str(out_dir / "summary.json"),
        "execution_context_path": str(out_dir / "execution-context.json"),
        "repair_guide_json_path": str(out_dir / "repair-guide.json"),
        "repair_guide_md_path": str(out_dir / "repair-guide.md"),
        "marathon_state_path": str(out_dir / "marathon-state.json"),
        "run_events_path": str(run_events_path(out_dir)),
        "harness_capabilities_path": str(harness_capabilities_path(out_dir)),
    }
    if approval_request_path(out_dir).exists():
        payload["approval_request_path"] = str(approval_request_path(out_dir))
    if approval_request_path(out_dir).exists() and approval_response_path(out_dir).exists():
        payload["approval_response_path"] = str(approval_response_path(out_dir))
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
        same_run = (
            isinstance(existing, dict)
            and str(existing.get("run_id") or "").strip() == run_id
            and str(existing.get("latest_out_dir") or "").strip() == str(out_dir)
        )
        if same_run:
            for key in ("agent_review_json_path", "agent_review_md_path"):
                value = str(existing.get(key) or "").strip()
                if value:
                    payload[key] = value
    write_json(path, payload)


def allocate_out_dir(
    task_id: str,
    requested_run_id: str,
    *,
    force_new_run_id: bool,
    allow_overwrite: bool,
    run_dir_fn: Callable[[str, str], Path],
) -> tuple[str, Path]:
    run_id = requested_run_id
    out_dir = run_dir_fn(task_id, run_id)
    if not out_dir.exists():
        return run_id, out_dir
    if force_new_run_id:
        original_run_id = run_id
        attempts = 0
        while out_dir.exists():
            run_id = uuid.uuid4().hex
            out_dir = run_dir_fn(task_id, run_id)
            attempts += 1
            if attempts > 16:
                raise RuntimeError("failed to allocate a unique run_id after 16 attempts")
        print(f"[sc-review-pipeline] INFO: run_id collision detected, remapped {original_run_id} -> {run_id}")
        return run_id, out_dir
    if not allow_overwrite:
        raise FileExistsError("output directory already exists for this task/run_id")
    shutil.rmtree(out_dir, ignore_errors=False)
    return run_id, out_dir


def append_step_event(
    *,
    out_dir: Path,
    task_id: str,
    run_id: str,
    delivery_profile: str,
    security_profile: str,
    step: dict[str, Any],
    append_run_event_fn: Callable[..., None],
) -> None:
    status = str(step.get("status") or "").strip().lower()
    event_name = {
        "planned": "step_planned",
        "skipped": "step_skipped",
        "ok": "step_completed",
        "fail": "step_failed",
    }.get(status, "step_updated")
    details: dict[str, Any] = {}
    for key in ("rc", "log", "summary_file", "reported_out_dir"):
        value = step.get(key)
        if value not in (None, ""):
            details[key] = value
    append_run_event_fn(
        out_dir=out_dir,
        event=event_name,
        task_id=task_id,
        run_id=run_id,
        delivery_profile=delivery_profile,
        security_profile=security_profile,
        step_name=str(step.get("name") or "").strip() or None,
        status=status or None,
        details=details,
    )


def run_agent_review_post_hook(
    *,
    out_dir: Path,
    mode: str,
    marathon_state: dict[str, Any],
    write_agent_review_fn: Callable[..., tuple[dict[str, Any], list[str], list[str]]],
    apply_agent_review_policy_fn: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    payload, resolve_errors, validation_errors = write_agent_review_fn(out_dir=out_dir, reviewer="artifact-reviewer")
    updated_state = apply_agent_review_policy_fn(marathon_state, payload)
    action = str(((updated_state.get("agent_review") or {}).get("recommended_action")) or "").strip() or "none"
    lines: list[str] = []
    for item in resolve_errors:
        lines.append(f"[sc-agent-review] ERROR: {item}")
    for item in validation_errors:
        lines.append(f"[sc-agent-review] ERROR: {item}")
    lines.append(f"SC_AGENT_REVIEW status={payload['review_verdict']} action={action} out={out_dir}")
    write_text(out_dir / "sc-agent-review.log", "\n".join(lines) + "\n")
    print("\n".join(lines))
    if resolve_errors or validation_errors:
        return 2, updated_state
    verdict = str(payload.get("review_verdict") or "").strip().lower()
    if mode == "require" and verdict in {"needs-fix", "block"}:
        return 1, updated_state
    return 0, updated_state


def load_source_run(
    task_id: str,
    selector_run_id: str | None,
    *,
    latest_index_path: Path,
    resolve_existing_out_dir_fn: Callable[..., Path | None],
    load_existing_summary_fn: Callable[[Path], dict[str, Any] | None],
    load_marathon_state_fn: Callable[[Path], dict[str, Any] | None],
) -> tuple[Path, dict[str, Any], dict[str, Any] | None]:
    out_dir = resolve_existing_out_dir_fn(task_id=task_id, run_id=selector_run_id, preferred_latest_index=latest_index_path)
    if out_dir is None:
        raise FileNotFoundError("no existing pipeline run found")
    summary = load_existing_summary_fn(out_dir) or {}
    if not summary:
        raise RuntimeError(f"existing summary.json is missing or invalid: {out_dir}")
    return out_dir, summary, load_marathon_state_fn(out_dir)
