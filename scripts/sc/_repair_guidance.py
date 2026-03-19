from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

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


def _test_recommendations(task_id: str, step: dict[str, Any], log_text: str) -> list[dict[str, Any]]:
    files = [str(x) for x in [step.get("log"), step.get("summary_file")] if str(x or "").strip()]
    recommendations = [
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


def build_repair_guide(summary: dict[str, Any], *, task_id: str, out_dir: Path) -> dict[str, Any]:
    failed_step = next((step for step in summary.get("steps", []) if step.get("status") == "fail"), None)
    if not isinstance(failed_step, dict):
        return {
            "schema_version": "1.0.0",
            "status": "not-needed",
            "task_id": task_id,
            "summary_status": str(summary.get("status") or "ok"),
            "failed_step": "",
            "recommendations": [],
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
