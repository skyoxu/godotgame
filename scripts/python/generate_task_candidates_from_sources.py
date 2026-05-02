#!/usr/bin/env python3
"""Generate deterministic task candidates from requirement anchors.

The output is intentionally conservative. An LLM may later rewrite candidate text,
but coverage and final triplet compilation should consume this normalized schema.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

OWNER_BY_KIND = {
    "gdd": "gameplay",
    "prd": "product",
    "overlay": "architecture",
    "adr": "architecture",
    "acceptance": "qa",
}
LAYER_BY_KIND = {
    "gdd": "feature",
    "prd": "feature",
    "overlay": "architecture",
    "adr": "architecture",
    "acceptance": "test",
}


def slug_words(text: str, limit: int = 7) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "-".join(words[:limit]) or "requirement"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def group_key(anchor: dict[str, Any]) -> str:
    source = str(anchor.get("source_path", ""))
    kind = str(anchor.get("kind", "requirement"))
    # Keep acceptance items near their source document but prevent one task per line.
    stem = source.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return f"{kind}:{stem}"


def task_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index:04d}"


def build_candidates(index: dict[str, Any], mode: str, id_prefix: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for anchor in index.get("anchors", []):
        grouped[group_key(anchor)].append(anchor)
    candidates: list[dict[str, Any]] = []
    for idx, (_key, anchors) in enumerate(sorted(grouped.items()), 1):
        priorities = [str(a.get("priority", "P2")) for a in anchors]
        priority = "P0" if "P0" in priorities else "P1" if "P1" in priorities else "P2" if "P2" in priorities else "P3"
        first = anchors[0]
        kind = str(first.get("kind", "requirement"))
        title_seed = str(first.get("text", "Requirement task"))
        labels = sorted({kind, "generated", mode} | {str(a.get("kind", "requirement")) for a in anchors})
        refs = sorted({ref for a in anchors for ref in a.get("refs", []) if isinstance(ref, str)})
        source_refs = [f"{a.get('source_path')}:{a.get('line')}" for a in anchors]
        requirement_ids = [str(a.get("requirement_id")) for a in anchors]
        candidates.append({
            "id": task_id(id_prefix, idx),
            "title": f"Implement {slug_words(title_seed).replace('-', ' ')}",
            "description": title_seed[:500],
            "status": "pending",
            "priority": priority,
            "layer": LAYER_BY_KIND.get(kind, "feature"),
            "depends_on": [],
            "adr_refs": [r for r in refs if r.startswith("ADR-")],
            "chapter_refs": [],
            "overlay_refs": [r for r in refs if r.startswith("docs/architecture/overlays/")],
            "labels": labels,
            "owner": OWNER_BY_KIND.get(kind, "implementation"),
            "test_refs": [r for r in refs if r.startswith("Game.") or r.startswith("Tests.") or r.endswith(".cs") or r.endswith(".gd")],
            "acceptance": [f"Cover requirement {rid}. Source: {src}" for rid, src in zip(requirement_ids[:8], source_refs[:8])],
            "test_strategy": ["Add or update deterministic tests for the covered requirements before marking the task done."],
            "source_refs": source_refs,
            "requirement_ids": requirement_ids,
            "generation_mode": mode,
        })
    return {
        "schema": "task-generation.candidates.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": mode,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate task candidates from a requirements index.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--requirements", default="logs/ci/task-generation/requirements.index.json")
    parser.add_argument("--mode", choices=["init", "add"], default="init")
    parser.add_argument("--id-prefix", default="GEN")
    parser.add_argument("--out", default="logs/ci/task-generation/task-candidates.normalized.json")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    data = build_candidates(load_json(root / args.requirements), args.mode, args.id_prefix)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"task_candidates={out} candidates={data['candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

