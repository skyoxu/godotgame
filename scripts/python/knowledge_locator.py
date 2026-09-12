#!/usr/bin/env python3
"""Deterministic, template-safe repository knowledge locator."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from project_health_knowledge import query, revision

CONSUMERS = {"repository-session", "chapter4", "chapter5", "chapter6", "review"}

def locate(root: str | Path, *, consumer: str, text: str, task_id: str | None = None) -> dict:
    if consumer not in CONSUMERS:
        raise ValueError(f"unknown consumer: {consumer}")
    result = query(root, text)
    return {
        "schema": "godot-project-knowledge.locator.v1",
        "consumer": consumer,
        "task_id": task_id,
        "revision": revision(Path(root).resolve()),
        "query": text,
        "candidates": [
            {"path": item["path"], "score": item["score"], "line": item["line"], "snippet": item.get("snippet", ""), "semantic_satisfaction": "undecided"}
            for item in result.get("results", [])
        ],
    }

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repository-root",default="."); p.add_argument("--consumer",default="repository-session",choices=sorted(CONSUMERS)); p.add_argument("--query"); p.add_argument("--task-id")
    a=p.parse_args(argv)
    text=a.query
    if text is None:
        request=json.load(__import__("sys").stdin); text=str(request.get("query") or request.get("text") or ""); a.consumer=str(request.get("consumer") or a.consumer); a.task_id=request.get("task_id")
    print(json.dumps(locate(a.repository_root,consumer=a.consumer,text=text,task_id=a.task_id),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
