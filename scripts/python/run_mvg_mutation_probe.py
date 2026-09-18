#!/usr/bin/env python3
"""Optional parameterized MVG mutation experiment; not a whole-program mutation score or gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import uuid
from pathlib import Path

from _mvg_execution import execute_test
from _mvg_manifest import safe_path
from _project_health_runtime_snapshot import prepare_snapshot
from run_mvg_acceptance import git, write_json

SCHEMA = "godotgame.mvg-mutation-probe.v1"


def _read_spec(root: Path, path: str) -> dict:
    return json.loads(safe_path(root, path).read_text(encoding="utf-8-sig"))


def _validate_spec(root: Path, doc: dict) -> list[str]:
    errors: list[str] = []
    try:
        if doc.get("schema_version") != SCHEMA:
            errors.append("Unsupported schema_version")
        source = safe_path(root, doc["source_path"])
        if not source.is_file():
            errors.append("Mutation source does not exist")
        test = doc["test"]
        if test["kind"] != "dotnet":
            errors.append("Mutation probe currently requires a dotnet test")
        if not safe_path(root, test["path"]).is_file():
            errors.append("Mutation test does not exist")
        if type(test["min_tests"]) is not int or test["min_tests"] < 1:
            errors.append("Mutation test min_tests must be positive")
        mutants = doc["mutants"]
        if not mutants:
            errors.append("At least one mutant is required")
        ids = [row["id"] for row in mutants]
        if len(ids) != len(set(ids)):
            errors.append("Mutation ids must be unique")
        for row in mutants:
            if not row["before"] or row["before"] == row["after"]:
                errors.append(f"{row['id']}: mutation replacement must change non-empty text")
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"Malformed mutation spec: {exc}")
    return errors


def run(args: argparse.Namespace, root: Path | None = None) -> int:
    root = (root or Path(__file__).resolve().parents[2]).resolve()
    out = root / "logs/ci/mvg-mutation" / uuid.uuid4().hex
    out.mkdir(parents=True)
    summary = {
        "schema_version": SCHEMA,
        "status": "blocked",
        "mutants": [],
        "default_gate": False,
    }
    rc = 1

    try:
        if args.timeout_sec < 1:
            raise ValueError("timeout-sec must be positive")
        revision = git(root, "rev-parse", "--verify", args.revision + "^{commit}")
        summary["base_commit"] = revision
        deadline = time.monotonic() + args.timeout_sec
        work = out / "snapshot"
        summary["inputs"] = prepare_snapshot(
            root,
            work,
            revision,
            "main" if args.snapshot == "commit" else "workspace",
            deadline,
        )

        doc = _read_spec(work, args.spec)
        errors = _validate_spec(work, doc)
        summary["validation_errors"] = errors
        if errors:
            raise ValueError("; ".join(errors))

        source_rel = doc["source_path"]
        test = dict(doc["test"])
        summary["scope"] = source_rel
        baseline = execute_test(work, test, out / "baseline", "", deadline)
        summary["baseline"] = baseline
        if baseline["status"] != "passed":
            raise RuntimeError("Baseline did not pass; mutation results would be uninterpretable")

        source = safe_path(work, source_rel)
        original = source.read_bytes()
        summary["source_sha256"] = hashlib.sha256(original).hexdigest()

        try:
            for row in doc["mutants"]:
                before = row["before"].encode()
                after = row["after"].encode()
                if original.count(before) != 1:
                    raise ValueError("Mutation target drift: " + row["id"])
                source.write_bytes(original.replace(before, after))
                result = execute_test(work, test, out / row["id"], "", deadline)
                evidence = result["evidence"]
                killed = (
                    result["exit_code"] not in {0, 124, 127}
                    and evidence["failed"] > 0
                    and evidence["tests"] >= test["min_tests"]
                    and evidence["skipped"] == 0
                    and evidence["reason"] in {
                        "failed-skipped-or-empty-tests",
                        "reported-suite-failure",
                    }
                )
                status = "killed" if killed else ("survived" if result["status"] == "passed" else "unverified")
                summary["mutants"].append(
                    {
                        "id": row["id"],
                        "before": row["before"],
                        "after": row["after"],
                        "status": status,
                        "execution": result,
                    }
                )
                source.write_bytes(original)
                if time.monotonic() >= deadline:
                    raise TimeoutError("Global mutation budget exhausted")
        finally:
            source.write_bytes(original)

        summary["status"] = (
            "passed"
            if all(row["status"] == "killed" for row in summary["mutants"])
            else "needs-investigation"
        )
        rc = 0 if summary["status"] == "passed" else 1
    except (
        OSError,
        ValueError,
        RuntimeError,
        TimeoutError,
        subprocess.SubprocessError,
        KeyError,
        TypeError,
    ) as exc:
        summary["reason"] = str(exc)
    finally:
        write_json(out / "summary.json", summary)
        print(json.dumps({"status": summary["status"], "summary": str(out / "summary.json")}))
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Repository-relative mutation spec JSON")
    parser.add_argument("--timeout-sec", type=int, default=900)
    parser.add_argument("--snapshot", choices=["workspace", "commit"], default="workspace")
    parser.add_argument("--revision", default="HEAD")
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
