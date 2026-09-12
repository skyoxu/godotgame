from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "scripts/python"
if str(PYTHON) not in sys.path:
    sys.path.insert(0, str(PYTHON))

from impact_analysis_handoff import validate
from impact_analysis_index import ImpactIndexError, build_index, publish_index
from impact_analyzer import ImpactAnalyzer
from impact_runtime import resolve_target
from project_health_knowledge import scan


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


class ImpactIndexRuntimeTests(unittest.TestCase):
    def make_repo(self, root: Path) -> str:
        git(root, "init", "-b", "main")
        git(root, "config", "user.email", "test@example.invalid")
        git(root, "config", "user.name", "Impact Test")
        (root / "scripts/python").mkdir(parents=True)
        (root / "Game.Core").mkdir()
        (root / "Game.Godot/Scenes").mkdir(parents=True)
        (root / "Game.Godot/Scripts").mkdir(parents=True)
        (root / "Game.Godot/Data").mkdir(parents=True)
        (root / "Tests.Godot").mkdir()
        config = {
            "schema": "godot-project-impact.analysis-config.v1",
            "revision": "test-v1",
            "include_prefixes": ["Game.Core/", "Game.Godot/", "Tests.Godot/"],
            "include_exact_paths": [],
            "include_extensions": [".cs", ".gd", ".tscn", ".json"],
            "max_file_bytes": 1048576,
            "relation_types": ["declares", "declares-config-pointer", "resource-reference", "scene-script", "text-symbol-reference"],
        }
        aliases = {"schema": "godot-project-impact.target-aliases.v1", "revision": "test-v1", "aliases": []}
        (root / "scripts/python/impact_analysis_config.v1.json").write_text(json.dumps(config), encoding="utf-8")
        (root / "scripts/python/impact_target_aliases.v1.json").write_text(json.dumps(aliases), encoding="utf-8")
        (root / "Game.Core/FeatureService.cs").write_text("public class FeatureService { public void Apply() {} }\n", encoding="utf-8")
        (root / "Game.Core/Other.cs").write_text("public class Other { public void FeatureService() {} }\n", encoding="utf-8")
        (root / "Game.Godot/Scripts/FeatureView.gd").write_text("extends Control\nfunc show_feature():\n    pass\n", encoding="utf-8")
        (root / "Game.Godot/Scenes/FeaturePanel.tscn").write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://Game.Godot/Scripts/FeatureView.gd" id="1"]\n[node name="FeaturePanel" type="Control"]\nscript = ExtResource("1")\n', encoding="utf-8")
        (root / "Game.Godot/Data/feature.json").write_text('{"feature":{"enabled":true,"limit":3}}\n', encoding="utf-8")
        (root / "Tests.Godot/test_feature.gd").write_text("extends GdUnitTestSuite\n# FeatureService\n", encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-m", "seed")
        return git(root, "rev-parse", "HEAD")

    def test_index_scene_config_relation_and_strict_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            revision = self.make_repo(root)
            index = build_index(root, revision, trusted_ref="refs/heads/main")
            self.assertTrue(any(item.get("type") == "scene-script" and item.get("confirmed") for item in index["relations"]))
            pointer = resolve_target(index, "Game.Godot/Data/feature.json#/feature/enabled")
            self.assertEqual("config-pointer", pointer["kind"])
            self.assertEqual("boolean", pointer["value_type"])
            self.assertTrue(any(item.get("type") == "declares-config-pointer" and item.get("to") == pointer["id"] for item in index["relations"]))
            publish_index(root, index, root / "logs/ci")
            scan(root)
            report = ImpactAnalyzer(root).analyze("Game.Core/FeatureService.cs", strict=True, frozen_context_sha256="freeze-123")
            self.assertEqual(index["index_id"], report["index_id"])
            self.assertEqual("freeze-123", report["frozen_context_sha256"])
            self.assertEqual("file", report["resolved_target"]["kind"])

    def test_natural_language_ambiguous_symbols_and_missing_pointers_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            revision = self.make_repo(root)
            index = build_index(root, revision)
            with self.assertRaises(ImpactIndexError):
                resolve_target(index, "please change the feature flow")
            # FeatureService is both a type declaration and a method name in this fixture.
            with self.assertRaises(ImpactIndexError) as caught:
                resolve_target(index, "FeatureService")
            self.assertEqual("underqualified_target", caught.exception.code)
            with self.assertRaises(ImpactIndexError) as missing:
                resolve_target(index, "Game.Godot/Data/feature.json#/feature/missing")
            self.assertEqual("unsupported_target", missing.exception.code)

    def test_handoff_requires_exact_frozen_hash(self):
        frozen = {"consumer": "chapter6", "revision": "a" * 40, "frozen_sha256": "freeze-a"}
        impact = {"mode": "strict", "revision": "a" * 40, "frozen_context_sha256": "freeze-b", "index_id": "idx-x", "target": "x"}
        result = validate(frozen, impact)
        self.assertEqual("failed", result["status"])
        self.assertIn("frozen_hash_mismatch", result["errors"])


if __name__ == "__main__":
    unittest.main()
