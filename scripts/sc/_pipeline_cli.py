from __future__ import annotations

import argparse
import os


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


def task_root_id(task_id: str) -> str:
    return str(task_id).strip().split(".", 1)[0].strip()


def prepare_env(run_id: str, delivery_profile: str, security_profile: str) -> None:
    os.environ["SC_PIPELINE_RUN_ID"] = run_id
    os.environ["SC_TEST_RUN_ID"] = run_id
    os.environ["SC_ACCEPTANCE_RUN_ID"] = run_id
    os.environ["DELIVERY_PROFILE"] = delivery_profile
    os.environ["SECURITY_PROFILE"] = security_profile
