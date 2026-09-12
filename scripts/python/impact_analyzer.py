#!/usr/bin/env python3
"""Deterministic revision-bound Impact exploration and strict analysis."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from impact_analysis_index import ImpactIndexError
from impact_runtime import analyze_index
from project_health_knowledge import base_dir, latest, snapshot_text


class ImpactAnalyzer:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = base_dir(root)

    def _explore(self, needle: str, limit: int) -> dict[str, Any]:
        state = latest(self.root)
        manifest = state.get("records", [])
        manifest_paths = {str(record.get("path") or "") for record in manifest}
        normalized = needle.replace("\\", "/").removeprefix("./")
        exact_path = normalized if normalized in manifest_paths else None
        tokens = [token.casefold() for token in re.findall(r"[\w_.:/-]+", needle, flags=re.UNICODE) if token.strip()] or [needle.casefold()]
        evidence: list[dict[str, Any]] = []
        omissions: list[dict[str, str]] = []
        for record in manifest:
            if not record.get("searchable"):
                continue
            rel = str(record.get("path") or "")
            try:
                text = snapshot_text(self.root, rel, state)
            except (ValueError, UnicodeDecodeError) as exc:
                omissions.append({"path": rel, "reason": str(exc)})
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
            evidence.append({"path": rel, "score": count, "relationship": "target" if exact_path == rel else "text-reference", "confirmed": bool(exact_path == rel), "hits": line_hits})
        evidence.sort(key=lambda item: (-int(item["score"]), item["path"]))
        return {
            "schema": "godot-project-impact.report.v3", "revision": state.get("revision"),
            "snapshot_mode": state.get("snapshot_mode"), "target": needle, "mode": "explore",
            "warning": "text-reference edges are evidence, not confirmed semantic dependencies",
            "evidence": evidence[:max(1, min(int(limit), 500))], "omissions": omissions,
        }

    def analyze(self, target: str, *, strict: bool = False, limit: int = 100, frozen_context_sha256: str | None = None) -> dict[str, Any]:
        needle = str(target or "").strip()
        if not needle:
            raise ValueError("impact target is required")
        state = latest(self.root)
        revision = str(state.get("revision") or "")
        if not strict:
            return self._explore(needle, limit)
        try:
            indexed = analyze_index(self.root, needle, revision, max_depth=2, include_unconfirmed=True)
        except ImpactIndexError as exc:
            raise ValueError(f"{exc.code}: {exc.reason}") from exc
        evidence = []
        for relation in indexed.get("evidence", [])[:max(1, min(int(limit), 500))]:
            evidence.append({
                "relationship": relation.get("type"), "confirmed": bool(relation.get("confirmed")),
                "direction": relation.get("direction"), "depth": relation.get("depth"),
                "from": relation.get("from"), "to": relation.get("to"), "line": relation.get("line"),
            })
        return {
            "schema": "godot-project-impact.report.v3", "revision": revision,
            "snapshot_mode": state.get("snapshot_mode"), "index_id": indexed.get("index_id"),
            "target": needle, "resolved_target": indexed.get("target"), "mode": "strict",
            "frozen_context_sha256": frozen_context_sha256,
            "warning": indexed.get("warning"), "evidence": evidence, "omissions": [],
        }
