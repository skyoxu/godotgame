#!/usr/bin/env python3
"""Shared helpers for Chapter 3 UI/UX seed metadata."""

from __future__ import annotations

import re
from typing import Any

UI_UX_SEED_POLICY_REF = "docs/workflows/ui-ux-implementation-policy.md"
UI_UX_SEED_LABELS = {
    "ui-ux-seed",
    "chapter3-ui-intent",
    "chapter7-input",
    "planning-metadata",
    "not-chapter6-runnable",
}


def _excerpt_score(text: str) -> tuple[int, int]:
    stripped = str(text or "").strip()
    if not stripped:
        return (0, 0)
    if "\n" not in stripped and re.match(r"^#{1,6}\s+\S", stripped):
        return (1, len(stripped))
    if "|" in stripped:
        return (4, len(stripped))
    if stripped.startswith(("- ", "* ")):
        return (3, len(stripped))
    return (2, len(stripped))


def build_ui_ux_seed(anchors: list[dict[str, Any]]) -> dict[str, Any]:
    categories: list[str] = []
    source_refs: list[str] = []
    excerpts: dict[str, str] = {}
    for anchor in anchors:
        category = str(anchor.get("ui_ux_category") or "").strip()
        if not category:
            continue
        if category not in categories:
            categories.append(category)
        source_ref = f"{anchor.get('source_path')}:{anchor.get('line')}"
        if source_ref not in source_refs:
            source_refs.append(source_ref)
        excerpt = str(anchor.get("text") or "")[:500]
        if category not in excerpts or _excerpt_score(excerpt) > _excerpt_score(excerpts[category]):
            excerpts[category] = excerpt
    if not categories:
        return {}
    return {
        "required": True,
        "policy_ref": UI_UX_SEED_POLICY_REF,
        "categories": categories,
        "source_refs": source_refs,
        "excerpts": excerpts,
    }
