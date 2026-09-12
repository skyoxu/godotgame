#!/usr/bin/env python3
"""Freeze an explicit Knowledge candidate decision set into bounded context."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def freeze(bundle: dict, decisions: dict) -> dict:
    if bundle.get("schema") not in {"godot-project-knowledge.context-candidates.v1", "godot-project-knowledge.context-candidates.v2"}:
        raise ValueError("unsupported candidate bundle")
    if bundle.get("schema") == "godot-project-knowledge.context-candidates.v2" and bundle.get("status") != "ready":
        raise ValueError("candidate bundle is not ready for freeze")
    if bundle.get("consumer") in {"chapter6", "review"} and bundle.get("schema") == "godot-project-knowledge.context-candidates.v2" and bundle.get("publication_state") != "published-current":
        raise ValueError("formal Chapter 6 / Review freeze requires published-current Knowledge")
    by_path = {candidate["path"]: candidate for candidate in bundle.get("candidates", [])}
    rows = []
    for item in decisions.get("decisions", []):
        path = str(item.get("path") or "")
        accepted = bool(item.get("accepted"))
        reason = str(item.get("reason") or "").strip()
        satisfies = str(item.get("satisfies") or "").strip()
        if path not in by_path:
            raise ValueError(f"decision path is not a candidate: {path}")
        if not reason:
            raise ValueError(f"decision reason required: {path}")
        rows.append({"path": path, "accepted": accepted, "reason": reason, "satisfies": satisfies, "source": by_path[path]})
    if not rows:
        raise ValueError("at least one explicit candidate decision is required")
    out = {
        "schema": "godot-project-knowledge.frozen-context.v2",
        "consumer": bundle.get("consumer"),
        "task_id": bundle.get("task_id"),
        "revision": bundle.get("revision"),
        "policy_revision": bundle.get("policy_revision"),
        "publication_state": bundle.get("publication_state"),
        "candidate_bundle_sha256": bundle.get("bundle_sha256") or sha(bundle),
        "decisions": rows,
        "accepted_paths": [row["path"] for row in rows if row["accepted"]],
    }
    out["frozen_sha256"] = sha(out)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    out = freeze(bundle, decisions)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "output": args.output, "frozen_sha256": out["frozen_sha256"]}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
