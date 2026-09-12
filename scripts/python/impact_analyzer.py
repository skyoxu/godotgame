#!/usr/bin/env python3
"""Deterministic repository impact exploration for the template repository.

The analyzer intentionally reports evidence only. It never upgrades keyword matches
into confirmed symbol relationships.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_health_knowledge import base_dir, latest, safe_file, revision


class ImpactAnalyzer:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = base_dir(root)

    def analyze(self, target: str, *, strict: bool = False, limit: int = 100) -> dict[str, Any]:
        needle = str(target or "").strip()
        if not needle:
            raise ValueError("impact target is required")
        manifest = latest(self.root).get("records", [])
        exact_path = None
        try:
            candidate = safe_file(self.root, needle)
            if candidate.is_file():
                exact_path = candidate.relative_to(self.root).as_posix()
        except ValueError:
            pass

        tokens = [t.lower() for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.:/-]*", needle)]
        if not tokens:
            tokens = [needle.lower()]
        evidence: list[dict[str, Any]] = []
        for record in manifest:
            rel = str(record.get("path") or "")
            path = safe_file(self.root, rel)
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError):
                continue
            lower = text.lower()
            count = sum(lower.count(token) for token in tokens)
            if exact_path and rel == exact_path:
                count += 1000
            if count <= 0:
                continue
            line_hits = []
            for idx, line in enumerate(text.splitlines(), 1):
                if any(token in line.lower() for token in tokens):
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
            raise ValueError("impact target could not be resolved")
        return {
            "schema": "godot-project-impact.report.v1",
            "revision": revision(self.root),
            "target": needle,
            "mode": "strict" if strict else "explore",
            "warning": "text-reference edges are evidence, not confirmed semantic dependencies",
            "evidence": evidence[:max(1, min(int(limit), 500))],
        }
