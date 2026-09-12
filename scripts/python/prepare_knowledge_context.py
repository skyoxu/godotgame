#!/usr/bin/env python3
"""Prepare consumer-scoped Knowledge context candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from knowledge_locator import locate

FORMAL_PUBLISHED_CONSUMERS = {"chapter6", "review"}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def prepare(root, consumer, text, task_id=None, *, require_published: bool | None = None):
    formal = consumer in FORMAL_PUBLISHED_CONSUMERS if require_published is None else bool(require_published)
    located = locate(root, consumer=consumer, text=text, task_id=task_id, require_published=formal)
    status = located.get("status")
    payload = {
        "schema": "godot-project-knowledge.context-candidates.v2",
        "consumer": consumer,
        "task_id": task_id,
        "revision": located.get("revision"),
        "policy_revision": located.get("policy_revision"),
        "publication_state": located.get("publication_state"),
        "query": text,
        "status": "ready" if status in {"matched", "insufficient_match"} else "fallback_required",
        "locator_status": status,
        "candidates": located.get("candidates", []),
        "observe_only": True,
        "semantic_decision_required": True,
        "freeze_state": "unfrozen",
    }
    if payload["status"] != "ready":
        payload["fallback"] = {
            "required": True,
            "reason": located.get("reason") or "knowledge_locator_unavailable",
            "authority_route": "direct repository authorities",
        }
    payload["bundle_sha256"] = hashlib.sha256(canonical(payload)).hexdigest()
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--consumer", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--output")
    parser.add_argument("--allow-unpublished", action="store_true")
    args = parser.parse_args(argv)
    require_published = False if args.allow_unpublished else None
    data = prepare(args.repository_root, args.consumer, args.query, args.task_id, require_published=require_published)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 2 if data.get("status") == "fallback_required" else 0


if __name__ == "__main__": raise SystemExit(main())
