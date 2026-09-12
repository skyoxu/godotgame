#!/usr/bin/env python3
"""Deterministic, template-safe repository knowledge locator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_health_knowledge import latest, query

CONSUMERS = {"repository-session", "chapter4", "chapter5", "chapter6", "review"}


def locate(root: str | Path, *, consumer: str, text: str, task_id: str | None = None) -> dict:
    if consumer not in CONSUMERS:
        raise ValueError(f"unknown consumer: {consumer}")
    repo = Path(root).resolve()
    result = query(repo, text)
    return {
        "schema": "godot-project-knowledge.locator.v2",
        "consumer": consumer,
        "task_id": task_id,
        "revision": latest(repo).get("revision"),
        "query": text,
        "candidates": [
            {
                "path": item["path"],
                "score": item["score"],
                "line": item["line"],
                "snippet": item.get("snippet", ""),
                "semantic_satisfaction": "undecided",
            }
            for item in result.get("results", [])
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--consumer", default="repository-session", choices=sorted(CONSUMERS))
    parser.add_argument("--query")
    parser.add_argument("--task-id")
    args = parser.parse_args(argv)
    text = args.query
    if text is None:
        request = json.load(__import__("sys").stdin)
        text = str(request.get("query") or request.get("text") or "")
        args.consumer = str(request.get("consumer") or args.consumer)
        args.task_id = request.get("task_id")
    print(json.dumps(locate(args.repository_root, consumer=args.consumer, text=text, task_id=args.task_id), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
