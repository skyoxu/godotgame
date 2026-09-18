#!/usr/bin/env python3
"""Plan, recommend, or execute MVG integration tests against an isolated snapshot."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from _mvg_execution import execute_test
from _mvg_manifest import read_manifest, recommend, validate_manifest
from _project_health_runtime_snapshot import prepare_snapshot


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        timeout=30,
    ).stdout.decode("utf-8").strip()


def changed_paths(
    root: Path,
    base: str,
    revision: str = "HEAD",
    *,
    workspace: bool = True,
) -> tuple[list[str], str]:
    try:
        paths: set[str] = set()
        if base:
            resolved = git(root, "rev-parse", "--verify", base + "^{commit}")
            paths.update(
                git(root, "diff", "--name-only", "--no-renames", "-z", resolved, revision).split("\0")
            )
        if workspace:
            paths.update(
                git(root, "diff", "--name-only", "--no-renames", "-z", revision).split("\0")
            )
            paths.update(git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0"))
        actual = sorted(paths - {""})
        return actual, "" if actual else "No changed paths; absence is not proof of no impact"
    except (subprocess.SubprocessError, OSError) as exc:
        return [], "Git change range unavailable: " + str(exc)


def register_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", required=True, help="Repository-relative MVG manifest JSON")
    parser.add_argument("--mode", choices=["plan", "recommend", "run"], default="plan")
    parser.add_argument("--snapshot", choices=["workspace", "commit"], default="workspace")
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument(
        "--base",
        default="",
        help="Optional comparison base; impact recommendations never exclude required tests",
    )
    parser.add_argument("--godot-bin", default=os.environ.get("GODOT_BIN", ""))
    parser.add_argument("--timeout-sec", type=int, default=900, help="Global runtime budget")
    parser.add_argument(
        "--challenge-input",
        action="store_true",
        help="After baseline passes, run manifest-declared negative wiring challenges",
    )


def _challenge_detected(result: dict, challenge: dict) -> bool:
    evidence = result.get("evidence") or {}
    expected = challenge["expected_failure_contains"]
    return (
        result.get("exit_code") not in {0, 124, 127}
        and int(evidence.get("failed", 0)) > 0
        and int(evidence.get("skipped", 0)) == 0
        and any(expected in message for message in evidence.get("failure_messages", []))
        and evidence.get("reason") in {"failed-skipped-or-empty-tests", "reported-suite-failure"}
    )


def run(args: argparse.Namespace, root: Path | None = None) -> int:
    root = (root or Path(__file__).resolve().parents[2]).resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    out = root / "logs/ci/mvg-acceptance" / run_id
    out.mkdir(parents=True)
    summary = {
        "schema_version": "godotgame.mvg-acceptance.v1",
        "run_id": run_id,
        "mode": args.mode,
        "status": "blocked",
        "runtime_verified": False,
        "steps": [],
        "authorizes_task_status_write": False,
    }
    exit_code = 1

    try:
        if args.timeout_sec < 1:
            raise ValueError("timeout-sec must be positive")

        revision = git(root, "rev-parse", "--verify", args.revision + "^{commit}")
        summary.update(
            base_commit=revision,
            workspace_dirty=bool(git(root, "status", "--porcelain")),
        )
        deadline = time.monotonic() + args.timeout_sec
        execution_root = root

        if args.mode == "run" or args.snapshot == "commit":
            execution_root = out / "snapshot"
            snapshot = prepare_snapshot(
                root,
                execution_root,
                revision,
                "main" if args.snapshot == "commit" else "workspace",
                deadline,
            )
            summary["source_revision"] = snapshot["source_revision"]
            summary["snapshot_digest"] = snapshot["snapshot_digest"]
            summary["input_manifest"] = str(out / "input-manifest.json")

        doc = read_manifest(execution_root, args.manifest)
        errors = validate_manifest(execution_root, doc, executable=args.mode == "run")
        summary.update(
            mvg_id=doc.get("mvg_id"),
            manifest=args.manifest,
            validation_errors=errors,
        )
        if errors:
            raise ValueError("; ".join(errors))

        comparison_revision = revision if args.snapshot == "commit" else git(root, "rev-parse", "HEAD")
        paths, unknown = changed_paths(
            root,
            args.base,
            comparison_revision,
            workspace=args.snapshot == "workspace",
        )
        summary["changed_paths"] = paths
        summary["recommendation"] = recommend(doc, paths, unknown_reason=unknown)
        summary["recommendation"]["comparison_target"] = (
            summary.get("source_revision", "workspace")
            if args.snapshot == "workspace"
            else revision
        )
        summary["recommendation"]["includes_working_changes"] = args.snapshot == "workspace"
        summary["required_tests"] = [test["id"] for test in doc["tests"]]

        if args.mode != "run":
            summary["status"] = "planned" if args.mode == "plan" else "recommended"
            exit_code = 0
        else:
            env = dict(os.environ)
            env["APPDATA"] = str(out / "user-data")
            env["XDG_DATA_HOME"] = str(out / "user-data")
            env["GDUNIT_STRICT_EXIT_CODE"] = "1"
            godot_ready = False

            for test in doc["tests"]:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Global runtime budget exhausted")
                result = execute_test(
                    execution_root,
                    test,
                    out / test["id"],
                    args.godot_bin,
                    deadline,
                    env,
                    prewarm=not godot_ready,
                )
                summary["steps"].append(result)
                if result["status"] != "passed":
                    raise RuntimeError("Required test failed or is unverified: " + test["id"])
                if test["kind"] == "gdunit":
                    godot_ready = True

            if args.challenge_input:
                targets = [test for test in doc["tests"] if test.get("challenge")]
                if not targets:
                    raise ValueError("Manifest has no input challenge target")
                summary["challenges"] = []
                for test in targets:
                    challenge = test["challenge"]
                    challenge_env = dict(env)
                    challenge_env.update(challenge.get("env", {}))
                    result = execute_test(
                        execution_root,
                        test,
                        out / ("challenge-" + test["id"]),
                        args.godot_bin,
                        deadline,
                        challenge_env,
                        prewarm=not godot_ready,
                    )
                    result["challenge_id"] = challenge["id"]
                    result["defect_detected"] = _challenge_detected(result, challenge)
                    summary["challenges"].append(result)
                    if not result["defect_detected"]:
                        raise RuntimeError(
                            "Negative wiring challenge was not demonstrated by the expected assertion: "
                            + challenge["id"]
                        )
                    if test["kind"] == "gdunit":
                        godot_ready = True

            summary.update(status="passed", runtime_verified=True)
            exit_code = 0

    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        RuntimeError,
        subprocess.SubprocessError,
        TimeoutError,
    ) as exc:
        summary["reason"] = str(exc)
    finally:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        write_json(out / "summary.json", summary)
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "runtime_verified": summary["runtime_verified"],
                    "summary": str(out / "summary.json"),
                    "reason": summary.get("reason", ""),
                }
            )
        )
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    register_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
