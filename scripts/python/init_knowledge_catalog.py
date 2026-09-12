#!/usr/bin/env python3
"""Initialize template-safe Knowledge control-plane directories without business data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

COMMON_DOMAINS = ["toolchain", "game-design", "game-runtime", "delivery"]
COMMON_VISIBILITY = ["active", "dependency", "conditional"]
COMMON_LIFECYCLES = ["repository-source"]

DEFAULT_POLICIES = {
    "schema": "godot-project-knowledge.consumer-policies.v2",
    "policy_revision": "godot-project-knowledge-consumer-policies.v2",
    "consumers": {
        "repository-session": {"task_id_required": False, "observe_only": True},
        "chapter4": {"task_id_required": False, "observe_only": True},
        "chapter5": {"task_id_required": True, "observe_only": True},
        "chapter6": {"task_id_required": True, "freeze_before_red": True},
        "review": {"task_id_required": True, "separate_from_chapter6": True},
    },
    "policies": [
        {
            "consumer": "repository-session",
            "domains": COMMON_DOMAINS,
            "visibility": COMMON_VISIBILITY,
            "lifecycles": COMMON_LIFECYCLES,
            "statuses": ["active", "conditional", "historical"],
            "historical_mode": "exact-only",
            "path_prefixes": ["docs/", ".taskmaster/", ".agents/skills/", "Game.Core/Contracts/", "execution-plans/", "decision-logs/"],
            "exact_paths": ["AGENTS.md", "README.md", "workflow.md", "DELIVERY_PROFILE.md"],
            "max_candidates": 24,
            "minimum_confidence": "medium",
            "freeze_point": "session-context-ready",
        },
        {
            "consumer": "chapter4",
            "domains": ["toolchain", "game-design", "game-runtime"],
            "visibility": COMMON_VISIBILITY,
            "lifecycles": COMMON_LIFECYCLES,
            "statuses": ["active", "conditional"],
            "historical_mode": "forbidden",
            "path_prefixes": ["docs/prd/", "docs/gdd/", "docs/adr/", "docs/architecture/", "Game.Core/Contracts/", ".agents/skills/workflow-chapter4-"],
            "exact_paths": ["AGENTS.md", "workflow.md", ".taskmaster/docs/prd.txt"],
            "max_candidates": 24,
            "minimum_confidence": "medium",
            "freeze_point": "before-overlay-write",
        },
        {
            "consumer": "chapter5",
            "domains": COMMON_DOMAINS,
            "visibility": COMMON_VISIBILITY,
            "lifecycles": COMMON_LIFECYCLES,
            "statuses": ["active", "conditional", "historical"],
            "historical_mode": "exact-only",
            "path_prefixes": ["docs/prd/", "docs/gdd/", "docs/adr/", "docs/architecture/", "Game.Core/Contracts/", ".taskmaster/tasks/", "execution-plans/", ".agents/skills/workflow-chapter5-"],
            "exact_paths": ["AGENTS.md", "workflow.md", "docs/testing-framework.md", ".taskmaster/docs/prd.txt"],
            "max_candidates": 28,
            "minimum_confidence": "medium",
            "freeze_point": "before-semantic-stabilization",
        },
        {
            "consumer": "chapter6",
            "domains": COMMON_DOMAINS,
            "visibility": COMMON_VISIBILITY,
            "lifecycles": COMMON_LIFECYCLES,
            "statuses": ["active", "conditional", "historical"],
            "historical_mode": "exact-only",
            "path_prefixes": ["docs/prd/", "docs/gdd/", "docs/adr/", "docs/architecture/", "Game.Core/Contracts/", ".taskmaster/tasks/", "execution-plans/", "decision-logs/", ".agents/skills/workflow-chapter6-"],
            "exact_paths": ["AGENTS.md", "workflow.md", "docs/testing-framework.md", ".taskmaster/docs/prd.txt"],
            "max_candidates": 32,
            "minimum_confidence": "medium",
            "freeze_point": "before-red",
        },
        {
            "consumer": "review",
            "domains": COMMON_DOMAINS,
            "visibility": COMMON_VISIBILITY,
            "lifecycles": COMMON_LIFECYCLES,
            "statuses": ["active", "conditional", "historical"],
            "historical_mode": "exact-only",
            "path_prefixes": ["docs/", "Game.Core/Contracts/", ".taskmaster/tasks/", "execution-plans/", "decision-logs/", ".agents/skills/"],
            "exact_paths": ["AGENTS.md", "README.md", "workflow.md", "DELIVERY_PROFILE.md"],
            "max_candidates": 32,
            "minimum_confidence": "medium",
            "freeze_point": "review-run-input",
        },
    ],
}
DEFAULT_EXCLUSIONS = {
    "schema": "godot-project-knowledge.source-exclusions.v1",
    "rules": [
        {"prefix": ".git/", "reason": "repository internals"},
        {"prefix": ".godot/", "reason": "generated engine state"},
        {"prefix": "logs/", "reason": "run evidence is not repository authority"},
        {"prefix": "knowledge/indexes/generations/", "reason": "generated publication output"},
    ],
}
DEFAULT_SUITE = {
    "schema": "godot-project-knowledge.evaluation-suite.v1",
    "note": "Template-safe empty suite; business repositories add deterministic expectations.",
    "cases": [],
}
FILES = {
    "docs/knowledge/README.md": "# Project Resource Knowledge\n\nThis directory is human-reviewable project resource knowledge. It starts empty in the template. Repository sources remain authoritative.\n",
    "knowledge/policies/consumer-policies.v1.json": json.dumps(DEFAULT_POLICIES, indent=2) + "\n",
    "knowledge/policies/source-exclusions.v1.json": json.dumps(DEFAULT_EXCLUSIONS, indent=2) + "\n",
    "knowledge/evaluation/queries.v1.json": json.dumps(DEFAULT_SUITE, indent=2) + "\n",
}


def initialize(root: Path) -> dict:
    created = []
    for rel, content in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(rel)
    for rel in (
        "docs/knowledge/generated",
        "docs/knowledge/catalogs",
        "docs/knowledge/indexes",
        "docs/knowledge/schema",
        "knowledge/indexes/generations",
        "knowledge/catalogs",
        "knowledge/snapshots",
        "knowledge/projections",
        "knowledge/evaluation",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)
    return {"status": "ok", "created": created, "business_data_seeded": False}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    print(json.dumps(initialize(Path(args.repo_root).resolve()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
