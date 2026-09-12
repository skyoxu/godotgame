#!/usr/bin/env python3
"""Task-scoped GdUnit runtime verification on immutable Project Health snapshots."""
from __future__ import annotations

import argparse
import hashlib
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

from _project_health_runtime_snapshot import prepare_snapshot
from project_health_knowledge import latest, main_revision, task_rows, write_json

TEST_PREFIX = "Tests.Godot/"
CLEANUP_MARGIN_SECONDS = 30


def _canonical_id(value: Any) -> str:
    text = str(value or "").strip()
    if not text or any(ch in text for ch in "\\/\r\n\t"):
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
            elif isinstance(child, (dict, list)):
                refs.extend(_extract_test_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(_extract_test_refs(child))
    cleaned: list[str] = []
    for ref in refs:
        ref = ref.rstrip(".,;:)")
        if ".." in Path(ref).parts or not ref.startswith(TEST_PREFIX):
            continue
        if ref not in cleaned:
            cleaned.append(ref)
    return cleaned


def _rows(root: Path) -> list[dict[str, Any]]:
    state = latest(root)
    manifest = {str(record.get("path") or "") for record in state.get("records", [])}
    result = []
    for row in task_rows(root, state):
        combined = {"task": row.get("task"), "mappings": row.get("mappings")}
        refs = _extract_test_refs(combined)
        existing = [ref for ref in refs if ref in manifest or any(path.startswith(ref.rstrip("/") + "/") for path in manifest)]
        gameplay = any(path.endswith("/tasks_gameplay.json") or path.endswith("tasks_gameplay.json") for path in row.get("sources", []))
        result.append({
            "id": _canonical_id(row["id"]),
            "title": row.get("title", ""),
            "test_refs": existing,
            "sources": row.get("sources", []),
            "gameplay": gameplay,
            "eligible": bool(existing),
        })
    return result


def eligibility(root: Path) -> dict[str, Any]:
    root = root.resolve()
    rows = _rows(root)
    return {
        "schema": "godot-project-health.runtime-eligibility.v3",
        "status": "ok",
        "revision": latest(root).get("revision"),
        "tasks": rows,
        "eligible_count": sum(1 for row in rows if row["eligible"]),
        "gameplay_count": sum(1 for row in rows if row["gameplay"]),
        "note": "Eligibility is not runtime acceptance. Verification executes only real task-scoped Tests.Godot refs; gameplay rows without refs remain runtime_unverified.",
    }


def _report_counts(report_dir: Path) -> dict[str, Any]:
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


def _unverified(root: Path, row: dict[str, Any], revision: str, mode: str, reason: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return _write_evidence(root, {
        "schema": "godot-project-health.runtime-evidence.v2",
        "task_id": row["id"], "title": row.get("title", ""), "source_revision": revision,
        "task_definition_revision": latest(root).get("revision"), "verification_mode": mode,
        "test_refs": row.get("test_refs", []), "scenes": [], "command": [], "status": "runtime_unverified",
        "reason": reason, "started_at": now, "finished_at": now, "exit_code": None,
        "report_path": None, "test_results": {}, "runtime_verified": False, "workspace_verified": False,
    })


def _run_process(command: list[str], cwd: Path, timeout: int) -> tuple[int | None, str, str, bool]:
    proc = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    try:
        stdout, stderr = proc.communicate(timeout=timeout + CLEANUP_MARGIN_SECONDS)
        return proc.returncode, stdout, stderr, False
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=15)
        else:
            proc.kill()
        try:
            stdout, stderr = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            stdout, stderr = "", ""
        return None, stdout, stderr, True


def _run_one(root: Path, execution_root: Path, row: dict[str, Any], godot_bin: str, timeout: int, source_revision: str, task_definition_revision: str, mode: str) -> dict[str, Any]:
    refs = row.get("test_refs", [])
    if not refs:
        return _unverified(root, row, source_revision, mode, "No task-scoped Godot/GdUnit assertion path was found")
    started = datetime.now(timezone.utc).isoformat()
    report = root / "logs/ci/project-health-knowledge/runtime/reports" / uuid.uuid4().hex
    report.mkdir(parents=True, exist_ok=False)
    command = [
        sys.executable,
        str(execution_root / "scripts/python/run_gdunit.py"),
        "--godot-bin", godot_bin,
        "--project", "Tests.Godot",
        "--prewarm",
        "--timeout-sec", str(timeout),
        "--rd", str(report),
    ]
    for ref in refs:
        command.extend(["--add", ref.removeprefix(TEST_PREFIX)])
    exit_code, stdout, stderr, timed_out = _run_process(command, execution_root, timeout)
    (report / "project-health-stdout.txt").write_text(stdout[-200000:], encoding="utf-8")
    (report / "project-health-stderr.txt").write_text(stderr[-200000:], encoding="utf-8")
    results = _report_counts(report)
    passing = bool(results.get("tests", 0) > 0 and results.get("failures") == 0 and results.get("errors") == 0)
    status = "passed" if exit_code == 0 and passing and not timed_out else "failed"
    reason = None if status == "passed" else ("runtime test timed out" if timed_out else "Task-scoped GdUnit assertions did not produce a clean non-empty report")
    return _write_evidence(root, {
        "schema": "godot-project-health.runtime-evidence.v2",
        "task_id": row["id"], "title": row.get("title", ""), "source_revision": source_revision,
        "task_definition_revision": task_definition_revision, "verification_mode": mode,
        "test_refs": refs, "scenes": [], "command": command, "status": status, "reason": reason,
        "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(), "exit_code": exit_code,
        "report_path": report.relative_to(root).as_posix(), "test_results": results,
        "runtime_verified": False, "workspace_verified": False,
    })


def _inputs_unchanged(snapshot_root: Path, manifest: dict[str, Any]) -> bool:
    for path, digest in manifest.get("files", {}).items():
        candidate = snapshot_root / Path(path)
        if not candidate.is_file() or hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
            return False
    return True


def verify(
    root: Path,
    godot_bin: str,
    timeout: int = 600,
    task_id: str | None = None,
    task_ids: list[str] | None = None,
    all_eligible: bool = False,
    all_gameplay: bool = False,
    global_timeout: int = 3600,
    mode: str = "main",
) -> dict[str, Any]:
    root = root.resolve()
    if timeout <= 0 or global_timeout <= 0:
        raise ValueError("timeout values must be positive")
    if mode not in {"main", "workspace"}:
        raise ValueError("mode must be main or workspace")
    if sum(bool(value) for value in (task_id, task_ids, all_eligible, all_gameplay)) > 1:
        raise ValueError("Use only one task selection mode")
    rows = eligibility(root)["tasks"]
    if task_id is not None:
        wanted = {_canonical_id(task_id)}
        selected = [row for row in rows if row["id"] in wanted and row["eligible"]]
    elif task_ids is not None:
        wanted = {_canonical_id(value) for value in task_ids}
        selected = [row for row in rows if row["id"] in wanted and row["eligible"]]
    elif all_gameplay:
        wanted = {row["id"] for row in rows if row["gameplay"]}
        selected = [row for row in rows if row["id"] in wanted]
    elif all_eligible:
        wanted = {row["id"] for row in rows if row["eligible"]}
        selected = [row for row in rows if row["id"] in wanted]
    else:
        raise ValueError("Select --task-id, --task-ids, --all-eligible, or --all-gameplay")
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
        state = latest(root)
        task_definition_revision = str(state.get("revision") or "")
        if mode == "main" and main_revision(root) != task_definition_revision:
            results = [_unverified(root, row, task_definition_revision, mode, "The scanned revision no longer matches local main") for row in selected]
            manifest = None
            execution_root = None
        else:
            deadline = time.monotonic() + global_timeout
            batch = root / "logs/ci/project-health-knowledge/runtime/batches" / uuid.uuid4().hex
            execution_root = batch / "source"
            manifest = prepare_snapshot(root, execution_root, task_definition_revision, mode, deadline)
            results = []
            for row in selected:
                remaining = int(deadline - time.monotonic())
                if remaining <= CLEANUP_MARGIN_SECONDS:
                    results.append(_unverified(root, row, manifest["source_revision"], mode, "Global runtime verification timeout reached before task start"))
                    continue
                results.append(_run_one(root, execution_root, row, godot_bin, min(timeout, remaining - CLEANUP_MARGIN_SECONDS), manifest["source_revision"], task_definition_revision, mode))
            unchanged = _inputs_unchanged(execution_root, manifest)
            stable_main = main_revision(root) == task_definition_revision and latest(root).get("revision") == task_definition_revision
            for result in results:
                passed = result.get("status") == "passed" and bool(result.get("test_refs")) and unchanged
                result["workspace_verified"] = bool(passed and mode == "workspace")
                result["runtime_verified"] = bool(passed and mode == "main" and stable_main and result.get("source_revision") == task_definition_revision)
                if result.get("status") == "passed" and not (result["workspace_verified"] or result["runtime_verified"]):
                    result["status"] = "runtime_unverified"
                    result["reason"] = "Snapshot inputs, scan or local-main revision changed during runtime verification"
                write_json(root / result["evidence_path"], result)
        output = {
            "schema": "godot-project-health.runtime-index.v2",
            "source_revision": task_definition_revision if mode == "main" else (manifest["source_revision"] if manifest else "workspace"),
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
    parser.add_argument("--all-gameplay", action="store_true")
    parser.add_argument("--mode", choices=("main", "workspace"), default="main")
    parser.add_argument("--eligibility-only", action="store_true")
    args = parser.parse_args(argv)
    if args.eligibility_only or not any((args.task_id, args.task_ids, args.all_eligible, args.all_gameplay)):
        print(json.dumps(eligibility(args.repo_root.resolve()), ensure_ascii=False, indent=2))
        return 0
    godot_bin = args.godot_bin or os.environ.get("GODOT_BIN")
    if not godot_bin:
        raise SystemExit("--godot-bin or GODOT_BIN is required for runtime verification")
    payload = verify(
        args.repo_root, godot_bin, args.timeout_sec, args.task_id,
        args.task_ids.split(",") if args.task_ids else None,
        args.all_eligible, args.all_gameplay, args.global_timeout_sec, args.mode,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
