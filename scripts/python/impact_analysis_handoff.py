#!/usr/bin/env python3
"""Validate revision and frozen-context lineage for a formal Impact handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(frozen: dict, impact: dict) -> dict:
    errors = []
    frozen_hash = frozen.get("frozen_sha256")
    if frozen.get("revision") != impact.get("revision"):
        errors.append("revision_mismatch")
    if frozen.get("consumer") not in {"chapter6", "review"}:
        errors.append("unsupported_consumer")
    if not frozen_hash:
        errors.append("missing_frozen_hash")
    if impact.get("mode") != "strict":
        errors.append("impact_not_strict")
    if impact.get("frozen_context_sha256") != frozen_hash:
        errors.append("frozen_hash_mismatch")
    if not impact.get("index_id"):
        errors.append("missing_impact_index")
    return {
        "schema": "godot-project-impact.handoff.v2",
        "status": "ok" if not errors else "failed",
        "consumer": frozen.get("consumer"),
        "revision": frozen.get("revision"),
        "frozen_context_sha256": frozen_hash,
        "impact_index_id": impact.get("index_id"),
        "impact_target": impact.get("target"),
        "errors": errors,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-context", required=True)
    parser.add_argument("--impact-report", required=True)
    args = parser.parse_args(argv)
    out = validate(
        json.loads(Path(args.frozen_context).read_text(encoding="utf-8")),
        json.loads(Path(args.impact_report).read_text(encoding="utf-8")),
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["status"] == "ok" else 2


if __name__ == "__main__": raise SystemExit(main())
