"""Deterministic, non-blocking Chapter 6 Godot element capture."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from _godot_scene_graph import scene_graph_for_revision
from project_health_knowledge import latest, write_json

GODOT_PATH_SUFFIXES = (
    ".tscn", ".gd", ".cs", ".tres", ".res", ".json", ".csv", ".cfg", ".ini",
    ".yaml", ".yml", ".toml", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif",
    ".wav", ".ogg", ".mp3",
)


def _changed_paths(root: Path) -> set[str]:
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"], cwd=root, text=True, encoding="utf-8",
            errors="replace", capture_output=True, check=False,
        )
        return {line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()}
    except OSError:
        return set()


def capture_element_manifest(root: Path, task_id: str, source_revision: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    state = latest(root)
    revision = source_revision or str(state.get("revision") or "")
    graph = scene_graph_for_revision(root, revision)
    links_path = root / "docs/knowledge/generated/task-resource-links.json"
    links = json.loads(links_path.read_text(encoding="utf-8-sig")) if links_path.exists() else {"generated": []}
    entries = [entry for entry in links.get("generated", []) if isinstance(entry, dict) and str(entry.get("task_id")) == str(task_id)]

    elements: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        path = str(entry.get("path") or "").replace("\\", "/")
        if not path or path in seen:
            continue
        seen.add(path)
        item: dict[str, Any] = {
            "path": path,
            "kind": entry.get("kind"),
            "status": "verified" if str(entry.get("confidence") or "") == "confirmed" else "inferred",
            "evidence": entry.get("evidence", []),
        }
        if item["kind"] == "scene" and path in graph.get("nodes", {}):
            scene = graph["nodes"][path]
            item["nodes"] = [
                {"path": f"{node.get('parent') or '.'}/{node.get('name') or '(unnamed)'}", "type": node.get("type"), "line": node.get("line")}
                for node in scene.get("nodes", [])
            ]
            item["scripts"] = scene.get("functional_summary", {}).get("scripts", [])
            item["events"] = scene.get("functional_summary", {}).get("events", [])
            item["scene_classification"] = scene.get("classification")
        if item["kind"] in {"config", "asset"}:
            item["readers"] = entry.get("readers", [])
        elements.append(item)

    changed = _changed_paths(root)
    linked = {item["path"] for item in elements}
    for path in sorted(changed - linked):
        if not path.casefold().endswith(GODOT_PATH_SUFFIXES):
            continue
        suffix = Path(path).suffix.casefold()
        kind = "scene" if suffix == ".tscn" else "script" if suffix in {".gd", ".cs"} else "resource"
        elements.append({"path": path, "kind": kind, "status": "unmapped", "evidence": [{"source": "git-diff"}]})

    gaps: list[dict[str, Any]] = []
    for item in elements:
        if item["status"] == "unmapped":
            gaps.append({"severity": "P1" if item["kind"] in {"scene", "script"} else "P2", "path": item["path"], "reason": "Changed Godot element has no task resource binding."})
        elif item["kind"] in {"scene", "asset", "config"} and not any(isinstance(evidence, dict) and evidence.get("focus") == "core" for evidence in item.get("evidence", [])):
            gaps.append({"severity": "P2", "path": item["path"], "reason": "Resource is recorded but lacks confirmed semantic focus."})

    payload = {
        "schema": "godot-project-knowledge.chapter6-element-capture.v1",
        "task_id": str(task_id), "source_revision": revision, "elements": elements,
        "documentation_gaps": gaps, "blocking": False,
    }
    output = root / "docs/knowledge/generated" / f"chapter6-task-{task_id}-elements.json"
    write_json(output, payload)
    gaps_output = root / "docs/knowledge/generated" / f"chapter6-task-{task_id}-documentation-gaps.md"
    lines = [f"# Chapter 6 documentation gaps: task {task_id}", "", "Generated from deterministic evidence. These gaps are non-blocking follow-up items.", ""]
    lines.extend((f"- [{gap['severity']}] `{gap['path']}`: {gap['reason']}" for gap in gaps))
    if not gaps:
        lines.append("- No documentation gaps detected.")
    gaps_output.parent.mkdir(parents=True, exist_ok=True)
    gaps_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": output.relative_to(root).as_posix(), "elements": len(elements), "documentation_gaps": len(gaps), "blocking": False}
