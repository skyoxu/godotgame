from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from chapter6_knowledge import capture
from freeze_knowledge_context import freeze
from impact_analyzer import ImpactAnalyzer
from prepare_knowledge_context import prepare
from project_health_godot import build_navigation
from project_health_knowledge import (
    query,
    safe_file,
    save_config,
    scan,
    snapshot_bytes,
    snapshot_text,
    task_rows,
)
from project_health_runtime import eligibility
from workflow_chapter_knowledge_overlay import BEGIN, END, apply_overlay


def config(bindings: dict[str, str], *, gdd=None, aliases=None, scenes=None, extensions=None) -> dict:
    return {
        "source_path_bindings": bindings,
        "source_paths": list(bindings.values()),
        "gdd_paths": gdd or [],
        "task_scene_bindings": scenes or [],
        "query_aliases": aliases or {},
        "include_extensions": extensions or [".md", ".txt", ".json", ".cs", ".gd", ".tscn", ".tres", ".cfg"],
        "max_file_bytes": 512000,
        "max_asset_bytes": 16 * 1024 * 1024,
        "max_results": 50,
    }


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


class TemplateKnowledgeImpactTests(unittest.TestCase):
    def test_empty_template_and_deterministic_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/spec.md").write_text("PlayerService emits ReadyEvent\n", encoding="utf-8")
            state = scan(root, config({"docs": "docs"}, extensions=[".md"]))
            self.assertEqual(1, state["counts"]["files"])
            self.assertEqual("docs/spec.md", query(root, "PlayerService")["results"][0]["path"])

    def test_aliases_and_actionable_categories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Game.Core").mkdir()
            (root / "Tests.Godot").mkdir()
            (root / "docs/gdd").mkdir(parents=True)
            (root / "Game.Core/Feature.cs").write_text("class FeatureService {}\n", encoding="utf-8")
            (root / "Tests.Godot/test_feature.gd").write_text("FeatureService\n", encoding="utf-8")
            (root / "docs/gdd/feature.md").write_text("功能 FeatureService\n", encoding="utf-8")
            save_config(root, config(
                {"domain_code": "Game.Core", "engine_tests": "Tests.Godot"},
                gdd=["docs/gdd"], aliases={"功能": ["FeatureService"]},
                extensions=[".md", ".cs", ".gd"],
            ))
            scan(root)
            result = query(root, "功能")
            self.assertIn("FeatureService", result["queries"])
            self.assertTrue(result["actionable"]["code"])
            self.assertTrue(result["actionable"]["tests"])
            self.assertTrue(result["gdd_supplements"])

    def test_git_scan_is_bound_to_local_main_not_dirty_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-b", "main")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "config", "user.name", "Project Health Test")
            (root / "docs").mkdir()
            path = root / "docs/spec.md"
            path.write_text("main-only evidence\n", encoding="utf-8")
            git(root, "add", "docs/spec.md")
            git(root, "commit", "-m", "seed")
            main_sha = git(root, "rev-parse", "refs/heads/main")
            path.write_text("dirty workspace evidence\n", encoding="utf-8")
            state = scan(root, config({"docs": "docs"}, extensions=[".md"]))
            self.assertEqual("main", state["snapshot_mode"])
            self.assertEqual(main_sha, state["revision"])
            self.assertEqual("main-only evidence\n", snapshot_text(root, "docs/spec.md", state))
            self.assertFalse(query(root, "dirty workspace")["results"])

    def test_binary_asset_enters_bounded_snapshot_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "Game.Godot/Assets/icon.png"
            asset.parent.mkdir(parents=True)
            raw = b"\x89PNG\r\n\x1a\nproject-health-test"
            asset.write_bytes(raw)
            state = scan(root, config({"engine_code": "Game.Godot"}, extensions=[".gd", ".tscn"]))
            record = next(item for item in state["records"] if item["path"] == "Game.Godot/Assets/icon.png")
            self.assertTrue(record["asset"])
            self.assertFalse(record["searchable"])
            self.assertEqual(raw, snapshot_bytes(root, record["path"], state))

    def test_impact_text_reference_is_not_confirmed_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/spec.md").write_text("PlayerService\n", encoding="utf-8")
            scan(root, config({"docs": "docs"}, extensions=[".md"]))
            report = ImpactAnalyzer(root).analyze("PlayerService")
            self.assertFalse(report["evidence"][0]["confirmed"])

    def test_freeze_requires_explicit_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/a.md").write_text("intent", encoding="utf-8")
            scan(root, config({"docs": "docs"}, extensions=[".md"]))
            bundle = prepare(root, "chapter6", "intent", "1")
            with self.assertRaises(ValueError):
                freeze(bundle, {"decisions": [{"path": "docs/a.md", "accepted": True, "reason": ""}]})

    def test_resource_capture_never_invents_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual("skipped", capture(root, "1", [])["status"])
            with self.assertRaises(ValueError):
                capture(root, "1", ["missing.tscn"])

    def test_safe_file_rejects_escape_and_windows_style_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with self.assertRaises(ValueError):
                safe_file(root, "../outside")
            with self.assertRaises(ValueError):
                safe_file(root, "Game.Godot\\scene.tscn")

    def test_task_rows_use_tasks_json_ssot_and_join_gameplay_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / ".taskmaster/tasks"
            task_dir.mkdir(parents=True)
            (task_dir / "tasks.json").write_text(json.dumps({
                "master": {"tasks": [{"id": 7, "title": "Feature", "status": "done", "dependencies": [2]}]}
            }), encoding="utf-8")
            (task_dir / "tasks_gameplay.json").write_text(json.dumps([
                {"taskmaster_id": 7, "test_refs": ["Tests.Godot/tests/test_feature.gd"], "gameplay_note": "view"}
            ]), encoding="utf-8")
            scan(root, config({"tasks": ".taskmaster/tasks"}, extensions=[".json"]))
            rows = task_rows(root)
            self.assertEqual(["7"], [row["id"] for row in rows])
            self.assertEqual("Feature", rows[0]["title"])
            self.assertIn(".taskmaster/tasks/tasks_gameplay.json", rows[0]["mappings"])

    def test_runtime_eligibility_uses_only_existing_snapshot_test_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / ".taskmaster/tasks"
            task_dir.mkdir(parents=True)
            test_dir = root / "Tests.Godot/tests/Gameplay"
            test_dir.mkdir(parents=True)
            (test_dir / "test_feature.gd").write_text("extends GdUnitTestSuite\n", encoding="utf-8")
            (task_dir / "tasks_gameplay.json").write_text(json.dumps({
                "tasks": [{
                    "id": "7", "title": "Feature",
                    "test_refs": [
                        "Tests.Godot/tests/Gameplay/test_feature.gd",
                        "Tests.Godot/tests/Gameplay/missing.gd",
                    ],
                }]
            }), encoding="utf-8")
            save_config(root, config(
                {"tasks": ".taskmaster/tasks", "engine_tests": "Tests.Godot"},
                extensions=[".json", ".gd"],
            ))
            scan(root)
            result = eligibility(root)
            self.assertEqual(1, result["eligible_count"])
            self.assertTrue(result["tasks"][0]["gameplay"])
            self.assertEqual(["Tests.Godot/tests/Gameplay/test_feature.gd"], result["tasks"][0]["test_refs"])

    def test_static_godot_navigation_requires_real_attachment_and_witness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scene_dir = root / "Game.Godot/Scenes"
            script_dir = root / "Game.Godot/Scripts"
            data_dir = root / "Game.Godot/Data"
            task_dir = root / ".taskmaster/tasks"
            scene_dir.mkdir(parents=True)
            script_dir.mkdir(parents=True)
            data_dir.mkdir(parents=True)
            task_dir.mkdir(parents=True)
            (script_dir / "FeaturePanel.gd").write_text(
                'extends Control\nconst DATA = "Game.Godot/Data/feature.json"\nfunc _apply_feature() -> void:\n    pass\n',
                encoding="utf-8",
            )
            (scene_dir / "FeaturePanel.tscn").write_text(
                '[gd_scene load_steps=2 format=3]\n\n'
                '[ext_resource type="Script" path="res://Game.Godot/Scripts/FeaturePanel.gd" id="1"]\n\n'
                '[node name="FeaturePanel" type="Control"]\nscript = ExtResource("1")\n',
                encoding="utf-8",
            )
            (data_dir / "feature.json").write_text(
                '{"feature":{"id":"feature.basic","limit":3,"weight":1}}', encoding="utf-8"
            )
            (task_dir / "tasks.json").write_text(json.dumps({
                "master": {"tasks": [{"id": 7, "title": "Feature", "status": "pending"}]}
            }), encoding="utf-8")
            binding = {
                "task_id": "7",
                "scene": "Game.Godot/Scenes/FeaturePanel.tscn",
                "node": ".",
                "script": "Game.Godot/Scripts/FeaturePanel.gd",
                "witness": "func _apply_feature() -> void:",
                "configs": [{"path": "Game.Godot/Data/feature.json", "pointers": ["/feature/limit"]}],
            }
            save_config(root, config(
                {"tasks": ".taskmaster/tasks", "engine_code": "Game.Godot"},
                scenes=[binding], extensions=[".json", ".gd", ".tscn"],
            ))
            state = scan(root)
            row = task_rows(root, state)[0]
            nav = build_navigation(root, "7", task=row["task"], mappings=row["mappings"], bindings=[binding], state=state)
            self.assertEqual("static_attached", nav["static"]["status"])
            self.assertEqual("Game.Godot/Scripts/FeaturePanel.gd", nav["static"]["scenes"][0]["script"])
            config_row = next(item for item in nav["configs"] if item["path"] == "Game.Godot/Data/feature.json")
            self.assertEqual(["/feature/limit"], [item["pointer"] for item in config_row["confirmed_fields"]])
            bad = {**binding, "witness": "func missing()"}
            bad_nav = build_navigation(root, "7", task=row["task"], mappings=row["mappings"], bindings=[bad], state=state)
            self.assertNotEqual("static_attached", bad_nav["static"]["status"])
            self.assertTrue(bad_nav["static"]["invalid_declarations"])

    def test_workflow_overlay_is_single_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("# Skill\n\n## Idempotent Procedure\n\n1. Original\n", encoding="utf-8")
            body = "## Knowledge / Impact Contract\n\n- Rule"
            self.assertTrue(apply_overlay(path, body))
            once = path.read_text(encoding="utf-8")
            self.assertIn(BEGIN, once)
            self.assertIn(END, once)
            self.assertFalse(apply_overlay(path, body))
            twice = path.read_text(encoding="utf-8")
            self.assertEqual(once, twice)
            self.assertEqual(1, twice.count(BEGIN))


if __name__ == "__main__":
    unittest.main()
