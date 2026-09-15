#!/usr/bin/env python3
"""CLI for deterministic Impact exploration or formal strict analysis.

When an output path is requested, report + run-manifest publication is guarded by
one directory writer lock. Collision diagnostics are written to an isolated run
directory first so a losing concurrent writer never races the winning writer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from impact_analysis_index import ImpactIndexError
from impact_analyzer import ImpactAnalyzer

RUN_MANIFEST_SCHEMA = "godot-project-impact.run-manifest.v1"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temp.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def _manifest_for(output: Path, report: dict[str, Any], root: Path, run_id: str) -> dict[str, Any]:
    data = _json_bytes(report)
    try:
        report_path = output.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        report_path = str(output.resolve())
    return {
        "schema": RUN_MANIFEST_SCHEMA,
        "run_id": run_id,
        "report_path": report_path,
        "report_sha256": hashlib.sha256(data).hexdigest(),
        "status": report.get("status", "ok"),
        "revision": report.get("revision"),
    }


def _publish_pair(root: Path, output: Path, report: dict[str, Any], run_id: str) -> dict[str, Any]:
    """Publish one report/manifest pair under an exclusive directory writer lock."""
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = output.with_name("run-manifest.v1.json")
    lock = output.parent / ".impact-report-publish.lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise ImpactIndexError("index_identity_collision", "another writer owns the output directory") from exc

    report_data = _json_bytes(report)
    manifest = _manifest_for(output, report, root, run_id)
    manifest_data = _json_bytes(manifest)
    report_written = False
    try:
        if output.exists() or manifest_path.exists():
            raise ImpactIndexError("index_identity_collision", "output report or run manifest already exists")
        _atomic_write(output, report_data)
        report_written = True
        _atomic_write(manifest_path, manifest_data)
    except Exception:
        if report_written:
            try:
                if output.read_bytes() == report_data:
                    output.unlink()
            except OSError:
                pass
        raise
    finally:
        try:
            lock.rmdir()
        except OSError:
            pass
    return manifest


def _as_impact_error(exc: Exception) -> ImpactIndexError:
    if isinstance(exc, ImpactIndexError):
        return exc
    text = str(exc)
    if ": " in text:
        code, reason = text.split(": ", 1)
        if code and code.replace("_", "").isalnum():
            return ImpactIndexError(code, reason)
    return ImpactIndexError("internal_error", text or exc.__class__.__name__)


def _failure_report(target: str, revision: str | None, reason: ImpactIndexError) -> dict[str, Any]:
    return {
        "schema": "godot-project-impact.failure-report.v1",
        "status": reason.code,
        "revision": revision,
        "target": target,
        "failure_reason": {"code": reason.code, "reason": reason.reason},
    }


def _failure_evidence(root: Path, output: Path | None, run_id: str, target: str, revision: str | None, reason: ImpactIndexError) -> dict[str, Any]:
    isolated = root / "logs" / "ci" / datetime.now(timezone.utc).date().isoformat() / "impact-analysis" / f"failed-{run_id}" / "impact-report.v1.json"
    concurrent_collision = reason.code in {"lock_unavailable", "index_identity_collision"} and (
        reason.code == "lock_unavailable" or any(marker in reason.reason for marker in (
            "another writer owns the output directory",
            "output report or run manifest already exists",
        ))
    )
    if concurrent_collision:
        candidates = [isolated, output] if output is not None and output.resolve() != isolated.resolve() else [isolated]
    else:
        candidates = [output, isolated] if output is not None and output.resolve() != isolated.resolve() else [isolated]
    errors: list[str] = []
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            report = _failure_report(target, revision, reason)
            manifest = _publish_pair(root, candidate, report, run_id)
            return {"evidence_saved": True, "report_path": manifest["report_path"], "report_sha256": manifest["report_sha256"]}
        except Exception as exc:
            errors.append(str(exc))
    return {"evidence_saved": False, "evidence_error": "; ".join(errors)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target", required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--frozen-context")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    run_id = uuid.uuid4().hex
    output = Path(args.output) if args.output else None
    if output is not None and not output.is_absolute():
        output = root / output
    frozen_hash = None
    revision: str | None = None
    try:
        if args.strict:
            if not args.frozen_context:
                parser.error("--strict formal analysis requires --frozen-context")
            frozen = json.loads(Path(args.frozen_context).read_text(encoding="utf-8"))
            frozen_hash = str(frozen.get("frozen_sha256") or "").strip()
            if not frozen_hash:
                raise ImpactIndexError("invalid_kcp_binding", "frozen context hash is missing")
        out = ImpactAnalyzer(root).analyze(args.target, strict=args.strict, frozen_context_sha256=frozen_hash)
        revision = str(out.get("revision") or "") or None
        if args.strict:
            frozen = json.loads(Path(args.frozen_context).read_text(encoding="utf-8"))
            if frozen.get("revision") != out.get("revision"):
                raise ImpactIndexError("revision_mismatch", "frozen context revision does not match Impact index/report revision")
        out = {**out, "status": "ok"}
        if output is not None:
            _publish_pair(root, output, out, run_id)
        else:
            print(_json_bytes(out).decode("utf-8"), end="")
        return 0
    except SystemExit:
        raise
    except Exception as exc:
        reason = _as_impact_error(exc)
        evidence = _failure_evidence(root, output, run_id, str(args.target), revision, reason)
        print(json.dumps({"status": reason.code, "reason": reason.reason, **evidence}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
