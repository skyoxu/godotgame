#!/usr/bin/env python3
"""Developer CLI entry for the Godot+C# template.

This script provides stable subcommands that other tools (BMAD,
task-master-ai, Claude Code, Codex.CLI) can call instead of
reconstructing long Python/PowerShell commands.

All output messages are in English to keep logs uniform.
"""

from __future__ import annotations

import argparse
import subprocess
import sys


def run(cmd: list[str]) -> int:
    """Run a subprocess and return its exit code."""

    print(f"[dev_cli] running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, text=True)
    return proc.returncode


def cmd_run_ci_basic(args: argparse.Namespace) -> int:
    """Run core CI pipeline (dotnet tests + selfcheck + encoding)."""

    return run([
        "py",
        "-3",
        "scripts/python/ci_pipeline.py",
        "all",
        "--solution",
        args.solution,
        "--configuration",
        args.configuration,
        "--godot-bin",
        args.godot_bin,
        "--build-solutions",
    ])


def cmd_run_quality_gates(args: argparse.Namespace) -> int:
    """Run quality_gates.py all with optional hard GdUnit and smoke.""" 

    cmd = [
        "py",
        "-3",
        "scripts/python/quality_gates.py",
        "all",
        "--solution",
        args.solution,
        "--configuration",
        args.configuration,
        "--godot-bin",
        args.godot_bin,
        "--build-solutions",
    ]
    if args.gdunit_hard:
        cmd.append("--gdunit-hard")
    if args.smoke:
        cmd.append("--smoke")
    return run(cmd)


def cmd_run_gdunit_hard(args: argparse.Namespace) -> int:
    """Run hard GdUnit set (Adapters/Config + Security)."""

    return run([
        "py",
        "-3",
        "scripts/python/run_gdunit.py",
        "--prewarm",
        "--godot-bin",
        args.godot_bin,
        "--project",
        "Tests.Godot",
        "--add",
        "tests/Adapters/Config",
        "--add",
        "tests/Security/Hard",
        "--timeout-sec",
        "300",
        "--rd",
        "logs/e2e/dev-cli/gdunit-hard",
    ])


def cmd_run_gdunit_full(args: argparse.Namespace) -> int:
    """Run a broad GdUnit set (Adapters + Security + Integration + UI)."""

    return run([
        "py",
        "-3",
        "scripts/python/run_gdunit.py",
        "--prewarm",
        "--godot-bin",
        args.godot_bin,
        "--project",
        "Tests.Godot",
        "--add",
        "tests/Adapters",
        "--add",
        "tests/Security/Hard",
        "--add",
        "tests/Integration",
        "--add",
        "tests/UI",
        "--timeout-sec",
        "600",
        "--rd",
        "logs/e2e/dev-cli/gdunit-full",
    ])


def cmd_run_preflight(args: argparse.Namespace) -> int:
    """Run local pre-flight checks (dotnet --info + core tests)."""

    return run([
        "py",
        "-3",
        "scripts/python/preflight.py",
        "--test-project",
        args.test_project,
        "--configuration",
        args.configuration,
    ])


def cmd_run_smoke_strict(args: argparse.Namespace) -> int:
    """Run strict headless smoke against Main scene."""

    return run([
        "py",
        "-3",
        "scripts/python/smoke_headless.py",
        "--godot-bin",
        args.godot_bin,
        "--project",
        ".",
        "--scene",
        "res://Game.Godot/Scenes/Main.tscn",
        "--timeout-sec",
        str(args.timeout_sec),
        "--mode",
        "strict",
    ])


def cmd_new_execution_plan(args: argparse.Namespace) -> int:
    """Create a new execution plan scaffold."""

    cmd = [
        "py",
        "-3",
        "scripts/python/new_execution_plan.py",
        "--title",
        args.title,
    ]
    if args.status:
        cmd += ["--status", args.status]
    if args.goal:
        cmd += ["--goal", args.goal]
    if args.scope:
        cmd += ["--scope", args.scope]
    if args.current_step:
        cmd += ["--current-step", args.current_step]
    if args.stop_loss:
        cmd += ["--stop-loss", args.stop_loss]
    if args.next_action:
        cmd += ["--next-action", args.next_action]
    if args.exit_criteria:
        cmd += ["--exit-criteria", args.exit_criteria]
    for item in args.adr:
        cmd += ["--adr", item]
    for item in args.decision_log:
        cmd += ["--decision-log", item]
    if args.task_id:
        cmd += ["--task-id", args.task_id]
    if args.run_id:
        cmd += ["--run-id", args.run_id]
    if args.latest_json:
        cmd += ["--latest-json", args.latest_json]
    if args.output:
        cmd += ["--output", args.output]
    return run(cmd)


def cmd_new_decision_log(args: argparse.Namespace) -> int:
    """Create a new decision log scaffold."""

    cmd = [
        "py",
        "-3",
        "scripts/python/new_decision_log.py",
        "--title",
        args.title,
    ]
    if args.status:
        cmd += ["--status", args.status]
    if args.why_now:
        cmd += ["--why-now", args.why_now]
    if args.context:
        cmd += ["--context", args.context]
    if args.decision:
        cmd += ["--decision", args.decision]
    if args.consequences:
        cmd += ["--consequences", args.consequences]
    if args.recovery_impact:
        cmd += ["--recovery-impact", args.recovery_impact]
    if args.validation:
        cmd += ["--validation", args.validation]
    if args.supersedes:
        cmd += ["--supersedes", args.supersedes]
    if args.superseded_by:
        cmd += ["--superseded-by", args.superseded_by]
    for item in args.adr:
        cmd += ["--adr", item]
    for item in args.execution_plan:
        cmd += ["--execution-plan", item]
    if args.task_id:
        cmd += ["--task-id", args.task_id]
    if args.run_id:
        cmd += ["--run-id", args.run_id]
    if args.latest_json:
        cmd += ["--latest-json", args.latest_json]
    if args.output:
        cmd += ["--output", args.output]
    return run(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dev CLI for Godot+C# template (AI-friendly entrypoint)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # run-ci-basic
    p_ci = sub.add_parser("run-ci-basic", help="run core CI pipeline (dotnet + selfcheck + encoding)")
    p_ci.add_argument("--solution", default="Game.sln")
    p_ci.add_argument("--configuration", default="Debug")
    p_ci.add_argument("--godot-bin", required=True)
    p_ci.set_defaults(func=cmd_run_ci_basic)

    # run-quality-gates
    p_qg = sub.add_parser("run-quality-gates", help="run quality_gates.py all with optional GdUnit hard and smoke")
    p_qg.add_argument("--solution", default="Game.sln")
    p_qg.add_argument("--configuration", default="Debug")
    p_qg.add_argument("--godot-bin", required=True)
    p_qg.add_argument("--gdunit-hard", action="store_true")
    p_qg.add_argument("--smoke", action="store_true")
    p_qg.set_defaults(func=cmd_run_quality_gates)

    # run-gdunit-hard
    p_gh = sub.add_parser("run-gdunit-hard", help="run hard GdUnit set (Adapters/Config + Security)")
    p_gh.add_argument("--godot-bin", required=True)
    p_gh.set_defaults(func=cmd_run_gdunit_hard)

    # run-gdunit-full
    p_gf = sub.add_parser("run-gdunit-full", help="run broad GdUnit tests (Adapters+Security+Integration+UI)")
    p_gf.add_argument("--godot-bin", required=True)
    p_gf.set_defaults(func=cmd_run_gdunit_full)

    # run-preflight
    p_pf = sub.add_parser("run-preflight", help="run local pre-flight checks (dotnet --info + core tests)")
    p_pf.add_argument("--test-project", default="Game.Core.Tests/Game.Core.Tests.csproj")
    p_pf.add_argument("--configuration", default="Debug")
    p_pf.set_defaults(func=cmd_run_preflight)

    # run-smoke-strict
    p_sm = sub.add_parser("run-smoke-strict", help="run strict headless smoke against Main scene")
    p_sm.add_argument("--godot-bin", required=True)
    p_sm.add_argument("--timeout-sec", type=int, default=5)
    p_sm.set_defaults(func=cmd_run_smoke_strict)

    # new-execution-plan
    p_ep = sub.add_parser("new-execution-plan", help="create an execution plan scaffold")
    p_ep.add_argument("--title", required=True)
    p_ep.add_argument("--status", default="active", choices=["active", "paused", "done", "blocked"])
    p_ep.add_argument("--goal", default="TODO: describe goal")
    p_ep.add_argument("--scope", default="TODO: define scope")
    p_ep.add_argument("--current-step", default="TODO: define current step")
    p_ep.add_argument("--stop-loss", default="TODO: define stop-loss boundary")
    p_ep.add_argument("--next-action", default="TODO: define next action")
    p_ep.add_argument("--exit-criteria", default="TODO: define exit criteria")
    p_ep.add_argument("--adr", action="append", default=[])
    p_ep.add_argument("--decision-log", action="append", default=[])
    p_ep.add_argument("--task-id", default="")
    p_ep.add_argument("--run-id", default="")
    p_ep.add_argument("--latest-json", default="")
    p_ep.add_argument("--output", default="")
    p_ep.set_defaults(func=cmd_new_execution_plan)

    # new-decision-log
    p_dl = sub.add_parser("new-decision-log", help="create a decision log scaffold")
    p_dl.add_argument("--title", required=True)
    p_dl.add_argument("--status", default="proposed", choices=["proposed", "accepted", "superseded"])
    p_dl.add_argument("--why-now", default="TODO: explain why now")
    p_dl.add_argument("--context", default="TODO: capture context")
    p_dl.add_argument("--decision", default="TODO: record decision")
    p_dl.add_argument("--consequences", default="TODO: describe consequences")
    p_dl.add_argument("--recovery-impact", default="TODO: describe recovery impact")
    p_dl.add_argument("--validation", default="TODO: describe validation")
    p_dl.add_argument("--supersedes", default="none")
    p_dl.add_argument("--superseded-by", default="none")
    p_dl.add_argument("--adr", action="append", default=[])
    p_dl.add_argument("--execution-plan", action="append", default=[])
    p_dl.add_argument("--task-id", default="")
    p_dl.add_argument("--run-id", default="")
    p_dl.add_argument("--latest-json", default="")
    p_dl.add_argument("--output", default="")
    p_dl.set_defaults(func=cmd_new_decision_log)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return func(args)


if __name__ == "__main__":
    sys.exit(main())
