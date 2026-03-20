#!/usr/bin/env python3
"""
Run a deterministic local review pipeline with one shared run_id:
1) sc-test
2) sc-acceptance-check
3) sc-llm-review
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from agent_to_agent_review import write_agent_review
from _agent_review_policy import apply_agent_review_policy, apply_agent_review_signal
from _delivery_profile import (
    default_security_profile_for_delivery,
    profile_acceptance_defaults,
    profile_llm_review_defaults,
    resolve_delivery_profile,
)
from _approval_contract import approval_request_path, approval_response_path
from _harness_capabilities import harness_capabilities_path, write_harness_capabilities
from _marathon_policy import (
    apply_context_refresh_policy,
    cap_step_timeout,
    mark_wall_time_exceeded,
    refresh_diff_stats,
    wall_time_exceeded,
)
from _marathon_state import (
    build_forked_state,
    build_initial_state,
    can_retry_failed_step,
    load_marathon_state,
    mark_aborted,
    record_step_result,
    resolve_existing_out_dir,
    resume_state,
    save_marathon_state,
    step_is_already_complete,
)
from _pipeline_approval import sync_soft_approval_sidecars
from _pipeline_events import append_run_event, run_events_path
from _pipeline_plan import build_pipeline_steps
from _pipeline_support import (
    load_existing_summary as _load_existing_summary,
    resolve_agent_review_mode as _resolve_agent_review_mode,
    run_step as _run_step,
    upsert_step as _upsert_step,
)
from _repair_guidance import build_execution_context, build_repair_guide, render_repair_guide_markdown
from _summary_schema import SummarySchemaError, validate_pipeline_summary
from _util import repo_root, today_str, write_json, write_text

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run task review pipeline with strict run_id binding.")
    parser.add_argument("--task-id", required=True, help="Task id (e.g. 1 or 1.3).")
    parser.add_argument("--run-id", default=None, help="New run id for normal/fork mode, or selector for resume/abort.")
    parser.add_argument("--fork-from-run-id", default=None, help="Optional source run id selector when using --fork.")
    parser.add_argument("--godot-bin", default=None, help="Godot binary path (or env GODOT_BIN).")
    parser.add_argument("--delivery-profile", default=None, choices=["playable-ea", "fast-ship", "standard"], help="Delivery profile (default: env DELIVERY_PROFILE or fast-ship).")
    parser.add_argument("--security-profile", default=None, choices=["strict", "host-safe"])
    parser.add_argument("--skip-test", action="store_true", help="Skip sc-test step.")
    parser.add_argument("--skip-acceptance", action="store_true", help="Skip sc-acceptance-check step.")
    parser.add_argument("--skip-llm-review", action="store_true", help="Skip sc-llm-review step.")
    parser.add_argument("--skip-agent-review", action="store_true", help="Skip the post-pipeline agent review sidecar.")
    parser.add_argument("--llm-agents", default=None, help="llm_review --agents value. Default follows delivery profile.")
    parser.add_argument("--llm-timeout-sec", type=int, default=None, help="llm_review total timeout. Default follows delivery profile.")
    parser.add_argument("--llm-agent-timeout-sec", type=int, default=None, help="llm_review per-agent timeout. Default follows delivery profile.")
    parser.add_argument("--llm-semantic-gate", default=None, choices=["skip", "warn", "require"])
    parser.add_argument("--llm-base", default="main", help="llm_review --base value.")
    parser.add_argument("--llm-diff-mode", default="full", choices=["full", "summary", "none"], help="llm_review --diff-mode value.")
    parser.add_argument("--llm-no-uncommitted", action="store_true", help="Do not pass --uncommitted to llm_review.")
    parser.add_argument("--llm-strict", action="store_true", help="Pass --strict to llm_review.")
    parser.add_argument("--review-template", default="scripts/sc/templates/llm_review/bmad-godot-review-template.txt", help="llm_review template path.")
    parser.add_argument("--resume", action="store_true", help="Resume the latest matching run for this task.")
    parser.add_argument("--abort", action="store_true", help="Abort the latest matching run for this task without running steps.")
    parser.add_argument("--fork", action="store_true", help="Fork the latest matching run into a new run id and continue there.")
    parser.add_argument("--max-step-retries", type=int, default=0, help="Automatic retry count for a failing step inside this invocation.")
    parser.add_argument("--max-wall-time-sec", type=int, default=0, help="Per-run wall-time budget. 0 disables the budget.")
    parser.add_argument("--context-refresh-after-failures", type=int, default=3, help="Flag context refresh when one step fails this many times. 0 disables.")
    parser.add_argument("--context-refresh-after-resumes", type=int, default=2, help="Flag context refresh when resume count reaches this value. 0 disables.")
    parser.add_argument("--context-refresh-after-diff-lines", type=int, default=300, help="Flag context refresh when working-tree diff grows by this many lines from the run baseline. 0 disables.")
    parser.add_argument("--context-refresh-after-diff-categories", type=int, default=2, help="Flag context refresh when new diff categories added from the run baseline reach this count. 0 disables.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without executing.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow reusing an existing task+run_id output directory by deleting it first.")
    parser.add_argument("--force-new-run-id", action="store_true", help="When task+run_id directory exists, auto-generate a new run_id instead of failing.")
    return parser

def _task_root_id(task_id: str) -> str:
    return str(task_id).strip().split(".", 1)[0].strip()


def _prepare_env(run_id: str, delivery_profile: str, security_profile: str) -> None:
    os.environ["SC_PIPELINE_RUN_ID"] = run_id
    os.environ["SC_TEST_RUN_ID"] = run_id
    os.environ["SC_ACCEPTANCE_RUN_ID"] = run_id
    os.environ["DELIVERY_PROFILE"] = delivery_profile
    os.environ["SECURITY_PROFILE"] = security_profile

def _pipeline_run_dir(task_id: str, run_id: str) -> Path:
    return repo_root() / "logs" / "ci" / today_str() / f"sc-review-pipeline-task-{task_id}-{run_id}"


def _pipeline_latest_index_path(task_id: str) -> Path:
    return repo_root() / "logs" / "ci" / today_str() / f"sc-review-pipeline-task-{task_id}" / "latest.json"

def _write_latest_index(*, task_id: str, run_id: str, out_dir: Path, status: str) -> None:
    path = _pipeline_latest_index_path(task_id)
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


def _allocate_out_dir(task_id: str, requested_run_id: str, *, force_new_run_id: bool, allow_overwrite: bool) -> tuple[str, Path]:
    run_id = requested_run_id
    out_dir = _pipeline_run_dir(task_id, run_id)
    if not out_dir.exists():
        return run_id, out_dir
    if force_new_run_id:
        original_run_id = run_id
        attempts = 0
        while out_dir.exists():
            run_id = uuid.uuid4().hex
            out_dir = _pipeline_run_dir(task_id, run_id)
            attempts += 1
            if attempts > 16:
                raise RuntimeError("failed to allocate a unique run_id after 16 attempts")
        print(f"[sc-review-pipeline] INFO: run_id collision detected, remapped {original_run_id} -> {run_id}")
        return run_id, out_dir
    if not allow_overwrite:
        raise FileExistsError("output directory already exists for this task/run_id")
    shutil.rmtree(out_dir, ignore_errors=False)
    return run_id, out_dir

_refresh_diff_stats = refresh_diff_stats

def _apply_runtime_policy(state: dict[str, Any], *, failure_threshold: int, resume_threshold: int, diff_lines_threshold: int, diff_categories_threshold: int) -> dict[str, Any]:
    return apply_context_refresh_policy(
        _refresh_diff_stats(state),
        failure_threshold=failure_threshold,
        resume_threshold=resume_threshold,
        diff_lines_threshold=diff_lines_threshold,
        diff_categories_threshold=diff_categories_threshold,
    )


def _append_step_event(
    *,
    out_dir: Path,
    task_id: str,
    run_id: str,
    delivery_profile: str,
    security_profile: str,
    step: dict[str, Any],
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
    append_run_event(
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


def _run_agent_review_post_hook(*, out_dir: Path, mode: str, marathon_state: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    payload, resolve_errors, validation_errors = write_agent_review(out_dir=out_dir, reviewer="artifact-reviewer")
    updated_state = apply_agent_review_policy(marathon_state, payload)
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


def _load_source_run(task_id: str, selector_run_id: str | None) -> tuple[Path, dict[str, Any], dict[str, Any] | None]:
    out_dir = resolve_existing_out_dir(task_id=task_id, run_id=selector_run_id, preferred_latest_index=_pipeline_latest_index_path(task_id))
    if out_dir is None:
        raise FileNotFoundError("no existing pipeline run found")
    summary = _load_existing_summary(out_dir) or {}
    if not summary:
        raise RuntimeError(f"existing summary.json is missing or invalid: {out_dir}")
    return out_dir, summary, load_marathon_state(out_dir)


def main() -> int:
    args = build_parser().parse_args()
    task_id = _task_root_id(args.task_id)
    if not task_id:
        print("[sc-review-pipeline] ERROR: invalid --task-id")
        return 2
    if bool(args.allow_overwrite) and bool(args.force_new_run_id):
        print("[sc-review-pipeline] ERROR: --allow-overwrite and --force-new-run-id are mutually exclusive.")
        return 2
    if sum(bool(x) for x in (args.resume, args.abort, args.fork)) > 1:
        print("[sc-review-pipeline] ERROR: --resume, --abort, and --fork are mutually exclusive.")
        return 2

    delivery_profile = resolve_delivery_profile(args.delivery_profile)
    security_profile = str(args.security_profile or default_security_profile_for_delivery(delivery_profile)).strip().lower()
    acceptance_defaults = profile_acceptance_defaults(delivery_profile)
    llm_defaults = profile_llm_review_defaults(delivery_profile)
    agent_review_mode = _resolve_agent_review_mode(delivery_profile)
    llm_agents = str(args.llm_agents or llm_defaults.get("agents") or "all")
    llm_timeout_sec = int(args.llm_timeout_sec or llm_defaults.get("timeout_sec") or 900)
    llm_agent_timeout_sec = int(args.llm_agent_timeout_sec or llm_defaults.get("agent_timeout_sec") or 300)
    llm_semantic_gate = str(args.llm_semantic_gate or llm_defaults.get("semantic_gate") or "require")
    llm_strict = bool(args.llm_strict) or bool(llm_defaults.get("strict", False))

    requested_run_id = str(args.run_id or "").strip() or uuid.uuid4().hex
    run_id = requested_run_id
    summary: dict[str, Any]

    try:
        if args.resume or args.abort:
            out_dir, summary, marathon_state = _load_source_run(task_id, (args.run_id or "").strip() or None)
            run_id = str(summary.get("run_id") or "").strip() or run_id
            requested_run_id = str(summary.get("requested_run_id") or run_id).strip() or run_id
        elif args.fork:
            source_out_dir, source_summary, source_state = _load_source_run(task_id, (args.fork_from_run_id or "").strip() or None)
            run_id, out_dir = _allocate_out_dir(task_id, requested_run_id, force_new_run_id=bool(args.force_new_run_id), allow_overwrite=bool(args.allow_overwrite))
            summary, marathon_state = build_forked_state(
                source_out_dir=source_out_dir,
                source_summary=source_summary,
                source_state=source_state,
                new_run_id=run_id,
                requested_run_id=requested_run_id,
                max_step_retries=args.max_step_retries,
                max_wall_time_sec=args.max_wall_time_sec,
            )
        else:
            run_id, out_dir = _allocate_out_dir(task_id, requested_run_id, force_new_run_id=bool(args.force_new_run_id), allow_overwrite=bool(args.allow_overwrite))
            summary = {
                "cmd": "sc-review-pipeline",
                "task_id": task_id,
                "requested_run_id": requested_run_id,
                "run_id": run_id,
                "allow_overwrite": bool(args.allow_overwrite),
                "force_new_run_id": bool(args.force_new_run_id),
                "status": "ok",
                "steps": [],
            }
            marathon_state = None
    except FileExistsError:
        print("[sc-review-pipeline] ERROR: output directory already exists for this task/run_id. Use a new --run-id, --force-new-run-id, or pass --allow-overwrite.")
        return 2
    except RuntimeError as exc:
        print(f"[sc-review-pipeline] ERROR: {exc}")
        return 2
    except FileNotFoundError:
        print("[sc-review-pipeline] ERROR: no existing pipeline run found for resume/abort/fork.")
        return 2

    _prepare_env(run_id, delivery_profile, security_profile)
    write_text(out_dir / "run_id.txt", run_id + "\n")

    marathon_state = marathon_state or load_marathon_state(out_dir) or build_initial_state(
        task_id=task_id,
        run_id=run_id,
        requested_run_id=requested_run_id,
        max_step_retries=args.max_step_retries,
        max_wall_time_sec=args.max_wall_time_sec,
        summary=summary,
    )
    write_harness_capabilities(
        out_dir=out_dir,
        cmd="sc-review-pipeline",
        task_id=task_id,
        run_id=run_id,
        delivery_profile=delivery_profile,
        security_profile=security_profile,
    )
    if args.abort:
        append_run_event(
            out_dir=out_dir,
            event="run_aborted",
            task_id=task_id,
            run_id=run_id,
            delivery_profile=delivery_profile,
            security_profile=security_profile,
            status="aborted",
            details={"reason": "operator_requested"},
        )
        save_marathon_state(out_dir, mark_aborted(marathon_state, reason="operator_requested"))
        _write_latest_index(task_id=task_id, run_id=run_id, out_dir=out_dir, status="aborted")
        print(f"SC_REVIEW_PIPELINE status=aborted out={out_dir}")
        return 0
    if args.resume:
        if str(marathon_state.get("status") or "").strip().lower() == "aborted":
            print("[sc-review-pipeline] ERROR: the selected run is aborted and cannot be resumed.")
            return 2
        marathon_state = resume_state(marathon_state, max_step_retries=args.max_step_retries, max_wall_time_sec=args.max_wall_time_sec)
    append_run_event(
        out_dir=out_dir,
        event="run_resumed" if args.resume else "run_forked" if args.fork else "run_started",
        task_id=task_id,
        run_id=run_id,
        delivery_profile=delivery_profile,
        security_profile=security_profile,
        status=str(summary.get("status") or "ok"),
        details={
            "requested_run_id": requested_run_id,
            "mode": "resume" if args.resume else "fork" if args.fork else "start",
        },
    )
    marathon_state = _apply_runtime_policy(
        marathon_state,
        failure_threshold=args.context_refresh_after_failures,
        resume_threshold=args.context_refresh_after_resumes,
        diff_lines_threshold=args.context_refresh_after_diff_lines,
        diff_categories_threshold=args.context_refresh_after_diff_categories,
    )

    schema_error_log = out_dir / "summary-schema-validation-error.log"

    def persist() -> bool:
        nonlocal marathon_state
        marathon_state = _apply_runtime_policy(
            marathon_state,
            failure_threshold=args.context_refresh_after_failures,
            resume_threshold=args.context_refresh_after_resumes,
            diff_lines_threshold=args.context_refresh_after_diff_lines,
            diff_categories_threshold=args.context_refresh_after_diff_categories,
        )
        if isinstance(marathon_state.get("agent_review"), dict):
            marathon_state = apply_agent_review_signal(marathon_state, marathon_state["agent_review"])
        try:
            validate_pipeline_summary(summary)
        except SummarySchemaError as exc:
            write_text(schema_error_log, f"{exc}\n")
            write_json(out_dir / "summary.invalid.json", summary)
            save_marathon_state(out_dir, marathon_state)
            _write_latest_index(task_id=task_id, run_id=run_id, out_dir=out_dir, status="fail")
            print(f"[sc-review-pipeline] ERROR: summary schema validation failed. details={schema_error_log}")
            return False
        invalid_summary_path = out_dir / "summary.invalid.json"
        if schema_error_log.exists():
            schema_error_log.unlink(missing_ok=True)
        if invalid_summary_path.exists():
            invalid_summary_path.unlink(missing_ok=True)
        write_harness_capabilities(
            out_dir=out_dir,
            cmd="sc-review-pipeline",
            task_id=task_id,
            run_id=run_id,
            delivery_profile=delivery_profile,
            security_profile=security_profile,
        )
        write_json(out_dir / "summary.json", summary)
        save_marathon_state(out_dir, marathon_state)
        provisional_repair_guide = build_repair_guide(summary, task_id=task_id, out_dir=out_dir, marathon_state=marathon_state)
        approval_state = sync_soft_approval_sidecars(
            out_dir=out_dir,
            task_id=task_id,
            run_id=run_id,
            summary=summary,
            repair_guide=provisional_repair_guide,
            marathon_state=marathon_state,
            explicit_fork=bool(args.fork),
        )
        repair_guide = build_repair_guide(
            summary,
            task_id=task_id,
            out_dir=out_dir,
            marathon_state=marathon_state,
            approval_state=approval_state,
        )
        write_json(out_dir / "repair-guide.json", repair_guide)
        write_text(out_dir / "repair-guide.md", render_repair_guide_markdown(repair_guide))
        write_json(
            out_dir / "execution-context.json",
            build_execution_context(
                task_id=task_id,
                requested_run_id=requested_run_id,
                run_id=run_id,
                out_dir=out_dir,
                delivery_profile=delivery_profile,
                security_profile=security_profile,
                summary=summary,
                marathon_state=marathon_state,
                approval_state=approval_state,
            ),
        )
        for event_payload in approval_state.get("events") or []:
            if not isinstance(event_payload, dict):
                continue
            append_run_event(
                out_dir=out_dir,
                event=str(event_payload.get("event") or "approval_updated"),
                task_id=task_id,
                run_id=run_id,
                delivery_profile=delivery_profile,
                security_profile=security_profile,
                status=str(event_payload.get("status") or "") or None,
                details=dict(event_payload.get("details") or {}),
            )
        _write_latest_index(task_id=task_id, run_id=run_id, out_dir=out_dir, status=str(summary.get("status", "fail")))
        return True

    def add_step(step: dict[str, Any]) -> bool:
        nonlocal marathon_state
        _upsert_step(summary, step)
        marathon_state = record_step_result(marathon_state, step)
        _append_step_event(
            out_dir=out_dir,
            task_id=task_id,
            run_id=run_id,
            delivery_profile=delivery_profile,
            security_profile=security_profile,
            step=step,
        )
        if not persist():
            return False
        return step.get("status") != "fail"

    if not persist():
        return 2

    steps = build_pipeline_steps(
        args=args,
        task_id=task_id,
        run_id=run_id,
        delivery_profile=delivery_profile,
        security_profile=security_profile,
        acceptance_defaults=acceptance_defaults,
        llm_agents=llm_agents,
        llm_timeout_sec=llm_timeout_sec,
        llm_agent_timeout_sec=llm_agent_timeout_sec,
        llm_semantic_gate=llm_semantic_gate,
        llm_strict=llm_strict,
    )

    halt_pipeline = False
    for step_name, cmd, timeout_sec, skipped in steps:
        if (args.resume or args.fork) and step_is_already_complete(marathon_state, step_name):
            continue
        if skipped:
            if not add_step({"name": step_name, "status": "skipped", "rc": 0, "cmd": cmd}):
                return 2 if schema_error_log.exists() else 1
            continue
        if args.dry_run:
            print(f"[dry-run] {step_name}: {' '.join(cmd)}")
            if not add_step({"name": step_name, "status": "planned", "rc": 0, "cmd": cmd}):
                return 2 if schema_error_log.exists() else 1
            continue
        while True:
            if wall_time_exceeded(marathon_state):
                summary["status"] = "fail"
                marathon_state = mark_wall_time_exceeded(marathon_state)
                append_run_event(
                    out_dir=out_dir,
                    event="wall_time_exceeded",
                    task_id=task_id,
                    run_id=run_id,
                    delivery_profile=delivery_profile,
                    security_profile=security_profile,
                    status="fail",
                    details={"step_name": step_name},
                )
                halt_pipeline = True
                break
            step_timeout = cap_step_timeout(timeout_sec, marathon_state)
            ok = add_step(_run_step(out_dir=out_dir, name=step_name, cmd=cmd, timeout_sec=step_timeout))
            if ok:
                break
            if schema_error_log.exists():
                return 2
            if not can_retry_failed_step(marathon_state, step_name):
                break
        if halt_pipeline:
            break
        current_step = (marathon_state.get("steps") or {}).get(step_name, {})
        if str(current_step.get("status") or "") == "fail":
            break

    if halt_pipeline and not persist():
        return 2
    if not persist():
        return 2
    if not args.dry_run and not args.skip_agent_review and agent_review_mode != "skip":
        post_hook_rc, marathon_state = _run_agent_review_post_hook(out_dir=out_dir, mode=agent_review_mode, marathon_state=marathon_state)
        if not persist():
            return 2
        append_run_event(
            out_dir=out_dir,
            event="run_completed",
            task_id=task_id,
            run_id=run_id,
            delivery_profile=delivery_profile,
            security_profile=security_profile,
            status=str(summary.get("status") or "fail"),
            details={"agent_review_rc": post_hook_rc},
        )
        if post_hook_rc != 0:
            return post_hook_rc
    else:
        append_run_event(
            out_dir=out_dir,
            event="run_completed",
            task_id=task_id,
            run_id=run_id,
            delivery_profile=delivery_profile,
            security_profile=security_profile,
            status=str(summary.get("status") or "fail"),
            details={"agent_review_rc": 0, "agent_review_mode": agent_review_mode},
        )
    print(f"SC_REVIEW_PIPELINE status={summary['status']} out={out_dir}")
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
