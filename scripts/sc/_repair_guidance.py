from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from _agent_review_policy import build_agent_review_recommendations
from _util import repo_root, today_str


def _run_git(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(repo_root()),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False,
        )
    except Exception:
        return ""
    return (proc.stdout or "").strip()


def _latest_markdown_file(root: Path) -> str:
    if not root.exists():
        return ""
    candidates = [path for path in root.rglob("*.md") if path.is_file()]
    if not candidates:
        return ""
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return str(candidates[0])


def build_execution_context(
    *,
    task_id: str,
    requested_run_id: str,
    run_id: str,
    out_dir: Path,
    delivery_profile: str,
    security_profile: str,
    summary: dict[str, Any],
    marathon_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _run_git(["rev-parse", "HEAD"])
    recent_log = [line for line in _run_git(["log", "--oneline", "-n", "8"]).splitlines() if line.strip()]
    status_short = [line for line in _run_git(["status", "--short"]).splitlines() if line.strip()]
    failed_step = next((step for step in summary.get("steps", []) if step.get("status") == "fail"), None)

    return {
        "schema_version": "1.0.0",
        "cmd": "sc-review-pipeline",
        "date": today_str(),
        "task_id": task_id,
        "requested_run_id": requested_run_id,
        "run_id": run_id,
        "status": str(summary.get("status") or "fail"),
        "delivery_profile": delivery_profile,
        "security_profile": security_profile,
        "failed_step": str(failed_step.get("name")) if isinstance(failed_step, dict) else "",
        "paths": {
            "repo_root": str(repo_root()),
            "out_dir": str(out_dir),
            "summary_json": str(out_dir / "summary.json"),
            "marathon_state_json": str(out_dir / "marathon-state.json"),
            "repair_guide_json": str(out_dir / "repair-guide.json"),
            "repair_guide_md": str(out_dir / "repair-guide.md"),
            "execution_plans_dir": str(repo_root() / "execution-plans"),
            "decision_logs_dir": str(repo_root() / "decision-logs"),
            "latest_execution_plan": _latest_markdown_file(repo_root() / "execution-plans"),
            "latest_decision_log": _latest_markdown_file(repo_root() / "decision-logs"),
            "agents_index": str(repo_root() / "docs" / "agents" / "00-index.md"),
            "agents_recovery": str(repo_root() / "docs" / "agents" / "01-session-recovery.md"),
        },
        "git": {
            "branch": branch,
            "head": head,
            "recent_log": recent_log,
            "status_short": status_short,
            "dirty": bool(status_short),
        },
        "recovery": {
            "resume_command": f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --resume",
            "abort_command": f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --abort",
            "fork_command": f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --fork",
        },
        "marathon": {
            "status": str((marathon_state or {}).get("status") or ""),
            "next_step_name": str((marathon_state or {}).get("next_step_name") or ""),
            "stop_reason": str((marathon_state or {}).get("stop_reason") or ""),
            "resume_count": int((marathon_state or {}).get("resume_count") or 0),
            "max_step_retries": int((marathon_state or {}).get("max_step_retries") or 0),
            "max_wall_time_sec": int((marathon_state or {}).get("max_wall_time_sec") or 0),
            "context_refresh_needed": bool((marathon_state or {}).get("context_refresh_needed") or False),
            "context_refresh_reasons": list((marathon_state or {}).get("context_refresh_reasons") or []),
            "forked_from_run_id": str((marathon_state or {}).get("forked_from_run_id") or ""),
            "diff_baseline_total_lines": int((((marathon_state or {}).get("diff_stats") or {}).get("baseline") or {}).get("total_lines") or 0),
            "diff_current_total_lines": int((((marathon_state or {}).get("diff_stats") or {}).get("current") or {}).get("total_lines") or 0),
            "diff_growth_total_lines": int((((marathon_state or {}).get("diff_stats") or {}).get("growth") or {}).get("total_lines") or 0),
            "diff_current_categories": list((((marathon_state or {}).get("diff_stats") or {}).get("current") or {}).get("categories") or []),
            "diff_current_axes": list((((marathon_state or {}).get("diff_stats") or {}).get("current") or {}).get("axes") or []),
            "diff_growth_new_categories": list((((marathon_state or {}).get("diff_stats") or {}).get("growth") or {}).get("new_categories") or []),
            "diff_growth_new_axes": list((((marathon_state or {}).get("diff_stats") or {}).get("growth") or {}).get("new_axes") or []),
        },
        "agent_review": {
            "review_verdict": str((((marathon_state or {}).get("agent_review") or {}).get("review_verdict") or "")),
            "recommended_action": str((((marathon_state or {}).get("agent_review") or {}).get("recommended_action") or "")),
            "recommended_refresh_reasons": list((((marathon_state or {}).get("agent_review") or {}).get("recommended_refresh_reasons") or [])),
        },
    }


def _base_recommendation(
    *,
    rec_id: str,
    title: str,
    why: str,
    commands: list[str],
    files: list[str],
) -> dict[str, Any]:
    return {
        "id": rec_id,
        "title": title,
        "why": why,
        "actions": [],
        "commands": commands,
        "files": files,
    }


def _resume_recommendation(task_id: str, step: dict[str, Any]) -> dict[str, Any]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    return _base_recommendation(
        rec_id="pipeline-resume",
        title="Resume the pipeline after fixing the first blocking issue",
        why="Use the stored run artifacts instead of starting a fresh diagnostic branch when the failing step is already isolated.",
        commands=[f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --resume"],
        files=files,
    )


def _fork_recommendation(task_id: str, step: dict[str, Any]) -> dict[str, Any]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    return _base_recommendation(
        rec_id="pipeline-fork",
        title="Fork a new run when you want a clean recovery branch",
        why="Use a new run id when the current artifact set should remain immutable for diagnosis or comparison.",
        commands=[f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --fork"],
        files=files,
    )


def _context_refresh_recommendation(task_id: str, step: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    files.extend(
        [
            str(repo_root() / "AGENTS.md"),
            str(repo_root() / "docs" / "agents" / "00-index.md"),
            str(repo_root() / "docs" / "agents" / "01-session-recovery.md"),
        ]
    )
    joined_reasons = ", ".join(reasons) if reasons else "marathon heuristic requested refresh"
    return _base_recommendation(
        rec_id="pipeline-context-refresh",
        title="Refresh context before the next attempt",
        why=f"The pipeline crossed the refresh threshold: {joined_reasons}. Reload the recovery map before resuming.",
        commands=[
            f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --fork",
            f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --resume",
        ],
        files=files,
    )


def _wall_time_recommendation(task_id: str, step: dict[str, Any]) -> dict[str, Any]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    return _base_recommendation(
        rec_id="pipeline-wall-time",
        title="Resume or fork after wall-time stop-loss",
        why="The current run exhausted its wall-time budget. Continue from the stored checkpoint instead of restarting from scratch.",
        commands=[
            f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --resume",
            f"py -3 scripts/sc/run_review_pipeline.py --task-id {task_id} --fork",
        ],
        files=files,
    )


def _test_recommendations(task_id: str, step: dict[str, Any], log_text: str) -> list[dict[str, Any]]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    recommendations = [
        _resume_recommendation(task_id, step),
        _base_recommendation(
            rec_id="sc-test-rerun",
            title="Rerun isolated sc-test first",
            why="Keep the failure surface small before rerunning the full review pipeline.",
            commands=[" ".join(step.get("cmd") or ["py", "-3", "scripts/sc/test.py", "--task-id", task_id])],
            files=files,
        )
    ]
    if "MSB1009" in log_text or "Project file does not exist" in log_text:
        recommendations.append(
            _base_recommendation(
                rec_id="sc-test-project-path",
                title="Check solution and project targets",
                why="The test runner resolved a missing .csproj or solution path.",
                commands=[f"py -3 scripts/sc/test.py --task-id {task_id} --dry-run"],
                files=files,
            )
        )
    if "coverage" in log_text.lower():
        recommendations.append(
            _base_recommendation(
                rec_id="sc-test-coverage-gate",
                title="Inspect coverage gate before changing thresholds",
                why="A coverage failure should be fixed by adding tests or excluding non-domain code deliberately.",
                commands=[f"py -3 scripts/sc/test.py --task-id {task_id}"],
                files=files,
            )
        )
    if "godot" in log_text.lower() and "not found" in log_text.lower():
        recommendations.append(
            _base_recommendation(
                rec_id="sc-test-godot-bin",
                title="Provide an explicit Godot binary",
                why="The test step could not locate Godot for headless or integration work.",
                commands=[f'py -3 scripts/sc/test.py --task-id {task_id} --godot-bin "$env:GODOT_BIN"'],
                files=files,
            )
        )
    return recommendations


def _acceptance_recommendations(task_id: str, step: dict[str, Any], log_text: str) -> list[dict[str, Any]]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    recommendations = [
        _resume_recommendation(task_id, step),
        _base_recommendation(
            rec_id="acceptance-rerun",
            title="Rerun acceptance only after fixing the first hard failure",
            why="Acceptance failures usually point to missing refs, evidence, or architecture linkage.",
            commands=[" ".join(step.get("cmd") or ["py", "-3", "scripts/sc/acceptance_check.py", "--task-id", task_id])],
            files=files,
        )
    ]
    lowered = log_text.lower()
    if "validate_task_test_refs" in lowered or "require-task-test-refs" in lowered:
        recommendations.append(
            _base_recommendation(
                rec_id="acceptance-test-refs",
                title="Fill task test refs before rerun",
                why="The acceptance gate expects `test_refs` to exist and resolve.",
                commands=[f"py -3 scripts/python/validate_task_test_refs.py --task-id {task_id}"],
                files=files + [str(repo_root() / "docs" / "testing-framework.md")],
            )
        )
    if "validate_acceptance_refs" in lowered or "acceptance refs" in lowered:
        recommendations.append(
            _base_recommendation(
                rec_id="acceptance-refs-align",
                title="Align acceptance refs with task and overlay docs",
                why="Acceptance refs drift usually means overlay, taskmaster, and tests are out of sync.",
                commands=[f"py -3 scripts/python/validate_acceptance_refs.py --task-id {task_id}"],
                files=files,
            )
        )
    if "strict-adr-status" in lowered or "adr" in lowered:
        recommendations.append(
            _base_recommendation(
                rec_id="acceptance-adr-status",
                title="Check ADR status and references",
                why="The acceptance step detected ADR status or linkage issues.",
                commands=["py -3 scripts/python/task_links_validate.py"],
                files=files + [str(repo_root() / "docs" / "architecture" / "ADR_INDEX_GODOT.md")],
            )
        )
    if "headless" in lowered or "e2e" in lowered:
        recommendations.append(
            _base_recommendation(
                rec_id="acceptance-headless",
                title="Inspect headless evidence and rerun only the failing path",
                why="Headless evidence failures are usually environment or resource-path issues.",
                commands=[f'py -3 scripts/sc/acceptance_check.py --task-id {task_id} --godot-bin "$env:GODOT_BIN"'],
                files=files,
            )
        )
    return recommendations


def _llm_review_recommendations(task_id: str, step: dict[str, Any], log_text: str) -> list[dict[str, Any]]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    recommendations = [
        _resume_recommendation(task_id, step),
        _base_recommendation(
            rec_id="llm-review-rerun",
            title="Fix findings before rerunning llm_review",
            why="LLM review should converge on a smaller diff, not be used as the first diagnostic tool.",
            commands=[" ".join(step.get("cmd") or ["py", "-3", "scripts/sc/llm_review.py", "--task-id", task_id])],
            files=files,
        )
    ]
    lowered = log_text.lower()
    if "needs fix" in lowered or "needs-fix" in lowered:
        recommendations.append(
            _base_recommendation(
                rec_id="llm-review-needs-fix",
                title="Resolve the top Needs Fix items first",
                why="The reviewer already narrowed the problem set. Fix the highest-severity findings before asking for another pass.",
                commands=[f"py -3 scripts/sc/llm_review_needs_fix_fast.py --task-id {task_id}"],
                files=files,
            )
        )
    if "semantic" in lowered:
        recommendations.append(
            _base_recommendation(
                rec_id="llm-review-semantic",
                title="Re-align semantics before rerun",
                why="Semantic gate failures usually come from acceptance refs, task context, or contracts drifting apart.",
                commands=[f"py -3 scripts/sc/llm_semantic_gate_all.py --task-id {task_id}"],
                files=files,
            )
        )
    return recommendations


def _load_marathon_state(out_dir: Path) -> dict[str, Any] | None:
    state_path = out_dir / "marathon-state.json"
    if not state_path.exists():
        return None
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def build_repair_guide(summary: dict[str, Any], *, task_id: str, out_dir: Path, marathon_state: dict[str, Any] | None = None) -> dict[str, Any]:
    runtime_state = marathon_state if isinstance(marathon_state, dict) else _load_marathon_state(out_dir)
    agent_review = ((runtime_state or {}).get("agent_review") or {}) if isinstance(runtime_state, dict) else {}
    failed_step = next((step for step in summary.get("steps", []) if step.get("status") == "fail"), None)
    if not isinstance(failed_step, dict):
        recommendations = build_agent_review_recommendations(task_id=task_id, agent_review=agent_review, out_dir=out_dir)
        synthetic_step = {"log": "", "summary_file": ""}
        if isinstance(runtime_state, dict):
            reasons = [str(x) for x in (runtime_state.get("context_refresh_reasons") or []) if str(x).strip()]
            if bool(runtime_state.get("context_refresh_needed")):
                recommendations.append(_context_refresh_recommendation(task_id, synthetic_step, reasons))
            if str(runtime_state.get("stop_reason") or "").strip().lower() == "wall_time_exceeded":
                recommendations.append(_wall_time_recommendation(task_id, synthetic_step))
            if recommendations:
                recommendations.append(_fork_recommendation(task_id, synthetic_step))
        return {
            "schema_version": "1.0.0",
            "status": "needs-fix" if recommendations else "not-needed",
            "task_id": task_id,
            "summary_status": str(summary.get("status") or "ok"),
            "failed_step": "",
            "recommendations": recommendations,
            "generated_from": {
                "summary_json": str(out_dir / "summary.json"),
            },
        }

    log_path = Path(str(failed_step.get("log") or ""))
    log_text = ""
    if log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            log_text = ""
    step_name = str(failed_step.get("name") or "")
    if step_name == "sc-test":
        recommendations = _test_recommendations(task_id, failed_step, log_text)
    elif step_name == "sc-acceptance-check":
        recommendations = _acceptance_recommendations(task_id, failed_step, log_text)
    else:
        recommendations = _llm_review_recommendations(task_id, failed_step, log_text)
    if isinstance(runtime_state, dict):
        reasons = [str(x) for x in (runtime_state.get("context_refresh_reasons") or []) if str(x).strip()]
        if bool(runtime_state.get("context_refresh_needed")):
            recommendations.append(_context_refresh_recommendation(task_id, failed_step, reasons))
        if str(runtime_state.get("stop_reason") or "").strip().lower() == "wall_time_exceeded":
            recommendations.append(_wall_time_recommendation(task_id, failed_step))
        recommendations.append(_fork_recommendation(task_id, failed_step))

    return {
        "schema_version": "1.0.0",
        "status": "needs-fix",
        "task_id": task_id,
        "summary_status": str(summary.get("status") or "fail"),
        "failed_step": step_name,
        "recommendations": recommendations,
        "generated_from": {
            "summary_json": str(out_dir / "summary.json"),
            "step_log": str(log_path) if log_path.exists() else "",
            "step_summary_file": str(failed_step.get("summary_file") or ""),
        },
    }


def render_repair_guide_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Repair Guide")
    lines.append("")
    lines.append(f"- status: {payload.get('status', 'unknown')}")
    lines.append(f"- task_id: {payload.get('task_id', '')}")
    lines.append(f"- summary_status: {payload.get('summary_status', '')}")
    lines.append(f"- failed_step: {payload.get('failed_step', '')}")
    lines.append("")
    recommendations = payload.get("recommendations") or []
    if not recommendations:
        lines.append("No repair action is required. The pipeline either passed or only produced planned/skipped steps.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Recommendations")
    for item in recommendations:
        lines.append(f"- {item.get('id', '')}: {item.get('title', '')}")
        why = str(item.get("why") or "").strip()
        if why:
            lines.append(f"  Why: {why}")
        for command in item.get("commands") or []:
            lines.append(f"  Command: `{command}`")
        for file_path in item.get("files") or []:
            if str(file_path).strip():
                lines.append(f"  File: `{file_path}`")
    lines.append("")
    return "\n".join(lines)
