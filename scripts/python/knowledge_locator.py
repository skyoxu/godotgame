#!/usr/bin/env python3
"""Policy-aware repository Knowledge locator with publication/freshness metadata."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _knowledge_catalog_builder import GitSnapshot, build_layers
from _knowledge_locator_core import locate as locate_core
from project_health_knowledge import latest

CONSUMERS = {"repository-session", "chapter4", "chapter5", "chapter6", "review"}
POLICY_PATH = Path("knowledge/policies/consumer-policies.v1.json")
EXCLUSIONS_PATH = Path("knowledge/policies/source-exclusions.v1.json")
CATALOG_PATH = Path("knowledge/catalogs/repository-knowledge-catalog.v1.json")
PROJECTIONS_PATH = Path("knowledge/projections/consumer-projections.v1.json")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _published_layers(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None:
    try:
        from publish_knowledge_catalog import check_current
        check_current(root)
        return _load(root / CATALOG_PATH), _load(root / PROJECTIONS_PATH), _load(root / POLICY_PATH)
    except Exception:
        return None


def _ephemeral_layers(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    policies = _load(root / POLICY_PATH)
    exclusions = _load(root / EXCLUSIONS_PATH)
    snapshot = latest(root)
    revision = str(snapshot.get("revision") or "").strip()
    if snapshot.get("snapshot_mode") == "main" and revision:
        # Bind ephemeral candidates to the exact Project Health scan revision.
        # Local main may have advanced after the scan; mixing those revisions would
        # make browser evidence internally inconsistent.
        _, catalog, projections = build_layers(GitSnapshot(root, revision), exclusions, policies)
        return catalog, projections, policies
    # Non-Git fixtures keep the existing bounded text-query fallback in project_health_knowledge.
    from project_health_knowledge import query
    return {"fallback_query": query}, {}, policies


def locate(root: str | Path, *, consumer: str, text: str, task_id: str | None = None, require_published: bool = False) -> dict[str, Any]:
    if consumer not in CONSUMERS:
        raise ValueError(f"unknown consumer: {consumer}")
    repo = Path(root).resolve()
    published = _published_layers(repo)
    publication_state = "published-current" if published else "ephemeral"
    if require_published and not published:
        return {
            "schema": "godot-project-knowledge.locator.v3", "status": "blocked",
            "reason": "published_knowledge_required", "consumer": consumer, "task_id": task_id,
            "revision": latest(repo).get("revision"), "query": text, "publication_state": publication_state,
            "candidates": [],
        }
    catalog, projections, policies = published or _ephemeral_layers(repo)
    if "fallback_query" in catalog:
        result = catalog["fallback_query"](repo, text)
        candidates = [{
            "path": item["path"], "score": item["score"], "line": item["line"],
            "line_start": item["line"], "line_end": item["line"], "snippet": item.get("snippet", ""),
            "semantic_satisfaction": "undecided", "rank_evidence": {"strategy": "directory-fallback", "confidence": "medium"},
        } for item in result.get("results", [])]
        return {
            "schema": "godot-project-knowledge.locator.v3", "status": "matched" if candidates else "insufficient_match",
            "consumer": consumer, "task_id": task_id, "revision": latest(repo).get("revision"), "query": text,
            "publication_state": publication_state, "candidates": candidates,
        }
    policy = next((item for item in policies.get("policies", []) if item.get("consumer") == consumer), None)
    projection = next((item for item in projections.get("projections", []) if item.get("consumer") == consumer), None)
    if not policy or not projection:
        return {"schema":"godot-project-knowledge.locator.v3","status":"blocked","reason":"consumer_policy_or_projection_missing","consumer":consumer,"task_id":task_id,"revision":catalog.get("source_snapshot",{}).get("commit"),"query":text,"publication_state":publication_state,"candidates":[]}
    maximum = int(policy.get("max_candidates", 12))
    core = locate_core({"query": text}, catalog, policy, set(projection.get("eligible_module_ids", [])), maximum)
    candidates = []
    for item in core.get("candidates", []):
        row = dict(item); row["semantic_satisfaction"] = "undecided"; candidates.append(row)
    return {
        "schema": "godot-project-knowledge.locator.v3", "status": core.get("status"),
        "consumer": consumer, "task_id": task_id, "revision": catalog.get("source_snapshot", {}).get("commit"),
        "query": text, "publication_state": publication_state, "policy_revision": policies.get("policy_revision"),
        "candidates": candidates,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--consumer", default="repository-session", choices=sorted(CONSUMERS))
    parser.add_argument("--query")
    parser.add_argument("--task-id")
    parser.add_argument("--require-published", action="store_true")
    args = parser.parse_args(argv)
    text = args.query
    if text is None:
        request = json.load(__import__("sys").stdin)
        text = str(request.get("query") or request.get("text") or "")
        args.consumer = str(request.get("consumer") or args.consumer)
        args.task_id = request.get("task_id")
        args.require_published = bool(request.get("require_published", args.require_published))
    print(json.dumps(locate(args.repository_root, consumer=args.consumer, text=text, task_id=args.task_id, require_published=args.require_published), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
