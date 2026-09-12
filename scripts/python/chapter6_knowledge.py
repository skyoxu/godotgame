#!/usr/bin/env python3
"""Capture reviewed Chapter 6 resource knowledge and optional semantic enrichment.

The semantic lane is evidence-constrained: the model may explain only resources,
JSON pointers, scene nodes, and asset bindings reconstructed from the current
Project Health snapshot. Generated explanations are non-authoritative and never
become runtime proof.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from generate_knowledge_links import generate
from init_knowledge_catalog import initialize
from project_health_knowledge import scan, write_json


def capture(root: Path, task_id: str, paths: list[str]) -> dict[str, Any]:
    """Capture only explicitly reviewed workspace resources; never invent links."""
    normalized: list[str] = []
    for raw in paths:
        candidate = (root / raw).resolve()
        if root != candidate and root not in candidate.parents:
            raise ValueError(f"path escapes repository: {raw}")
        if not candidate.exists():
            raise ValueError(f"resource path does not exist: {raw}")
        normalized.append(candidate.relative_to(root).as_posix())
    if not normalized:
        return {"status": "skipped", "reason": "no reviewed resource paths supplied", "task_id": str(task_id)}
    out = {
        "schema": "godot-project-knowledge.reviewed-resources.v2",
        "task_id": str(task_id),
        "resources": sorted(set(normalized)),
        "provenance": "explicit-reviewed-input",
    }
    path = root / "docs/knowledge/generated" / f"task-{task_id}-resources.json"
    write_json(path, out)
    return {"status": "ok", "output": path.relative_to(root).as_posix(), "count": len(out["resources"])}


def _semantic_prompt_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for entry in entries:
        kind = entry.get("kind")
        if kind not in {"config", "asset", "scene"}:
            continue
        item: dict[str, Any] = {
            key: entry.get(key)
            for key in ("id", "path", "kind", "role", "task_title", "readers", "evidence", "test_refs")
        }
        if kind == "config":
            fields = entry.get("parameters") if isinstance(entry.get("parameters"), list) else []
            prioritized = sorted(
                (field for field in fields if isinstance(field, dict) and isinstance(field.get("pointer"), str)),
                key=lambda field: (field.get("kind") != "numeric_parameter", field.get("line") or 0),
            )
            item["available_parameters"] = [
                {key: field.get(key) for key in ("pointer", "value", "line", "record_id", "kind")}
                for field in prioritized[:80]
            ]
            item["available_parameters_truncated"] = len(fields) > 80
        elif kind == "asset":
            bindings = entry.get("bindings") if isinstance(entry.get("bindings"), list) else []
            item["available_bindings"] = [
                {key: binding.get(key) for key in ("source", "line", "evidence")}
                for binding in bindings[:12] if isinstance(binding, dict)
            ]
            item["available_bindings_truncated"] = len(bindings) > 12
        else:
            bindings = entry.get("bindings") if isinstance(entry.get("bindings"), list) else []
            item["available_bindings"] = [{
                "node_path": binding.get("node_path"),
                "type": binding.get("type"),
                "line": binding.get("line"),
                "properties": [
                    {key: prop.get(key) for key in ("name", "value", "line")}
                    for prop in binding.get("properties", [])[:12] if isinstance(prop, dict)
                ],
            } for binding in bindings[:20] if isinstance(binding, dict)]
            item["available_bindings_truncated"] = len(bindings) > 20
        compact.append(item)
    return compact


def _validate_semantic_entries(model: object, entries: list[dict[str, Any]]) -> tuple[bool, list[dict[str, Any]], str | None]:
    if not isinstance(model, list) or not all(isinstance(item, dict) for item in model):
        return False, [], "semantic output must be an array of objects"
    available = {str(entry.get("path")): entry for entry in entries if entry.get("path")}
    normalized: list[dict[str, Any]] = []
    for item in model:
        path = str(item.get("path") or "")
        if path not in available:
            return False, [], f"unknown resource path: {path}"
        source = available[path]
        kind = source.get("kind")
        parameters = item.get("parameters", [])
        if not isinstance(parameters, list) or not all(isinstance(parameter, dict) for parameter in parameters):
            return False, [], f"parameters must be an array of objects: {path}"
        fields = source.get("parameters") if kind == "config" and isinstance(source.get("parameters"), list) else []
        fields_by_pointer = {
            str(field.get("pointer")): field
            for field in fields if isinstance(field, dict) and isinstance(field.get("pointer"), str)
        }
        validated_parameters: list[dict[str, Any]] = []
        for parameter in parameters:
            pointer = parameter.get("pointer") or parameter.get("key")
            if not isinstance(pointer, str) or pointer not in fields_by_pointer:
                return False, [], f"unknown parameter pointer for {path}: {pointer}"
            field = fields_by_pointer[pointer]
            validated_parameters.append({
                "pointer": pointer,
                "meaning": str(parameter.get("meaning") or parameter.get("description") or ""),
                "value": field.get("value"),
                "line": field.get("line"),
                "evidence_status": "field_exists_semantic_inference",
            })

        bindings = item.get("bindings", [])
        if not isinstance(bindings, list) or not all(isinstance(binding, dict) for binding in bindings):
            return False, [], f"bindings must be an array of objects: {path}"
        source_bindings = source.get("bindings") if isinstance(source.get("bindings"), list) else []
        validated_bindings: list[dict[str, Any]] = []
        if kind == "asset":
            available_bindings = {
                (binding.get("source"), binding.get("line")): binding
                for binding in source_bindings if isinstance(binding, dict)
            }
            for binding in bindings:
                key = (binding.get("source"), binding.get("line"))
                if key not in available_bindings or not str(binding.get("meaning") or "").strip():
                    return False, [], f"unknown or unexplained asset binding for {path}: {key}"
                actual = available_bindings[key]
                validated_bindings.append({
                    "source": actual.get("source"),
                    "line": actual.get("line"),
                    "evidence": actual.get("evidence"),
                    "meaning": str(binding.get("meaning") or ""),
                    "evidence_status": "static_binding_semantic_explanation",
                })
        elif kind == "scene":
            available_bindings = {
                (binding.get("node_path"), binding.get("line")): binding
                for binding in source_bindings if isinstance(binding, dict)
            }
            for binding in bindings:
                key = (binding.get("node_path"), binding.get("line"))
                if key not in available_bindings or not str(binding.get("meaning") or "").strip():
                    return False, [], f"unknown or unexplained scene binding for {path}: {key}"
                actual = available_bindings[key]
                validated_bindings.append({
                    "node_path": actual.get("node_path"),
                    "type": actual.get("type"),
                    "line": actual.get("line"),
                    "meaning": str(binding.get("meaning") or ""),
                    "evidence_status": "static_binding_semantic_explanation",
                })
        elif bindings:
            return False, [], f"bindings are not supported for {path}"

        normalized.append({
            "id": source.get("id"),
            "path": path,
            "kind": kind,
            "explanation": str(item.get("explanation") or ""),
            "modification_guidance": str(item.get("modification_guidance") or item.get("parameter_guidance") or ""),
            "modification_impact": str(item.get("modification_impact") or ""),
            "parameters": validated_parameters,
            "bindings": validated_bindings,
        })

    returned_kinds = {item.get("kind") for item in normalized}
    for required_kind in ("asset", "scene"):
        if any(entry.get("kind") == required_kind for entry in entries) and required_kind not in returned_kinds:
            return False, [], f"missing semantic {required_kind} entry"
    return True, normalized, None


def _build_semantic_prompt(prompt_entries: list[dict[str, Any]]) -> str:
    return (
        "Return a JSON array only. Explain only the supplied config, asset, or scene resources for a developer implementing this task. "
        "Keep every explanation non-authoritative and evidence-scoped. For each returned item keep path and add explanation, "
        "modification_guidance, modification_impact, parameters, and bindings. parameters must use only exact pointer values listed "
        "in available_parameters for that same config. Asset bindings must use exact source/line pairs; scene bindings must use exact "
        "node_path/line pairs from available_bindings. Every returned binding must have a non-empty meaning. Do not invent paths, "
        "fields, nodes, runtime observations, task facts, or evidence. Omit unrelated resources. Return at least one relevant asset and "
        "one relevant scene when those kinds are supplied.\n"
        + json.dumps(prompt_entries, ensure_ascii=False, separators=(",", ":"))
    )


def _semantic_enrich(root: Path, task_id: str, backend: str) -> dict[str, Any]:
    sys.path.insert(0, str(root / "scripts/sc"))
    from _llm_backend import run_llm_exec

    links = root / "docs/knowledge/generated/task-resource-links.json"
    payload = json.loads(links.read_text(encoding="utf-8-sig")) if links.exists() else {"generated": []}
    entries = [
        item for item in payload.get("generated", [])
        if isinstance(item, dict) and str(item.get("task_id")) == str(task_id)
    ]
    candidates = [entry for entry in entries if entry.get("kind") == "config"]
    candidates += [entry for entry in entries if entry.get("kind") == "asset"][:12]
    scenes = [entry for entry in entries if entry.get("kind") == "scene"]
    scenes.sort(key=lambda entry: entry.get("evidence", [{}])[0].get("focus") != "core")
    candidates += scenes[:8]
    if not candidates:
        return {"status": "skipped", "reason": "no config/asset/scene evidence for semantic enrichment"}

    output = root / "docs/knowledge/generated" / f"task-{task_id}-semantic.json"
    prompt = _build_semantic_prompt(_semantic_prompt_entries(candidates))
    validation_error: str | None = None
    model: list[dict[str, Any]] | None = None
    rc = 1
    trace = ""
    command: list[str] = []
    for attempt in range(1, 6):
        rc, trace, command = run_llm_exec(
            backend=backend,
            root=root,
            prompt=prompt,
            output_last_message=output,
            timeout_sec=300,
        )
        if rc == 0:
            try:
                candidate = json.loads(output.read_text(encoding="utf-8-sig"))
                valid, model, validation_error = _validate_semantic_entries(candidate, entries)
                if valid:
                    break
                model = None
            except (OSError, json.JSONDecodeError) as exc:
                validation_error = str(exc)
        if attempt < 5:
            time.sleep(1)
    if rc != 0 or model is None:
        write_json(output, {
            "status": "unverified",
            "task_id": str(task_id),
            "generated_by": "llm-assisted-semantic-analysis",
            "attempts": 5,
            "error": validation_error or trace[-1000:] or "semantic output validation failed",
        })
        return {"status": "unverified", "rc": rc, "attempts": 5}
    write_json(output, {
        "status": "verified",
        "task_id": str(task_id),
        "generated_by": "llm-assisted-semantic-analysis",
        "backend": backend,
        "entries": model,
    })
    return {"status": "verified", "entries": len(model), "attempts": attempt, "command": command}


def run(
    root: Path,
    task_id: str,
    paths: list[str] | None = None,
    *,
    write_task_refs: bool = False,
    semantic: bool = False,
    llm_backend: str = "codex-cli",
) -> dict[str, Any]:
    root = root.resolve()
    initialize(root)
    scanned = scan(root)
    links = generate(root, {str(task_id)}, write_task_refs)
    reviewed = capture(root, task_id, paths or [])
    result: dict[str, Any] = {
        "status": "knowledge_captured",
        "task_id": str(task_id),
        "source_revision": scanned.get("revision"),
        "resource_links": links,
        "reviewed_resources": reviewed,
    }
    if semantic:
        result["semantic_status"] = _semantic_enrich(root, str(task_id), llm_backend)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--write-task-refs", action="store_true")
    parser.add_argument("--semantic", action="store_true")
    parser.add_argument("--llm-backend", default="codex-cli")
    args = parser.parse_args(argv)
    result = run(
        args.repo_root.resolve(),
        str(args.task_id),
        args.path,
        write_task_refs=args.write_task_refs,
        semantic=args.semantic,
        llm_backend=args.llm_backend,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "knowledge_captured" else 1


if __name__ == "__main__":
    raise SystemExit(main())
