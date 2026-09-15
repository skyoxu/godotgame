"""Conservative, template-safe static Godot scene graph extraction.

The graph is evidence-scoped: only PackedScene instances or statically proven
scene-switch/instantiation routes make a destination reachable. Literal scene
paths without a proven trigger remain visible as ``possible`` references.
"""
from __future__ import annotations

import posixpath
import re
import subprocess
from collections import deque
from pathlib import Path, PurePosixPath
from typing import Any

SCENE_SUFFIX = ".tscn"
SCRIPT_SUFFIXES = {".gd", ".cs"}
CONFIG_SUFFIXES = {".json", ".cfg", ".ini", ".csv", ".yaml", ".yml", ".toml", ".tres", ".res"}
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".wav", ".ogg", ".mp3", ".ttf", ".otf", ".glb"}
_TEXT_SUFFIXES = {SCENE_SUFFIX, *SCRIPT_SUFFIXES}
_RES_PATH = re.compile(r"res://([^\"'\s)]+)")
_NODE = re.compile(r"^\[node\b([^\]]*)\]")
_SUB = re.compile(r'^\[sub_resource\s+type="([^"]+)"\s+id="([^"]+)"\]')
_EXT = re.compile(r"^\[ext_resource\b([^\]]*)\]")


def _clean(path: str) -> str:
    return path.removeprefix("res://").replace("\\", "/")


def _attrs(text: str) -> dict[str, str]:
    return dict(re.findall(r'(\w+)="([^"]*)"', text))


def _resolve_target(source: str, target: str, known: set[str]) -> str:
    target = posixpath.normpath(target).lstrip("./")
    if target in known:
        return target
    parts = source.split("/")
    for index in range(len(parts) - 1, 0, -1):
        candidate = posixpath.normpath("/".join(parts[:index] + [target]))
        if candidate in known:
            return candidate
    return target


def _main_scene(project_text: str) -> str | None:
    match = re.search(r'(?:run/main_scene|application/run/main_scene)\s*=\s*"res://([^"\r\n]+)"', project_text)
    return _clean(match.group(1)) if match else None


def _scene_evidence(line: str) -> tuple[str, str]:
    if re.search(r"\b(?:change_scene(?:_to_file|_to_packed)?|_?switch_to|instantiate)\s*\(", line):
        return "effective", "explicit scene switch or instantiation call"
    return "possible", "scene path literal without a statically proven trigger"


