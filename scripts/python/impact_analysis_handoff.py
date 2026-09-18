#!/usr/bin/env python3
"""Fail-closed validation for formal frozen-context / Impact handoffs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"[0-9a-f]{40}")
RUN_MANIFEST_SCHEMA = "godot-project-impact.run-manifest.v1"


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("frozen_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def validate(
    frozen: dict[str, Any],
    impact: dict[str, Any],
    *,
    repo_root: str | Path | None = None,
    expected_consumer: str | None = None,
    expected_task_id: str | None = None,
    impact_report_bytes: bytes | None = None,
    run_manifest: dict[str, Any] | None = None,
    impact_report_path: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    revision = str(frozen.get("revision") or "").lower()
    frozen_hash = str(frozen.get("frozen_sha256") or "").lower()
    actual_frozen_hash = _canonical_hash(frozen)

    if frozen.get("schema") != "godot-project-knowledge.frozen-context.v2":
        errors.append("unsupported_frozen_schema")
    if not FULL_SHA.fullmatch(revision):
        errors.append("revision_mismatch")
    if str(impact.get("revision") or "").lower() != revision:
        errors.append("revision_mismatch")
    consumer = str(frozen.get("consumer") or "")
    if consumer not in {"chapter6", "review"}:
        errors.append("unsupported_consumer")
    if expected_consumer and consumer != expected_consumer:
        errors.append("consumer_mismatch")
    if frozen.get("publication_state") != "published-current":
        errors.append("publication_not_current")
    if not frozen_hash or frozen_hash != actual_frozen_hash:
        errors.append("frozen_content_hash_mismatch")
    if impact.get("schema") != "godot-project-impact.report.v3":
        errors.append("unsupported_impact_schema")
    if impact.get("mode") != "strict":
        errors.append("impact_not_strict")
    if str(impact.get("frozen_context_sha256") or "").lower() != actual_frozen_hash:
        errors.append("frozen_hash_mismatch")
    if not impact.get("index_id"):
        errors.append("missing_impact_index")
    if not impact.get("index_path") or not impact.get("index_sha256"):
        errors.append("missing_impact_index_binding")
    if not isinstance(impact.get("resolved_target"), dict):
        errors.append("missing_resolved_target")

    if impact_report_bytes is not None or run_manifest is not None:
        if impact_report_bytes is None or not isinstance(run_manifest, dict):
            errors.append("missing_impact_run_manifest")
        else:
            actual_report_sha = hashlib.sha256(impact_report_bytes).hexdigest()
            if run_manifest.get("schema") != RUN_MANIFEST_SCHEMA:
                errors.append("unsupported_impact_run_manifest")
            if str(run_manifest.get("report_sha256") or "").lower() != actual_report_sha:
                errors.append("impact_report_hash_mismatch")
            if str(run_manifest.get("revision") or "").lower() != revision:
                errors.append("impact_manifest_revision_mismatch")
            if str(run_manifest.get("status") or "") != "ok":
                errors.append("impact_manifest_status_mismatch")
            if impact_report_path is not None:
                expected_path = Path(str(impact_report_path)).as_posix()
                if str(run_manifest.get("report_path") or "") != expected_path:
                    errors.append("impact_manifest_path_mismatch")

    task_id = frozen.get("task_id")
    if consumer == "review":
        if task_id not in {None, ""}:
            errors.append("review_task_must_be_null")
    else:
        if task_id in {None, ""}:
            errors.append("chapter6_task_required")
        if expected_task_id is not None and str(task_id) != str(expected_task_id):
            errors.append("task_mismatch")

    if repo_root is not None and impact.get("index_path"):
        root = Path(repo_root).resolve()
        raw_path = Path(str(impact["index_path"]))
        if raw_path.is_absolute() or ".." in raw_path.parts:
            errors.append("index_path_outside_repository")
        else:
            index_path = (root / raw_path).resolve()
            try:
                index_path.relative_to(root)
            except ValueError:
                errors.append("index_path_outside_repository")
            else:
                if not index_path.is_file():
                    errors.append("missing_index_artifact")
                else:
                    raw = index_path.read_bytes()
                    actual_index_sha = hashlib.sha256(raw).hexdigest()
                    if actual_index_sha != str(impact.get("index_sha256") or "").lower():
                        errors.append("index_hash_mismatch")
                    try:
                        index_doc = json.loads(raw.decode("utf-8"))
                        if index_doc.get("index_id") != impact.get("index_id"):
                            errors.append("index_identity_mismatch")
                        if str(index_doc.get("repository_revision") or "").lower() != revision:
                            errors.append("index_revision_mismatch")
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        errors.append("invalid_index_artifact")

    return {
        "schema": "godot-project-impact.handoff.v3",
        "status": "ok" if not errors else "failed",
        "consumer": consumer,
        "task_id": task_id,
        "revision": revision,
        "frozen_context_sha256": actual_frozen_hash,
        "impact_index_id": impact.get("index_id"),
        "impact_index_sha256": impact.get("index_sha256"),
        "impact_target": impact.get("target"),
        "errors": sorted(set(errors)),
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-context", required=True)
    parser.add_argument("--impact-report", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--consumer")
    parser.add_argument("--task-id")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    frozen_path = Path(args.frozen_context)
    impact_path = Path(args.impact_report)
    if not frozen_path.is_absolute():
        frozen_path = root / frozen_path
    if not impact_path.is_absolute():
        impact_path = root / impact_path
    try:
        frozen_path.resolve().relative_to(root)
        impact_path.resolve().relative_to(root)
    except ValueError:
        print(json.dumps({"schema":"godot-project-impact.handoff.v3","status":"failed","errors":["handoff_path_outside_repository"]}))
        return 2
    try:
        frozen_bytes = frozen_path.read_bytes()
        impact_bytes = impact_path.read_bytes()
        manifest_path = impact_path.with_name("run-manifest.v1.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else None
        report_relative = impact_path.resolve().relative_to(root).as_posix()
        frozen = json.loads(frozen_bytes.decode("utf-8"))
        impact = json.loads(impact_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({
            "schema": "godot-project-impact.handoff.v3",
            "status": "failed",
            "errors": ["invalid_handoff_artifact"],
            "reason": str(exc),
        }))
        return 2
    out = validate(
        frozen,
        impact,
        repo_root=root,
        expected_consumer=args.consumer,
        expected_task_id=args.task_id,
        impact_report_bytes=impact_bytes,
        run_manifest=manifest,
        impact_report_path=report_relative,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
