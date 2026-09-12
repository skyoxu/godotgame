#!/usr/bin/env python3
"""Template-safe immutable Impact Index core.

The index is evidence-only. It records exact files, declarations, exact JSON
configuration pointers, resource references, scene/script wiring and configured
task-scene relations from a trusted Git revision. Plain text symbol references
remain explicitly unconfirmed.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

INDEX_SCHEMA = "godot-project-impact.index.v1"
MANIFEST_SCHEMA = "godot-project-impact.index-manifest.v1"
FULL_SHA = re.compile(r"[0-9a-f]{40}")
CS_DECL = re.compile(r"\b(?:class|interface|record|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)")
CS_METHOD = re.compile(r"\b(?:public|private|protected|internal|static|virtual|override|async|sealed|partial|new|\s)+[A-Za-z_][A-Za-z0-9_<>,.?\[\]\s]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
GD_FUNC = re.compile(r"^\s*func\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
GD_CLASS = re.compile(r"^\s*class_name\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
RES_PATH = re.compile(r"res://([A-Za-z0-9_./ -]+)")
QUOTED_PATH = re.compile(r"[\"']((?:Game\.(?:Core|Godot)|Tests\.Godot|Game\.Core\.Tests)/[^\"']+)[\"']")
EXT_RESOURCE = re.compile(r'^\[ext_resource\s+[^\]]*path="res://([^"]+)"[^\]]*id="([^"]+)"[^\]]*\]', re.MULTILINE)
NODE = re.compile(r'^\[node\s+name="([^"]+)"(?:\s+type="([^"]+)")?(?:\s+parent="([^"]*)")?[^\]]*\]', re.MULTILINE)
SCRIPT_ASSIGN = re.compile(r'^script\s*=\s*ExtResource\("([^"]+)"\)', re.MULTILINE)
INSTANCE_ASSIGN = re.compile(r'instance\s*=\s*ExtResource\("([^"]+)"\)')


class ImpactIndexError(RuntimeError):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_path(value: str) -> str:
    path = PurePosixPath(str(value).replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ImpactIndexError("path_outside_repository", f"invalid repository path: {value}")
    return path.as_posix()


def _git(root: Path, *args: str, text: bool = True):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=text, encoding="utf-8" if text else None, check=False)


def resolve_revision(root: Path, revision: str, trusted_ref: str | None = None) -> str:
    value = revision.strip().casefold()
    if not FULL_SHA.fullmatch(value):
        raise ImpactIndexError("revision_mismatch", "revision must be a full 40-character Git SHA")
    resolved = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}")
    if resolved.returncode or resolved.stdout.strip().casefold() != value:
        raise ImpactIndexError("revision_mismatch", "revision is not available")
    if trusted_ref:
        trusted = _git(root, "rev-parse", "--verify", f"{trusted_ref}^{{commit}}")
        if trusted.returncode or trusted.stdout.strip().casefold() != value:
            raise ImpactIndexError("revision_mismatch", "trusted ref does not resolve to revision")
    return value


def _read_json(root: Path, revision: str, path: str) -> dict[str, Any]:
    proc = _git(root, "show", f"{revision}:{path}")
    if proc.returncode:
        raise ImpactIndexError("source_read_failure", f"unable to read {path}")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ImpactIndexError("invalid_manifest", f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ImpactIndexError("invalid_manifest", f"JSON object required: {path}")
    return data


def _policy_allows(path: str, config: dict[str, Any]) -> bool:
    exact = set(config.get("include_exact_paths", []))
    prefixes = tuple(config.get("include_prefixes", []))
    extensions = set(config.get("include_extensions", []))
    return (path in exact or path.startswith(prefixes)) and (path in exact or PurePosixPath(path).suffix.casefold() in extensions)


def _git_files(root: Path, revision: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    proc = _git(root, "ls-tree", "-rl", revision)
    if proc.returncode:
        raise ImpactIndexError("source_read_failure", "unable to enumerate trusted Git tree")
    result = []
    max_bytes = int(config.get("max_file_bytes", 1048576))
    for line in proc.stdout.splitlines():
        try:
            metadata, path = line.split("\t", 1)
            mode, kind, object_id, size_text = metadata.split()
            size = int(size_text)
            path = normalize_path(path)
        except ValueError:
            continue
        if kind != "blob" or size > max_bytes or not _policy_allows(path, config):
            continue
        result.append({"path": path, "git_mode": mode, "object_id": object_id, "size_bytes": size})
    return result


def _text(root: Path, revision: str, path: str) -> str:
    proc = _git(root, "show", f"{revision}:{path}")
    if proc.returncode:
        raise ImpactIndexError("source_read_failure", f"unable to read {path}")
    return proc.stdout


def _symbol_id(path: str, kind: str, name: str, line: int) -> str:
    return f"symbol:{kind}:{path}:{name}:{line}"


def _file_id(path: str) -> str:
    return "file:" + path


def _config_pointer_id(path: str, pointer: str) -> str:
    return f"config:{path}#{pointer}"


def _line_for(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def _declarations(path: str, text: str) -> list[dict[str, Any]]:
    symbols = []
    suffix = PurePosixPath(path).suffix.casefold()
    patterns: list[tuple[str, re.Pattern[str]]] = []
    if suffix == ".cs":
        patterns = [("type", CS_DECL), ("method", CS_METHOD)]
    elif suffix == ".gd":
        patterns = [("type", GD_CLASS), ("method", GD_FUNC)]
    for kind, pattern in patterns:
        for match in pattern.finditer(text):
            name = match.group(1)
            line = _line_for(text, match.start())
            symbols.append({"id": _symbol_id(path, kind, name, line), "kind": kind, "name": name, "path": path, "line": line})
    return symbols


def _pointer_token(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _json_pointers(path: str, text: str) -> list[dict[str, Any]]:
    if PurePosixPath(path).suffix.casefold() != ".json":
        return []
    try:
        document = json.loads(text)
    except json.JSONDecodeError:
        return []
    result: list[dict[str, Any]] = []

    def walk(value: Any, pointer: str) -> None:
        if pointer:
            if isinstance(value, dict):
                value_type = "object"
            elif isinstance(value, list):
                value_type = "array"
            elif value is None:
                value_type = "null"
            elif isinstance(value, bool):
                value_type = "boolean"
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                value_type = "number"
            else:
                value_type = "string"
            result.append({"id": _config_pointer_id(path, pointer), "path": path, "pointer": pointer, "value_type": value_type})
        if isinstance(value, dict):
            for key in sorted(value):
                walk(value[key], f"{pointer}/{_pointer_token(key)}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{pointer}/{index}")

    walk(document, "")
    return result


def _resource_edges(path: str, text: str, known_paths: set[str]) -> list[dict[str, Any]]:
    values = []
    for pattern in (RES_PATH, QUOTED_PATH):
        for match in pattern.finditer(text):
            target = normalize_path(match.group(1))
            if target in known_paths:
                values.append({"from": _file_id(path), "to": _file_id(target), "type": "resource-reference", "confirmed": True, "line": _line_for(text, match.start())})
    return values


def _scene_edges(path: str, text: str, known_paths: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not path.endswith(".tscn"):
        return [], []
    resources = {match.group(2): normalize_path(match.group(1)) for match in EXT_RESOURCE.finditer(text)}
    edges = []
    nodes = []
    node_matches = list(NODE.finditer(text))
    for index, match in enumerate(node_matches):
        name, node_type, parent = match.group(1), match.group(2), match.group(3)
        start = match.end()
        end = node_matches[index + 1].start() if index + 1 < len(node_matches) else len(text)
        block = text[start:end]
        node_path = name if not parent or parent == "." else f"{parent}/{name}"
        node = {"node_path": node_path, "type": node_type, "line": _line_for(text, match.start())}
        script = SCRIPT_ASSIGN.search(block)
        if script and resources.get(script.group(1)) in known_paths:
            target = resources[script.group(1)]
            node["script"] = target
            edges.append({"from": _file_id(path), "to": _file_id(target), "type": "scene-script", "confirmed": True, "node_path": node_path, "line": _line_for(text, start + script.start())})
        instance = INSTANCE_ASSIGN.search(match.group(0)) or INSTANCE_ASSIGN.search(block)
        if instance and resources.get(instance.group(1)) in known_paths:
            target = resources[instance.group(1)]
            node["instance"] = target
            edges.append({"from": _file_id(path), "to": _file_id(target), "type": "scene-instance", "confirmed": True, "node_path": node_path, "line": node["line"]})
        nodes.append(node)
    return edges, nodes


def _configured_edges(root: Path, revision: str, known_paths: set[str]) -> list[dict[str, Any]]:
    config_path = "scripts/python/project_health_knowledge_config.json"
    proc = _git(root, "cat-file", "-e", f"{revision}:{config_path}")
    if proc.returncode:
        return []
    config = _read_json(root, revision, config_path)
    edges = []
    for binding in config.get("task_scene_bindings", []):
        if not isinstance(binding, dict):
            continue
        task_id = str(binding.get("task_id", binding.get("taskmaster_id", ""))).strip()
        scene = str(binding.get("scene") or "").replace("\\", "/")
        if task_id and scene in known_paths:
            edges.append({"from": f"task:{task_id}", "to": _file_id(scene), "type": "configured-task-scene", "confirmed": True})
    return edges


def build_index(root: Path, revision: str, *, trusted_ref: str | None = None, config_path: str = "scripts/python/impact_analysis_config.v1.json", aliases_path: str = "scripts/python/impact_target_aliases.v1.json") -> dict[str, Any]:
    root = root.resolve()
    revision = resolve_revision(root, revision, trusted_ref)
    config = _read_json(root, revision, config_path)
    aliases = _read_json(root, revision, aliases_path)
    files = _git_files(root, revision, config)
    known_paths = {item["path"] for item in files}
    symbols: list[dict[str, Any]] = []
    config_pointers: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    scenes: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []
    for item in files:
        path = item["path"]
        text = _text(root, revision, path)
        digest = sha256_bytes(text.encode("utf-8"))
        manifest.append({**item, "sha256": digest})
        declared = _declarations(path, text)
        symbols.extend(declared)
        for symbol in declared:
            relations.append({"from": _file_id(path), "to": symbol["id"], "type": "declares", "confirmed": True, "line": symbol["line"]})
        pointers = _json_pointers(path, text)
        config_pointers.extend(pointers)
        for pointer in pointers:
            relations.append({"from": _file_id(path), "to": pointer["id"], "type": "declares-config-pointer", "confirmed": True, "pointer": pointer["pointer"]})
        relations.extend(_resource_edges(path, text, known_paths))
        scene_edges, nodes = _scene_edges(path, text, known_paths)
        relations.extend(scene_edges)
        if nodes:
            scenes.append({"path": path, "nodes": nodes})
    relations.extend(_configured_edges(root, revision, known_paths))
    # Unconfirmed symbol-text evidence is useful for exploration but never semantic authority.
    symbol_names = {symbol["name"]: symbol for symbol in symbols}
    for item in files:
        path = item["path"]
        text = _text(root, revision, path)
        for name, symbol in symbol_names.items():
            if path == symbol["path"]:
                continue
            for match in re.finditer(rf"\b{re.escape(name)}\b", text):
                relations.append({"from": _file_id(path), "to": symbol["id"], "type": "text-symbol-reference", "confirmed": False, "line": _line_for(text, match.start())})
                break
    identity = {
        "repository_revision": revision,
        "config_revision": str(config.get("revision")),
        "config_sha256": sha256_bytes(canonical_bytes(config)),
        "aliases_revision": str(aliases.get("revision")),
        "aliases_sha256": sha256_bytes(canonical_bytes(aliases)),
        "source_manifest_sha256": sha256_bytes(canonical_bytes(manifest)),
    }
    index_id = "idx-" + sha256_bytes(canonical_bytes(identity))
    return {
        "schema": INDEX_SCHEMA,
        "index_id": index_id,
        "repository_revision": revision,
        "trusted_ref": trusted_ref,
        "identity": identity,
        "source_manifest": manifest,
        "files": [{"id": _file_id(item["path"]), **item} for item in manifest],
        "symbols": sorted(symbols, key=lambda item: item["id"]),
        "config_pointers": sorted(config_pointers, key=lambda item: item["id"]),
        "scenes": scenes,
        "relations": relations,
        "aliases": aliases.get("aliases", []),
    }


def publish_index(root: Path, index: dict[str, Any], output_root: Path) -> dict[str, Any]:
    day = datetime.now(timezone.utc).date().isoformat()
    directory = output_root / day / "impact-index" / index["index_id"]
    directory.mkdir(parents=True, exist_ok=True)
    index_path = directory / "impact-index.v1.json"
    raw = json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    index_path.write_text(raw, encoding="utf-8")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "index_id": index["index_id"],
        "repository_revision": index["repository_revision"],
        "artifact_path": index_path.relative_to(root).as_posix(),
        "artifact_sha256": sha256_bytes(raw.encode("utf-8")),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = directory / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    current = root / "logs/ci/impact-index/current.json"
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "published", "index_id": index["index_id"], "index_path": manifest["artifact_path"], "manifest_path": manifest_path.relative_to(root).as_posix()}


def load_current_index(root: Path, revision: str | None = None) -> dict[str, Any]:
    pointer = root / "logs/ci/impact-index/current.json"
    if not pointer.is_file():
        raise ImpactIndexError("missing_index", "current impact index is missing")
    manifest = json.loads(pointer.read_text(encoding="utf-8"))
    if revision and manifest.get("repository_revision") != revision:
        raise ImpactIndexError("stale_index", "impact index revision does not match requested revision")
    path = root / str(manifest.get("artifact_path"))
    raw = path.read_bytes()
    if sha256_bytes(raw) != manifest.get("artifact_sha256"):
        raise ImpactIndexError("invalid_manifest", "impact index hash mismatch")
    index = json.loads(raw.decode("utf-8"))
    if index.get("index_id") != manifest.get("index_id"):
        raise ImpactIndexError("invalid_manifest", "impact index id mismatch")
    return index
