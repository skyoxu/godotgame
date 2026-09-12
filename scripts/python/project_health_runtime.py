#!/usr/bin/env python3
"""Template-safe task-scoped GdUnit runtime verification for Project Health.

The template may contain no business task data. When task data exists, this module
finds concrete task-scoped `Tests.Godot/**` references, validates them against the
current repository, and can invoke the repository's existing `run_gdunit.py`.
Runtime eligibility is evidence only; a task becomes runtime_verified only after a
fresh task-scoped report contains at least one passing assertion and no failures.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from project_health_knowledge import latest, revision, write_json

TEST_PREFIX = "Tests.Godot/"
CLEANUP_MARGIN_SECONDS = 30


def _walk_tasks(value: Any):
    if isinstance(value, dict):
        if "id" in value and ("title" in value or "status" in value):
            yield value
        for child in value.values():
            yield from _walk_tasks(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_tasks(child)


def _canonical_id(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError("task id is required")
    if any(ch in text for ch in "\\/\r\n\t"):
        raise ValueError("invalid task id")
    return text


def _extract_test_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, str):
        refs.extend(re.findall(r"Tests\.Godot/[A-Za-z0-9_./-]+", value.replace("\\", "/")))
    elif isinstance(value, dict):
        for key, child in value.items():
            if key in {"test_refs", "testRefs", "acceptance", "acceptance_criteria", "testStrategy", "test_strategy"}:
                refs.extend(_extract_test_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(_extract_test_refs(child))
    cleaned = []
    for ref in refs:
        ref = ref.rstrip(".,;:)")
        if ".." in Path(ref).parts or not ref.startswith(TEST_PREFIX):
            continue
        if ref not in cleaned:
            cleaned.append(ref)
    return cleaned


def _task_rows(root: Path) -> list[dict[str, Any]]:
    task_dir = root / ".taskmaster/tasks"
    merged: dict[str, dict[str, Any]] = {}
    if not task_dir.exists():
        return []
    for file in sorted(task_dir.glob("*.json")):
        try:
            payload = json.loads(file.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        for task in _walk_tasks(payload):
            try:
                task_id = _canonical_id(task.get("id"))
            except ValueError:
                continue
            row = merged.setdefault(task_id, {"id": task_id, "title": "", "test_refs": [], "sources": []})
            row["title"] = row["title"] or str(task.get("title") or "")
            row["sources"].append(file.relative_to(root).as_posix())
            for ref in _extract_test_refs(task):
                if ref not in row["test_refs"]:
                    row["test_refs"].append(ref)
    return sorted(merged.values(), key=lambda row: (not row["id"].isdigit(), int(row["id"]) if row["id"].isdigit() else row["id"]))


def _existing_refs(root: Path, refs: list[str]) -> list[str]:
    existing: list[str] = []
    for ref in refs:
        path = root / Path(ref)
        if path.exists():
            existing.append(ref)
            continue
        # Directory-style references may identify a suite prefix.
        prefix = path.parent
        if prefix.exists() and any(prefix.glob(path.name + "*")):
            existing.append(ref)
    return existing


def eligibility(root: Path) -> dict[str, Any]:
    root = root.resolve()
    tasks = []
    for row in _task_rows(root):
        existing = _existing_refs(root, row["test_refs"])
        tasks.append({**row, "eligible": bool(existing), "test_refs": existing})
    return {
        "schema": "godot-project-health.runtime-eligibility.v2",
        "status": "ok",
        "tasks": tasks,
        "eligible_count": sum(1 for row in tasks if row["eligible"]),
        "note": "Eligibility is not runtime acceptance. Runtime verification executes only existing task-scoped Tests.Godot references.",
    }


def _latest_results(report_dir: Path) -> dict[str, Any]:
    summary = report_dir / "run-summary.json"
    if not summary.exists():
        return {}
    try:
        payload = json.loads(summary.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    results = payload.get("results")
    return results if isinstance(results, dict) else {}


def _write_evidence(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    task_id = _canonical_id(payload["task_id"])
    evidence = root / "logs/ci/project-health-knowledge/runtime" / f"task-{task_id}-{uuid.uuid4().hex}.json"
    payload = {**payload, "evidence_path": evidence.relative_to(root).as_posix()}
    write_json(evidence, payload)
    return payload


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _scan_revision(root: Path) -> str:
    return str(latest(root).get("revision") or "")


def _source_revision(root: Path, mode: str) -> tuple[str, bool, str | None]:
    scan_rev = _scan_revision(root)
    head = revision(root)
    if mode == "workspace":
        return head, True, None
    if not re.fullmatch(r"[0-9a-f]{40}", scan_rev):
        return scan_rev, False, "A Git-backed project-health scan is required for main verification"
    main = _git(root, "rev-parse", "--verify", "refs/heads/main")
    if main != scan_rev:
        return scan_rev, False, "The scanned revision does not match local main"
    if head != scan_rev:
        return scan_rev, False, "HEAD does not match the scanned local-main revision"
    dirty = _git(root, "status", "--porcelain")
    if dirty:
        return scan_rev, False, "Main verification requires a clean workspace; use workspace mode for local changes"
    return scan_rev, True, None


def _run_one(root: Path, row: dict[str, Any], godot_bin: str, timeout: int, source_revision: str, mode: str) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    refs = row["test_refs"]
    report = root / "logs/ci/project-health-knowledge/runtime/reports" / uuid.uuid4().hex
    command = [
        sys.executable,
        str(root / "scripts/python/run_gdunit.py"),
        "--godot-bin", godot_bin,
        "--project", "Tests.Godot",
        "--prewarm",
        "--timeout-sec", str(timeout),
        "--rd", str(report),
    ]
    for ref in refs:
        command.extend(["--add", ref.removeprefix(TEST_PREFIX)])
    exit_code: int | None = None
    status = "runtime_unverified"
    reason: str | None = None
    stdout = ""
    stderr = ""
    try:
        proc = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout + CLEANUP_MARGIN_SECONDS,
        )
        exit_code = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
        results = _latest_results(report)
        passing = bool(results.get("tests", 0) > 0 and results.get("failures") == 0 and results.get("errors") == 0)
        if exit_code == 0 and passing:
            status = "passed"
        else:
            status = "failed"
            reason = "Task-scoped GdUnit assertions did not produce a clean non-empty report"
    except subprocess.TimeoutExpired:
        status = "failed"
        reason = "runtime test timed out"
        results = _latest_results(report)
    report.mkdir(parents=True, exist_ok=True)
    (report / "project-health-stdout.txt").write_text(stdout[-200000:], encoding="utf-8")
    (report / "project-health-stderr.txt").write_text(stderr[-200000:], encoding="utf-8")
    return _write_evidence(root, {
        "schema": "godot-project-health.runtime-evidence.v1",
        "task_id": row["id"],
        "title": row["title"],
        "source_revision": source_revision,
        "verification_mode": mode,
        "test_refs": refs,
        "command": command,
        "status": status,
        "reason": reason,
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "exit_code": exit_code,
        "report_path": report.relative_to(root).as_posix(),
        "test_results": results,
        "runtime_verified": status == "passed" and mode == "main",
        "workspace_verified": status == "passed" and mode == "workspace",
    })


def verify(
    root: Path,
    godot_bin: str,
    timeout: int = 600,
    task_id: str | None = None,
    task_ids: list[str] | None = None,
    all_eligible: bool = False,
    global_timeout: int = 3600,
    mode: str = "main",
) -> dict[str, Any]:
    root = root.resolve()
    if timeout <= 0 or global_timeout <= 0:
        raise ValueError("timeout values must be positive")
    if mode not in {"main", "workspace"}:
        raise ValueError("mode must be main or workspace")
    if sum(bool(value) for value in (task_id, task_ids, all_eligible)) > 1:
        raise ValueError("Use only one task selection mode")
    candidates = [row for row in eligibility(root)["tasks"] if row["eligible"]]
    if task_id is not None:
        wanted = {_canonical_id(task_id)}
    elif task_ids is not None:
        wanted = {_canonical_id(value) for value in task_ids}
    elif all_eligible:
        wanted = {row["id"] for row in candidates}
    else:
        raise ValueError("Select --task-id, --task-ids, or --all-eligible")
    selected = [row for row in candidates if row["id"] in wanted]
    missing = sorted(wanted - {row["id"] for row in selected})
    if missing:
        raise ValueError("Runtime-eligible tasks not found: " + ",".join(missing))

    lock = root / "logs/ci/project-health-knowledge/runtime/batch.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise ValueError("Another runtime verification batch is active") from exc
    try:
        source_revision, allowed, reason = _source_revision(root, mode)
        if not allowed:
            results = []
            for row in selected:
                now = datetime.now(timezone.utc).isoformat()
                results.append(_write_evidence(root, {
                    "schema": "godot-project-health.runtime-evidence.v1",
                    "task_id": row["id"], "title": row["title"], "source_revision": source_revision,
                    "verification_mode": mode, "test_refs": row["test_refs"], "command": [],
                    "status": "runtime_unverified", "reason": reason, "started_at": now,
                    "finished_at": now, "exit_code": None, "report_path": None, "test_results": {},
                    "runtime_verified": False, "workspace_verified": False,
                }))
        else:
            deadline = time.monotonic() + global_timeout
            results = []
            for row in selected:
                remaining = int(deadline - time.monotonic())
                if remaining <= CLEANUP_MARGIN_SECONDS:
                    now = datetime.now(timezone.utc).isoformat()
                    results.append(_write_evidence(root, {
                        "schema": "godot-project-health.runtime-evidence.v1",
                        "task_id": row["id"], "title": row["title"], "source_revision": source_revision,
                        "verification_mode": mode, "test_refs": row["test_refs"], "command": [],
                        "status": "runtime_unverified", "reason": "Global runtime timeout reached before task start",
                        "started_at": now, "finished_at": now, "exit_code": None, "report_path": None,
                        "test_results": {}, "runtime_verified": False, "workspace_verified": False,
                    }))
                    continue
                results.append(_run_one(root, row, godot_bin, min(timeout, remaining - CLEANUP_MARGIN_SECONDS), source_revision, mode))
        output = {
            "schema": "godot-project-health.runtime-index.v1",
            "source_revision": source_revision,
            "verification_mode": mode,
            "tasks": results,
            "summary": {
                "total": len(results),
                "passed": sum(row["status"] == "passed" for row in results),
                "failed": sum(row["status"] == "failed" for row in results),
                "runtime_unverified": sum(row["status"] == "runtime_unverified" for row in results),
                "runtime_verified": sum(bool(row.get("runtime_verified")) for row in results),
                "workspace_verified": sum(bool(row.get("workspace_verified")) for row in results),
            },
        }
        write_json(root / f"logs/ci/project-health-knowledge/runtime/{'latest' if mode == 'main' else 'workspace-latest'}.json", output)
        return output
    finally:
        try:
            lock.rmdir()
        except OSError:
            pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--godot-bin")
    parser.add_argument("--timeout-sec", type=int, default=600)
    parser.add_argument("--global-timeout-sec", type=int, default=3600)
    parser.add_argument("--task-id")
    parser.add_argument("--task-ids", help="Comma-separated task ids")
    parser.add_argument("--all-eligible", action="store_true")
    parser.add_argument("--mode", choices=("main", "workspace"), default="main")
    parser.add_argument("--eligibility-only", action="store_true")
    args = parser.parse_args(argv)
    if args.eligibility_only or not any((args.task_id, args.task_ids, args.all_eligible)):
        print(json.dumps(eligibility(args.repo_root.resolve()), ensure_ascii=False, indent=2))
        return 0
    godot_bin = args.godot_bin or os.environ.get("GODOT_BIN")
    if not godot_bin:
        raise SystemExit("--godot-bin or GODOT_BIN is required for runtime verification")
    payload = verify(
        args.repo_root, godot_bin, args.timeout_sec, args.task_id,
        args.task_ids.split(",") if args.task_ids else None,
        args.all_eligible, args.global_timeout_sec, args.mode,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
