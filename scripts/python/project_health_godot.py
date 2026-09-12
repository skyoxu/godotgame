#!/usr/bin/env python3
"""Template-safe, provenance-preserving Godot task navigation.

The implementation mirrors the investigation capabilities of the mature sibling
repository while removing product-specific identity assumptions. Literal paths,
scene attachments, exact JSON pointers and explicit reviewed mappings are evidence;
none of them silently become business authority.
"""
from __future__ import annotations

import json
import re
from pathlib import PurePosixPath
from typing import Any

from project_health_knowledge import ASSET_EXTENSIONS, latest, snapshot_text

CONFIG_SUFFIXES = {".json", ".tres", ".cfg", ".ini", ".csv", ".yaml", ".yml", ".toml"}
ASSET_SUFFIXES = set(ASSET_EXTENSIONS)
PATH_PATTERN = re.compile(r"(?:res://(?:\.\./)?|(?<![\w/]))((?:Game\.Core|Game\.Godot|Tests\.Godot|Game\.Core\.Tests)/[\w./-]+)")
QUOTED_PATH_PATTERN = re.compile(r'''(["'])(?:res://(?:\.\./)?)?((?:Game\.Core|Game\.Godot|Tests\.Godot|Game\.Core\.Tests)/[^"'\r\n]+)\1''')


def valid_path(path: str) -> bool:
    return bool(path) and ".." not in PurePosixPath(path).parts and not any(char in path for char in ":\\")


