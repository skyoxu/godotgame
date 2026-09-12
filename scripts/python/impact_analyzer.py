#!/usr/bin/env python3
"""Deterministic snapshot-bound impact exploration for the template repository.

The analyzer reports evidence only. Text matches never become confirmed semantic
relationships; the exact scanned target path is the only confirmed target edge.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_health_knowledge import base_dir, latest, snapshot_text


class ImpactAnalyzer:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = base_dir(root)

    def analyze(self, target: str, *, strict: bool = False, limit: int = 100) -> dict[str, Any]:
        needle = str(target or "").strip()
        if not needle:
            raise ValueError("impact target is required")
        state = latest(self.root)
        manifest = state.get("records", [])
        manifest_paths = {str(record.get("path") or "") for record in manifest}
        normalized = needle.replace("\\", "/").removeprefix("./")
        exact_path = normalized if normalized in manifest_paths else None
        tokens = [token.casefold() for token in re.findall(r"[\w_.:/-]+", needle, flags=re.UNICODE) if token.strip()]
        if not tokens:
            tokens = [needle.casefold()]
        evidence: list[dict[str, Any]] = []
        for record in manifest:
            if not record.get("searchable"):
                continue
            rel = str(record.get("path") or "")
            try:
                text = snapshot_text(self.root, rel, state)
            except (ValueError, UnicodeDecodeError):
                continue
            lower = text.casefold()
            count = sum(lower.count(token) for token in tokens)
            if exact_path and rel == exact_path:
                count += 1000
            if count <= 0:
                continue
            line_hits = []
            for idx, line in enumerate(text.splitlines(), 1):
                if any(token in line.casefold() for token in tokens):
                    line_hits.append({"line": idx, "text": line[:500]})
                    if len(line_hits) >= 8:
                        break
            evidence.append({
                "path": rel,
                "score": count,
                "relationship": "target" if exact_path == rel else "text-reference",
                "confirmed": bool(exact_path == rel),
                "hits": line_hits,
            })
        evidence.sort(key=lambda item: (-int(item["score"]), item["path"]))
        if strict and exact_path is None and not evidence:
            raise ValueError("impact target could not be resolved in the scanned snapshot")
        return {
            "schema": "godot-project-impact.report.v2",
            "revision": state.get("revision"),
            "snapshot_mode": state.get("snapshot_mode"),
            "target": needle,
            "mode": "strict" if strict else "explore",
            "warning": "text-reference edges are evidence, not confirmed semantic dependencies",
            "evidence": evidence[:max(1, min(int(limit), 500))],
        }
