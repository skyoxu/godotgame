#!/usr/bin/env python3
"""Validate revision and frozen-context lineage for an Impact handoff."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def validate(frozen: dict, impact: dict) -> dict:
    errors=[]
    if frozen.get("revision")!=impact.get("revision"): errors.append("revision_mismatch")
    if frozen.get("consumer") not in {"chapter6","review"}: errors.append("unsupported_consumer")
    if not frozen.get("frozen_sha256"): errors.append("missing_frozen_hash")
    return {"schema":"godot-project-impact.handoff.v1","status":"ok" if not errors else "failed","consumer":frozen.get("consumer"),"revision":frozen.get("revision"),"frozen_context_sha256":frozen.get("frozen_sha256"),"impact_target":impact.get("target"),"errors":errors}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--frozen-context",required=True); p.add_argument("--impact-report",required=True); a=p.parse_args(argv)
    out=validate(json.loads(Path(a.frozen_context).read_text(encoding="utf-8")),json.loads(Path(a.impact_report).read_text(encoding="utf-8"))); print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if out["status"]=="ok" else 2
if __name__=="__main__": raise SystemExit(main())