def references(text: str, available: set[str] | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for number, line in enumerate(str(text).splitlines(), 1):
        normalized = line.replace("\\\\", "/").replace('\\"', '"')
        quoted = list(QUOTED_PATH_PATTERN.finditer(normalized))
        matches = [(match.start(), match.group(2)) for match in quoted]
        matches.extend(
            (match.start(), match.group(1).rstrip(".,;:)"))
            for match in PATH_PATTERN.finditer(normalized)
            if not any(item.start() <= match.start() < item.end() for item in quoted)
        )
        for _, path in sorted(matches):
            ok = valid_path(path)
            if available is None or (ok and path in available):
                result.append({"path": path, "line": number, "evidence": line.strip()[:400], "valid": ok})
    return result


def _record_identity(value: dict[str, Any], inherited: Any = None) -> Any:
    if "id" in value and not isinstance(value["id"], (dict, list)):
        return value["id"]
    for key, item in value.items():
        if key.endswith("_id") and not isinstance(item, (dict, list)):
            return item
    return inherited


def fields(value: Any, pointer: str = "", identity: Any = None):
    """Return exact JSON leaves and generic record identities; never inferred constraints."""
    if isinstance(value, dict):
        identity = _record_identity(value, identity)
        for key, item in value.items():
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            yield from fields(item, pointer + "/" + escaped, identity)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from fields(item, pointer + "/" + str(index), identity)
    else:
        yield {
            "pointer": pointer,
            "value": value,
            "record_id": identity,
            "kind": "numeric_parameter" if isinstance(value, (int, float)) and not isinstance(value, bool) else "data_field",
        }


def located_fields(text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    parsed = json.loads(text)
    values = list(fields(parsed))
    positions: dict[str, dict[str, Any]] = {}

    def walk(offset: int, pointer: str = "") -> int:
        while offset < len(text) and text[offset].isspace():
            offset += 1
        start = offset
        if offset >= len(text):
            return offset
        if text[offset] == "{":
            offset += 1
            while True:
                while offset < len(text) and (text[offset].isspace() or text[offset] == ","):
                    offset += 1
                if text[offset] == "}":
                    return offset + 1
                key, offset = decoder.raw_decode(text, offset)
                while text[offset].isspace() or text[offset] == ":":
                    offset += 1
                escaped = str(key).replace("~", "~0").replace("/", "~1")
                offset = walk(offset, pointer + "/" + escaped)
        elif text[offset] == "[":
            offset += 1
            index = 0
            while True:
                while text[offset].isspace() or text[offset] == ",":
                    offset += 1
                if text[offset] == "]":
                    return offset + 1
                offset = walk(offset, pointer + "/" + str(index))
                index += 1
        else:
            _, end = decoder.raw_decode(text, offset)
            positions[pointer] = {
                "line": text.count("\n", 0, start) + 1,
                "column": start - text.rfind("\n", 0, start),
                "evidence": text[start:end],
            }
            return end
        return offset

    walk(0)
    return [{**item, **positions.get(item["pointer"], {})} for item in values]


def scene_nodes(path: str, sources: dict[str, str], available: set[str], visited: tuple[str, ...] = (), budget: list[int] | None = None) -> list[dict[str, Any]]:
    """Resolve scene/resource node properties with bounded Ext/SubResource expansion."""
    if budget is None:
        budget = [512]
    blocks: dict[tuple[str, str], dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for number, line in enumerate(sources.get(path, "").splitlines(), 1):
        if re.match(r"^\[(?:gd_scene|gd_resource|ext_resource|sub_resource|node|resource|connection)(?:\s|\])", line):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', line))
            instance = re.search(r'instance=(ExtResource\("[^"]+"\))', line)
            if instance:
                attrs["instance"] = instance.group(1)
            kind = line[1:].split(" ", 1)[0].rstrip("]")
            key = (kind, attrs.get("id", str(number)))
            current = {"kind": kind, "attrs": attrs, "line": number, "properties": []}
            blocks[key] = current
        elif current and re.match(r"^[\w/]+\s*=", line):
            key, value = line.split("=", 1)
            current["properties"].append({"name": key.strip(), "value": value.strip(), "line": number})
        elif current and current["properties"] and line.strip():
            current["properties"][-1]["value"] += "\n" + line.strip()

    def resolve(value: str, seen: tuple[tuple[str, str], ...] = ()) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for kind, identity in re.findall(r'(ExtResource|SubResource)\("([^"]+)"\)', value):
            key = ("ext_resource" if kind == "ExtResource" else "sub_resource", identity)
            reference = f"{kind}({identity})"
            reason = (
                "expansion_limit" if budget[0] <= 0 else
                "depth_limit" if len(seen) >= 32 else
                "resource_cycle" if key in seen else
                "resource_id_missing" if key not in blocks else None
            )
            budget[0] -= 1
            if reason:
                results.append({"path": "", "available": False, "chain": [reference], "unresolved_reason": reason})
                if reason == "expansion_limit":
                    break
                continue
            block = blocks[key]
            if kind == "ExtResource":
                target = block["attrs"].get("path", "").removeprefix("res://")
                item = {"path": target, "available": valid_path(target) and target in available, "chain": [reference], "line": block["line"]}
                results.append(item)
                if not item["available"]:
                    item["unresolved_reason"] = "invalid_or_unscanned_path"
                elif PurePosixPath(target).suffix.casefold() == ".tres":
                    nested_reason = (
                        "resource_cycle" if target in (*visited, path) else
                        "cross_resource_depth_limit" if len(visited) >= 8 else
                        "source_text_unavailable" if target not in sources else None
                    )
                    if nested_reason:
                        item["unresolved_reason"] = nested_reason
                    else:
                        for node in scene_nodes(target, sources, available, (*visited, path), budget):
                            for prop in node["properties"]:
                                for nested in prop["resources"]:
                                    results.append({**nested, "chain": [reference, target, prop["name"], *nested["chain"]]})
            else:
                for prop in block["properties"]:
                    for nested in resolve(prop["value"], (*seen, key)):
                        results.append({**nested, "chain": [reference, prop["name"], *nested["chain"]]})
        return results

    result: list[dict[str, Any]] = []
    for block in blocks.values():
        if block["kind"] not in ("node", "resource"):
            continue
        attrs = block["attrs"]
        parent = attrs.get("parent")
        node_path = "." if parent is None else "/".join(value for value in (parent, attrs.get("name", "")) if value != ".")
        properties = [{**prop, "resources": resolve(prop["value"])} for prop in block["properties"]]
        result.append({
            "scene": path,
            "node_path": node_path,
            "name": attrs.get("name", ""),
            "type": attrs.get("type", "inherited"),
            "line": block["line"],
            "properties": properties,
            "instance": resolve(attrs.get("instance", "")),
        })
    return result


def scene_bindings(sources: dict[str, str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path, text in sorted(sources.items()):
        if not path.startswith("Game.Godot/") or not path.endswith(".tscn"):
            continue
        resources: dict[str | None, str] = {}
        node: str | None = None
        for number, line in enumerate(text.splitlines(), 1):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', line))
            if line.startswith("[ext_resource"):
                resources[attrs.get("id")] = attrs.get("path", "").removeprefix("res://")
            elif line.startswith("[node "):
                name, parent = attrs.get("name", ""), attrs.get("parent")
                node = "." if parent is None else (name if parent == "." else f"{parent}/{name}")
            elif line.startswith("["):
                node = None
            match = re.fullmatch(r'\s*script\s*=\s*ExtResource\("([^"]+)"\)\s*', line)
            if match and node is not None:
                script = resources.get(match.group(1))
                if script in sources:
                    result.append({"scene": path, "node": node, "script": script, "line": number})
    return result


def _source_map(root, state: dict[str, Any]) -> dict[str, str]:
    sources: dict[str, str] = {}
    for record in state.get("records", []):
        rel = str(record.get("path") or "")
        if not record.get("searchable"):
            continue
        if not rel.startswith(("Game.Core/", "Game.Godot/", "Game.Core.Tests/", "Tests.Godot/", ".taskmaster/tasks/")):
            continue
        try:
            sources[rel] = snapshot_text(root, rel, state)
        except (ValueError, UnicodeDecodeError):
            continue
    return sources


def _binding_configs(bindings: list[dict[str, Any]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for binding in bindings:
        raw = binding.get("configs", binding.get("configuration", []))
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            continue
        for item in raw:
            if not isinstance(item, dict) or not str(item.get("path") or "").strip():
                continue
            path = str(item["path"]).strip().removeprefix("res://")
            pointers = item.get("pointers", item.get("fields", []))
            if not isinstance(pointers, list):
                pointers = []
            result.setdefault(path, set()).update(str(value) for value in pointers if str(value).startswith("/"))
    return result


def build_navigation(root, task_id: str, *, task: dict[str, Any] | None = None, mappings: Any = None, bindings: list[dict[str, Any]] | None = None, state: dict[str, Any] | None = None) -> dict[str, Any]:
    state = state or latest(root)
    sources = _source_map(root, state)
    available = {str(record.get("path") or "") for record in state.get("records", [])}
    matched = [item for item in (bindings or []) if str(item.get("task_id", item.get("taskmaster_id", ""))).strip() == str(task_id).strip()]
    payload_text = json.dumps({"task": task or {}, "mappings": mappings or {}, "bindings": matched}, ensure_ascii=False)
    declared = references(payload_text)
    actual_bindings = scene_bindings(sources)
    confirmed, invalid = [], []
    for declaration in matched:
        scene = str(declaration.get("scene") or "").removeprefix("res://")
        node = str(declaration.get("node", declaration.get("node_path", "")) or "")
        script = str(declaration.get("script") or "").removeprefix("res://")
        witness = str(declaration.get("witness") or "")
        matches = [row for row in actual_bindings if row["scene"] == scene and row["node"] == node and row["script"] == script]
        if matches and witness.strip() and witness in sources.get(script, ""):
            confirmed.append({**matches[0], "witness": witness, "kind": "declared_task_with_verified_static_attachment"})
        else:
            invalid.append(declaration)
    tests = sorted({item["path"] for item in references(payload_text, available) if item["path"].startswith(("Tests.Godot/", "Game.Core.Tests/"))})
    candidates = []
    for test in tests:
        for scene in sorted(set(re.findall(r'res://([^"\s]+\.tscn)', sources.get(test, "")))):
            if scene in sources and scene.startswith("Game.Godot/"):
                candidates.append({"scene": scene, "evidence": test, "kind": "test_reference"})
    roots = {item["path"] for item in declared if item["valid"] and item["path"] in available}
    roots.update(item["scene"] for item in confirmed if item["scene"] in available)
    roots.update(item["scene"] for item in candidates if item["scene"] in available)
    reached = {path: [{"path": path, "kind": "task_reference"}] for path in roots}
    edges = {path: references(text, available) for path, text in sources.items()}
    for _ in range(5):
        additions: dict[str, list[dict[str, Any]]] = {}
        for path, chain in list(reached.items()):
            for edge in edges.get(path, []):
                if edge["path"] not in reached:
                    additions.setdefault(edge["path"], [*chain, {"path": edge["path"], "from": path, "line": edge["line"], "kind": "literal_reference"}])
        if not additions:
            break
        reached.update(additions)
    configured_pointers = _binding_configs(matched)
    configs, code, scenes, assets = [], [], [], []
    for path, chain in sorted(reached.items()):
        suffix = PurePosixPath(path).suffix.casefold()
        provenance = {"path": path, "chain": chain, "focus": "core" if path in roots else "related", "evidence_kind": "static_reference", "runtime_observed": False}
        if suffix in CONFIG_SUFFIXES and path.startswith(("Game.Core/", "Game.Godot/")):
            readers = [{"reader": reader, "line": edge["line"], "evidence": edge["evidence"]} for reader, refs in edges.items() for edge in refs if edge["path"] == path]
            values, error = [], None
            if suffix == ".json":
                try:
                    values = located_fields(sources[path])
                except (ValueError, KeyError, RecursionError, json.JSONDecodeError) as exc:
                    error = str(exc)
            pointer_set = configured_pointers.get(path, set())
            configs.append({**provenance, "fields": values[:500], "field_count": len(values), "confirmed_fields": [{**field, "confirmation": "explicit_task_mapping"} for field in values if field.get("pointer") in pointer_set][:50], "truncated": len(values) > 500, "parse_error": error, "readers": readers, "activation": "Literal references do not prove runtime loading."})
        elif suffix in (".cs", ".gd") and path.startswith(("Game.Core/", "Game.Godot/")):
            code.append(provenance)
        elif suffix == ".tscn" and path.startswith("Game.Godot/"):
            scenes.append({**provenance, "nodes": scene_nodes(path, sources, available)})
        elif suffix in ASSET_SUFFIXES:
            assets.append({**provenance, "available": path in available, "users": [{"source": reader, "line": edge["line"], "evidence": edge["evidence"]} for reader, refs in edges.items() for edge in refs if edge["path"] == path]})
    unresolved = [{"source": source, **edge, "reason": "Not present in the scanned manifest" if edge["valid"] else "Invalid repository path"} for source, refs in [("task declaration", declared), *((path, references(sources.get(path, ""))) for path in reached)] for edge in refs if not edge["valid"] or edge["path"] not in available]
    return {
        "schema": "godot-project-health.godot-navigation.v2",
        "revision": state.get("revision"),
        "task_id": str(task_id),
        "static": {"status": "static_attached" if confirmed else ("candidate" if candidates else "unmapped"), "scenes": confirmed, "candidates": candidates, "invalid_declarations": invalid, "limitation": "Static attachment is not runtime execution or acceptance proof. Unmapped does not mean absent."},
        "configs": configs,
        "code": code,
        "scenes": scenes,
        "assets": assets,
        "tests": [{"path": path, "evidence_kind": "declared_test", "command_status": "suggested_not_executed", "command": (f'py -3 scripts/python/run_gdunit.py --godot-bin "$env:GODOT_BIN" --project Tests.Godot --prewarm --add "{path.removeprefix("Tests.Godot/")}"' if path.startswith("Tests.Godot/") else f'dotnet test Game.Core.Tests/Game.Core.Tests.csproj --filter "FullyQualifiedName~{PurePosixPath(path).stem}"')} for path in tests],
        "text_sources": sorted(sources),
        "unresolved_references": unresolved,
        "limitations": [
            "Static navigation does not prove runtime resource use.",
            "Test scene loads are candidates requiring inspection.",
            "Dynamic resource paths, runtime-created nodes and inherited overrides may be unresolved.",
            "Reference traversal stops after five hops.",
            "Configured JSON pointers are confirmed only when the exact field exists in the scanned file.",
        ],
    }


def static_status(root, task_id: str, *, task: dict[str, Any] | None = None, mappings: Any = None, bindings: list[dict[str, Any]] | None = None, state: dict[str, Any] | None = None) -> dict[str, Any]:
    nav = build_navigation(root, task_id, task=task, mappings=mappings, bindings=bindings, state=state)
    return nav["static"]