def _parse_scene(path: str, text: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    external: dict[str, dict[str, str]] = {}
    sub_resources: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        ext_match = _EXT.match(line)
        if ext_match:
            attrs = _attrs(ext_match.group(1))
            resource_id = attrs.get("id")
            resource_path = attrs.get("path")
            if resource_id and resource_path:
                external[resource_id] = {"path": _clean(resource_path), "type": attrs.get("type", "")}
            continue
        sub_match = _SUB.match(line)
        if sub_match:
            sub_resources.append({"type": sub_match.group(1), "id": sub_match.group(2), "line": line_no})
            continue
        node_match = _NODE.match(line)
        if node_match:
            attrs = _attrs(node_match.group(1))
            instance = re.search(r'instance=ExtResource\("([^"]+)"\)', node_match.group(1))
            instance_id = instance.group(1) if instance else None
            resource = external.get(instance_id or "")
            node = {
                "name": attrs.get("name", ""),
                "type": attrs.get("type", "inherited"),
                "parent": attrs.get("parent", "."),
                "line": line_no,
                "instance": resource.get("path") if resource else None,
                "resources": [],
            }
            if instance_id and resource is None:
                node["parse_error"] = f"missing ExtResource {instance_id}"
                diagnostics.append({"kind": "parse_error", "scene": path, "line": line_no, "reason": node["parse_error"]})
            if resource and resource.get("path", "").lower().endswith(SCENE_SUFFIX):
                edges.append({
                    "source": path,
                    "target": resource["path"],
                    "line": line_no,
                    "kind": "packed-scene-instance",
                    "evidence_level": "effective",
                    "evidence": "PackedScene instance declared on a scene node",
                })
            nodes.append(node)
            continue
        if nodes:
            nodes[-1]["resources"].extend(_clean(match.group(1)) for match in _RES_PATH.finditer(line))
            nodes[-1]["resources"].extend(
                f"SubResource({match.group(1)})" for match in re.finditer(r'SubResource\("([^"]+)"\)', line)
            )
    if not text.lstrip().startswith(("[gd_scene", "[gd_resource")):
        diagnostics.append({"kind": "parse_error", "scene": path, "line": 1, "reason": "missing gd_scene header"})
    root = next((node for node in nodes if node.get("parent") == "."), nodes[0] if nodes else {})
    scripts = sorted({resource["path"] for resource in external.values() if resource.get("path", "").lower().endswith(tuple(SCRIPT_SUFFIXES))})
    result: dict[str, Any] = {
        "path": path,
        "nodes": nodes,
        "external_resources": {key: value["path"] for key, value in external.items()},
        "external_resource_types": {key: value.get("type", "") for key, value in external.items()},
        "sub_resources": sub_resources,
        "child_scene_references": sorted({edge["target"] for edge in edges}),
        "description": f"Godot {root.get('type', 'scene')} scene with {len(nodes)} nodes" + (f"; scripts: {', '.join(scripts)}" if scripts else ""),
    }
    if any(item.get("kind") == "parse_error" for item in diagnostics):
        result["parse_error"] = "; ".join(item["reason"] for item in diagnostics if item.get("kind") == "parse_error")
    return result, edges, diagnostics


def _gd_function_bodies(text: str) -> dict[str, str]:
    lines = text.splitlines()
    starts: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(\s*)func\s+([A-Za-z_]\w*)\s*\(", line)
        if match:
            starts.append((index, len(match.group(1)), match.group(2)))
    bodies: dict[str, str] = {}
    for position, (start, _indent, name) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        bodies[name] = "\n".join(lines[start:end])
    return bodies


def build_scene_graph(sources: dict[str, str], known_paths: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    normalized = {path.replace("\\", "/"): text for path, text in sources.items()}
    known = {path.replace("\\", "/") for path in (known_paths or normalized.keys())} | set(normalized)
    scenes = {path: text for path, text in normalized.items() if path.lower().endswith(SCENE_SUFFIX)}
    main = _main_scene(normalized.get("project.godot", ""))
    diagnostics: list[dict[str, Any]] = []
    if not main:
        diagnostics.append({"kind": "missing_main_scene", "reason": "project.godot has no application/run/main_scene"})
    elif main not in scenes:
        diagnostics.append({"kind": "missing_main_scene", "reason": "configured main scene is not scanned", "path": main})

    parsed: dict[str, dict[str, Any]] = {}
    scene_edges: list[dict[str, Any]] = []
    for path, text in sorted(scenes.items()):
        try:
            parsed[path], edges, errors = _parse_scene(path, text)
            scene_edges.extend(edges)
            diagnostics.extend(errors)
        except Exception as exc:
            parsed[path] = {"path": path, "nodes": [], "external_resources": {}, "parse_error": str(exc)}
            diagnostics.append({"kind": "parse_error", "scene": path, "reason": str(exc)})

    for scene in parsed.values():
        for key, target in list(scene.get("external_resources", {}).items()):
            scene["external_resources"][key] = _resolve_target(scene["path"], target, known)
        for node in scene.get("nodes", []):
            if node.get("instance"):
                node["instance"] = _resolve_target(scene["path"], node["instance"], known)
    for edge in scene_edges:
        edge["target"] = _resolve_target(edge["source"], edge["target"], known)

    code_references: list[dict[str, Any]] = []
    for path, text in normalized.items():
        if PurePosixPath(path).suffix.casefold() not in SCRIPT_SUFFIXES:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            literal_found = False
            for match in _RES_PATH.finditer(line):
                literal_found = True
                target = _resolve_target(path, _clean(match.group(1)), known)
                suffix = PurePosixPath(target).suffix.casefold()
                if suffix == SCENE_SUFFIX:
                    evidence_level, evidence = _scene_evidence(line)
                    code_references.append({"source": path, "target": target, "line": line_no, "kind": "scene-reference", "classification": "static-reference", "evidence_level": evidence_level, "evidence": evidence})
                elif suffix in CONFIG_SUFFIXES:
                    code_references.append({"source": path, "target": target, "line": line_no, "kind": "config-reference", "classification": "static-reference", "evidence_level": "possible", "evidence": "literal config/resource path"})
                elif suffix in ASSET_SUFFIXES:
                    code_references.append({"source": path, "target": target, "line": line_no, "kind": "asset-reference", "classification": "static-reference", "evidence_level": "possible", "evidence": "literal asset path"})
            if re.search(r"\b(?:load|preload|ResourceLoader\.load)\s*\(", line) and not literal_found:
                code_references.append({"source": path, "line": line_no, "classification": "dynamic-unknown", "evidence": line.strip()[:400]})

    # A scene constant is only effective if it is later passed to an explicit route call.
    scene_constants: dict[tuple[str, str], tuple[str, int]] = {}
    for script_path, text in normalized.items():
        if PurePosixPath(script_path).suffix.casefold() not in SCRIPT_SUFFIXES:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            match = re.search(r'\b([A-Z][A-Z0-9_]*)\b[^"\']*["\']res://([^"\']+\.tscn)["\']', line)
            if match:
                scene_constants[(script_path, match.group(1))] = (_resolve_target(script_path, _clean(match.group(2)), known), line_no)
    for (script_path, constant), (target, declaration_line) in scene_constants.items():
        for line_no, line in enumerate(normalized[script_path].splitlines(), 1):
            if line_no == declaration_line:
                continue
            if re.search(r"\b(?:change_scene(?:_to_file|_to_packed)?|_?switch_to|instantiate)\s*\([^\n]*\b" + re.escape(constant) + r"\b", line):
                code_references.append({"source": script_path, "target": target, "line": line_no, "kind": "scene-reference", "classification": "static-reference", "evidence_level": "effective", "evidence": "scene constant passed to explicit route call"})
    effective_pairs = {(item.get("source"), item.get("target")) for item in code_references if item.get("kind") == "scene-reference" and item.get("evidence_level") == "effective"}
    code_references = [item for item in code_references if not (item.get("kind") == "scene-reference" and item.get("evidence_level") == "possible" and (item.get("source"), item.get("target")) in effective_pairs)]

    # Attach script references to the scene that owns the script. Possible edges
    # stay visible, but only effective edges participate in reachability.
    for scene_path, scene in parsed.items():
        scripts = sorted({value for value in scene.get("external_resources", {}).values() if PurePosixPath(value).suffix.casefold() in SCRIPT_SUFFIXES})
        events: set[str] = set()
        functions: set[str] = set()
        routes: set[str] = set()
        configs: set[str] = set()
        for script in scripts:
            text = normalized.get(script, "")
            events.update(re.findall(r'(?:Publish|PublishSimple)\s*\(\s*["\']([^"\']+)', text))
            events.update(re.findall(r'["\'](ui\.[A-Za-z0-9_.-]+)["\']', text))
            functions.update(re.findall(r"\b(?:func|void|bool|private|public|protected|internal|static)\s+([A-Za-z_]\w*)\s*\(", text))
            for reference in code_references:
                if reference.get("source") != script:
                    continue
                if reference.get("kind") == "scene-reference" and reference.get("target") != scene_path:
                    routes.add(str(reference.get("target")))
                    scene_edges.append({**reference, "source": scene_path, "kind": "script-reference"})
                elif reference.get("kind") == "config-reference":
                    configs.add(str(reference.get("target")))
        scene["functional_summary"] = {"scripts": scripts, "events": sorted(events), "functions": sorted(functions), "scene_routes": sorted(routes), "node_types": sorted({str(node.get('type') or '') for node in scene.get('nodes', []) if node.get('type')}), "config_references": sorted(configs)}

    # Bridge simple event-driven navigation: an attached script publishes a
    # literal event while another script has a matching conditional branch with
    # an explicit scene route.
    event_publishers: dict[str, set[str]] = {}
    event_constants: dict[str, str] = {}
    for text in normalized.values():
        for match in re.finditer(r'\bconst\s+string\s+(\w+)\s*=\s*["\']([^"\']+)["\']', text):
            event_constants[match.group(1)] = match.group(2)
    for script_path, text in normalized.items():
        if PurePosixPath(script_path).suffix.casefold() not in SCRIPT_SUFFIXES:
            continue
        for match in re.finditer(r'(?:Publish|PublishSimple)\s*\(\s*["\']([^"\']+)', text):
            event_publishers.setdefault(match.group(1), set()).add(script_path)
        for match in re.finditer(r"(?:Publish|PublishSimple)\s*\(\s*EventTypes\.(\w+)", text):
            event = event_constants.get(match.group(1))
            if event:
                event_publishers.setdefault(event, set()).add(script_path)

    handlers: dict[str, list[tuple[str, set[int]]]] = {}
    for script_path, text in normalized.items():
        if PurePosixPath(script_path).suffix.casefold() not in SCRIPT_SUFFIXES:
            continue
        lines = text.splitlines()
        for index, line in enumerate(lines):
            match = re.search(r'(?:if|elif|else\s+if)\s+[^\n]*["\']([^"\']+)["\']', line)
            if not match or match.group(1) not in event_publishers:
                continue
            indent = len(line) - len(line.lstrip())
            end = len(lines)
            for cursor in range(index + 1, len(lines)):
                candidate = lines[cursor]
                candidate_indent = len(candidate) - len(candidate.lstrip())
                if re.match(r"\s*(?:elif|else\s+if|else)\b", candidate) and candidate_indent == indent:
                    end = cursor
                    break
                if candidate.strip() and candidate_indent < indent:
                    end = cursor
                    break
            handlers.setdefault(match.group(1), []).append((script_path, set(range(index + 1, end + 1))))

    for scene_path, scene in parsed.items():
        attached = {value for value in scene.get("external_resources", {}).values() if PurePosixPath(value).suffix.casefold() in SCRIPT_SUFFIXES}
        for event, publishers in event_publishers.items():
            if not attached.intersection(publishers):
                continue
            for handler, line_numbers in handlers.get(event, []):
                for reference in code_references:
                    if reference.get("source") == handler and reference.get("line") in line_numbers and reference.get("kind") == "scene-reference":
                        scene_edges.append({"source": scene_path, "target": reference["target"], "line": reference["line"], "kind": "event-route", "event": event, "handler": handler, "evidence_level": "effective", "evidence": "event handler contains explicit scene route"})

    # Prefer effective evidence when the same relation is found more than once.
    deduplicated: dict[tuple[Any, ...], dict[str, Any]] = {}
    for edge in scene_edges:
        key = (edge.get("source"), edge.get("target"), edge.get("kind"), edge.get("event"))
        existing = deduplicated.get(key)
        if existing is None or (edge.get("evidence_level") == "effective" and existing.get("evidence_level") != "effective"):
            deduplicated[key] = edge
    scene_edges = sorted(deduplicated.values(), key=lambda item: (str(item.get("source")), str(item.get("target")), str(item.get("kind"))))

    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in scene_edges:
        if edge.get("evidence_level") == "effective":
            adjacency.setdefault(str(edge.get("source")), []).append(edge)

    reachable: set[str] = set()
    queue: deque[str] = deque()
    if main in scenes:
        reachable.add(main)
        queue.append(main)
    while queue:
        source = queue.popleft()
        for edge in adjacency.get(source, []):
            target = str(edge.get("target") or "")
            if target in scenes and target not in reachable:
                reachable.add(target)
                queue.append(target)

    colors: dict[str, int] = {}
    def visit(source: str) -> None:
        colors[source] = 1
        for edge in adjacency.get(source, []):
            target = str(edge.get("target") or "")
            if target not in reachable:
                continue
            if colors.get(target) == 1:
                diagnostics.append({"kind": "cycle", "source": source, "target": target, "line": edge.get("line")})
            elif colors.get(target, 0) == 0:
                visit(target)
        colors[source] = 2
    if main in reachable:
        visit(main)

    nodes = {path: {**data, "classification": "confirmed-reachable" if path in reachable else "unreachable-candidate"} for path, data in parsed.items()}
    diagnostics.extend({"kind": "dynamic-reference", **item} for item in code_references if item.get("classification") == "dynamic-unknown")
    return {
        "schema": "godot-project-knowledge.godot-scene-graph.v1",
        "main_scene": main,
        "nodes": nodes,
        "edges": scene_edges,
        "code_references": code_references,
        "diagnostics": diagnostics,
    }


def _git(root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    kwargs: dict[str, Any] = {"cwd": root, "capture_output": True, "check": False}
    if text:
        kwargs.update({"text": True, "encoding": "utf-8", "errors": "replace"})
    return subprocess.run(["git", *args], **kwargs)


def scene_graph_for_revision(root: Path, revision: str | None) -> dict[str, Any]:
    """Build a graph from one immutable Git revision, or a bounded workspace fixture."""
    root = root.resolve()
    sources: dict[str, str] = {}
    known_paths: list[str] = []
    if revision and re.fullmatch(r"[0-9a-f]{40}", revision):
        listed = _git(root, "ls-tree", "-r", "--name-only", revision)
        if listed.returncode != 0:
            raise ValueError("unable to enumerate Project Health revision")
        known_paths = [line.replace("\\", "/") for line in listed.stdout.splitlines() if line.strip()]
        selected = [path for path in known_paths if path == "project.godot" or PurePosixPath(path).suffix.casefold() in _TEXT_SUFFIXES]
        for path in selected:
            raw = _git(root, "show", f"{revision}:{path}", text=False)
            if raw.returncode != 0 or len(raw.stdout) > 2_000_000:
                continue
            try:
                sources[path] = raw.stdout.decode("utf-8-sig")
            except UnicodeDecodeError:
                continue
    else:
        for path in root.rglob("*"):
            if not path.is_file() or any(part in {".git", ".godot", "bin", "obj", "logs", "__pycache__"} for part in path.relative_to(root).parts):
                continue
            rel = path.relative_to(root).as_posix()
            known_paths.append(rel)
            if rel != "project.godot" and PurePosixPath(rel).suffix.casefold() not in _TEXT_SUFFIXES:
                continue
            if path.stat().st_size > 2_000_000:
                continue
            try:
                sources[rel] = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError):
                continue
    return build_scene_graph(sources, known_paths)
