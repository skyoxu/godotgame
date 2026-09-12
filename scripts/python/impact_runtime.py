#!/usr/bin/env python3
"""Resolve and traverse revision-bound Impact Index targets."""
from __future__ import annotations

from collections import deque
from pathlib import PurePosixPath
from typing import Any

from impact_analysis_index import ImpactIndexError, load_current_index, normalize_path


def _alias(index: dict[str, Any], target: str) -> str | None:
    folded = target.casefold()
    matches = []
    for item in index.get("aliases", []):
        if not isinstance(item, dict):
            continue
        alias = str(item.get("alias") or item.get("name") or "")
        if alias.casefold() == folded and item.get("target"):
            matches.append(str(item["target"]))
    if len(set(matches)) == 1:
        return matches[0]
    if len(set(matches)) > 1:
        raise ImpactIndexError("underqualified_target", "target alias is ambiguous")
    return None


def resolve_target(index: dict[str, Any], target: str) -> dict[str, Any]:
    raw = str(target or "").strip()
    if not raw:
        raise ImpactIndexError("unsupported_target", "impact target is required")
    alias = _alias(index, raw)
    if alias:
        raw = alias
    files = {item["path"]: item for item in index.get("files", []) if isinstance(item, dict) and item.get("path")}
    normalized = raw.replace("\\", "/").removeprefix("./")
    if normalized in files:
        return {"kind": "file", "id": "file:" + normalized, "path": normalized, "display": normalized}
    symbols = [item for item in index.get("symbols", []) if isinstance(item, dict)]
    exact_id = next((item for item in symbols if item.get("id") == raw), None)
    if exact_id:
        return {"kind": "symbol", "id": exact_id["id"], "path": exact_id["path"], "name": exact_id["name"], "line": exact_id["line"], "display": f"{exact_id['path']}::{exact_id['name']}"}
    if "::" in raw:
        path_part, name = raw.rsplit("::", 1)
        path_part = normalize_path(path_part)
        matches = [item for item in symbols if item.get("path") == path_part and item.get("name") == name]
    else:
        matches = [item for item in symbols if item.get("name") == raw]
    if len(matches) == 1:
        item = matches[0]
        return {"kind":"symbol","id":item["id"],"path":item["path"],"name":item["name"],"line":item["line"],"display":f"{item['path']}::{item['name']}"}
    if len(matches) > 1:
        raise ImpactIndexError("underqualified_target", f"symbol target is ambiguous: {raw}")
    raise ImpactIndexError("unsupported_target", f"target is not an exact indexed file or symbol: {raw}")


def analyze_index(root, target: str, revision: str, *, max_depth: int = 2, include_unconfirmed: bool = True) -> dict[str, Any]:
    index = load_current_index(root, revision)
    resolved = resolve_target(index, target)
    relations = [item for item in index.get("relations", []) if isinstance(item, dict)]
    queue = deque([(resolved["id"], 0)])
    seen = {resolved["id"]}
    evidence: list[dict[str, Any]] = []
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for relation in relations:
            if not include_unconfirmed and not relation.get("confirmed"):
                continue
            direction = None; other = None
            if relation.get("to") == current:
                direction = "inbound"; other = relation.get("from")
            elif relation.get("from") == current:
                direction = "outbound"; other = relation.get("to")
            if not other:
                continue
            row = dict(relation)
            row.update({"direction": direction, "depth": depth + 1, "via": current})
            evidence.append(row)
            if other not in seen:
                seen.add(other); queue.append((str(other), depth + 1))
    return {
        "schema": "godot-project-impact.runtime-analysis.v1",
        "revision": revision,
        "index_id": index.get("index_id"),
        "target": resolved,
        "max_depth": max_depth,
        "evidence": evidence,
        "warning": "text-symbol-reference relations are unconfirmed evidence and never semantic authority",
    }
