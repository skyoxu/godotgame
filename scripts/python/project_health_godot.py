#!/usr/bin/env python3
"""Template-safe static Godot navigation for Project Health.

This module does not infer business semantics. It validates configured task-scene
bindings against files that actually exist, then extracts inspectable scene/node/
script evidence from Godot text resources.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_health_knowledge import safe_file

EXT_RESOURCE_RE = re.compile(r'^\[ext_resource\s+type="(?P<type>[^"]+)"\s+path="(?P<path>[^"]+)"\s+id="(?P<id>[^"]+)"\]$', re.MULTILINE)
NODE_RE = re.compile(r'^\[node\s+name="(?P<name>[^"]+)"(?:\s+type="(?P<type>[^"]+)")?(?:\s+parent="(?P<parent>[^"]+)")?.*\]$', re.MULTILINE)
SCRIPT_ASSIGN_RE = re.compile(r'^script\s*=\s*ExtResource\("(?P<id>[^"]+)"\)', re.MULTILINE)


def _repo_path(root: Path, value: str) -> tuple[str, Path] | None:
    value = value.strip().replace("res://", "")
    if not value:
        return None
    path = safe_file(root, value)
    return value.replace("\\", "/"), path


def inspect_scene(root: Path, scene: str) -> dict[str, Any]:
    located = _repo_path(root.resolve(), scene)
    if located is None:
        return {"scene": scene, "exists": False, "nodes": [], "scripts": [], "resources": []}
    rel, path = located
    if not path.is_file():
        return {"scene": rel, "exists": False, "nodes": [], "scripts": [], "resources": []}
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    resources = [{"type": m.group("type"), "path": m.group("path").replace("res://", ""), "id": m.group("id")} for m in EXT_RESOURCE_RE.finditer(text)]
    resource_by_id = {item["id"]: item for item in resources}
    nodes = []
    for match in NODE_RE.finditer(text):
        name = match.group("name")
        parent = match.group("parent") or ""
        node_path = name if not parent or parent == "." else f"{parent}/{name}"
        nodes.append({"name": name, "node_path": node_path, "type": match.group("type") or ""})
    script_ids = list(dict.fromkeys(match.group("id") for match in SCRIPT_ASSIGN_RE.finditer(text)))
    scripts = [resource_by_id[value]["path"] for value in script_ids if value in resource_by_id and resource_by_id[value]["type"].casefold() == "script"]
    return {"scene": rel, "exists": True, "nodes": nodes, "scripts": scripts, "resources": resources}


def _values(binding: dict[str, Any], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        value = binding.get(key)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
        elif isinstance(value, list):
            values.extend(str(item).strip() for item in value if isinstance(item, str) and item.strip())
    return list(dict.fromkeys(values))


def task_navigation(root: Path, task_id: str, bindings: list[dict[str, Any]]) -> dict[str, Any]:
    root = root.resolve()
    matched = [item for item in bindings if str(item.get("task_id", item.get("taskmaster_id", ""))).strip() == str(task_id).strip()]
    scene_paths: list[str] = []
    declared_nodes: list[str] = []
    declared_scripts: list[str] = []
    witnesses: list[str] = []
    configs: list[dict[str, Any]] = []
    for binding in matched:
        scene_paths.extend(_values(binding, "scene", "scenes"))
        declared_nodes.extend(_values(binding, "node", "node_path", "nodes"))
        declared_scripts.extend(_values(binding, "script", "scripts"))
        witnesses.extend(_values(binding, "witness", "witnesses", "code_witnesses"))
        raw_configs = binding.get("configs", binding.get("configuration", []))
        if isinstance(raw_configs, dict):
            raw_configs = [raw_configs]
        if isinstance(raw_configs, list):
            configs.extend(item for item in raw_configs if isinstance(item, dict))
    scene_paths = list(dict.fromkeys(scene_paths))
    scenes = [inspect_scene(root, scene) for scene in scene_paths]
    discovered_scripts = list(dict.fromkeys(script for scene in scenes for script in scene.get("scripts", [])))
    scripts = []
    for script in list(dict.fromkeys([*declared_scripts, *discovered_scripts])):
        located = _repo_path(root, script)
        if located:
            rel, path = located
            scripts.append({"path": rel, "exists": path.is_file(), "evidence_kind": "configured" if script in declared_scripts else "scene-static"})
    node_rows = []
    discovered_nodes = {(scene["scene"], item["node_path"]): item for scene in scenes for item in scene.get("nodes", [])}
    for scene in scenes:
        for item in scene.get("nodes", []):
            configured = item["node_path"] in declared_nodes or item["name"] in declared_nodes
            node_rows.append({**item, "scene": scene["scene"], "evidence_kind": "configured" if configured else "scene-static"})
    for node in declared_nodes:
        if not any(node == item["node_path"] or node == item["name"] for item in node_rows):
            node_rows.append({"node_path": node, "name": node.rsplit("/", 1)[-1], "type": "", "scene": None, "evidence_kind": "configured-unresolved"})
    witness_rows = []
    for witness in list(dict.fromkeys(witnesses)):
        located = _repo_path(root, witness)
        if located:
            rel, path = located
            witness_rows.append({"path": rel, "exists": path.is_file(), "evidence_kind": "configured"})
    config_rows = []
    for config in configs:
        path_value = str(config.get("path") or "").strip()
        if not path_value:
            continue
        located = _repo_path(root, path_value)
        if not located:
            continue
        rel, path = located
        config_rows.append({
            "path": rel,
            "exists": path.is_file(),
            "pointers": [str(value) for value in config.get("pointers", config.get("fields", [])) if isinstance(value, (str, int, float))],
            "evidence_kind": "configured",
        })
    return {
        "schema": "godot-project-health.godot-navigation.v1",
        "task_id": str(task_id),
        "bindings": matched,
        "scenes": scenes,
        "nodes": node_rows,
        "scripts": scripts,
        "configs": config_rows,
        "witnesses": witness_rows,
        "note": "Static navigation validates configured mappings and scene text only; it does not promote inferred business semantics to authority.",
    }
