#!/usr/bin/env python3
"""Validate template Knowledge control-plane contracts and generated publication state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from publish_knowledge_catalog import PublicationBlocked, check_current

REQUIRED_CONTRACTS = (
    "knowledge/contracts/knowledge-context-candidates.v2.schema.json",
    "knowledge/contracts/knowledge-frozen-context.v2.schema.json",
    "knowledge/contracts/knowledge-index-pointer.v1.schema.json",
    "knowledge/contracts/knowledge-publication-generation.v1.schema.json",
    "knowledge/contracts/knowledge-locator-result.v3.schema.json",
    "knowledge/contracts/knowledge-consumption-decision-set.v2.schema.json",
)
REQUIRED_RESOURCE_SCHEMAS = (
    "docs/knowledge/schema/task-resource-links.v2.schema.json",
    "docs/knowledge/schema/task-semantic.v1.schema.json",
)


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate(root: Path, *, require_generated: bool = False) -> dict:
    issues: list[str] = []
    for relative in (*REQUIRED_CONTRACTS, *REQUIRED_RESOURCE_SCHEMAS):
        path = root / relative
        if not path.is_file():
            issues.append(f"missing:{relative}")
            continue
        try:
            schema = _json(path)
        except Exception as exc:
            issues.append(f"invalid-json:{relative}:{exc}")
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or not schema.get("$id"):
            issues.append(f"invalid-schema-header:{relative}")
    policy = root / "knowledge/policies/consumer-policies.v1.json"
    evaluation = root / "knowledge/evaluation/queries.v1.json"
    for path in (policy, evaluation):
        if not path.is_file():
            issues.append(f"missing:{path.relative_to(root).as_posix()}")
    if not issues:
        policies = _json(policy)
        consumers = {item.get("consumer") for item in policies.get("policies", []) if isinstance(item, dict)}
        expected = {"repository-session", "chapter4", "chapter5", "chapter6", "review"}
        if consumers != expected:
            issues.append(f"consumer-policy-set-mismatch:{sorted(consumers)}")
        suite = _json(evaluation)
        if suite.get("schema") != "godot-project-knowledge.evaluation-suite.v1" or not isinstance(suite.get("cases"), list):
            issues.append("evaluation-suite-invalid")
    publication = None
    if require_generated:
        try:
            publication = check_current(root)
        except PublicationBlocked as exc:
            issues.append(f"publication:{exc.reason}")
        except Exception as exc:
            issues.append(f"publication:invalid:{exc}")
    return {
        "schema": "godot-project-knowledge.control-plane-validation.v1",
        "status": "ok" if not issues else "failed",
        "require_generated": require_generated,
        "publication": publication,
        "issues": issues,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-generated", action="store_true")
    args = parser.parse_args(argv)
    result = validate(args.repository_root.resolve(), require_generated=args.require_generated)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__": raise SystemExit(main())
