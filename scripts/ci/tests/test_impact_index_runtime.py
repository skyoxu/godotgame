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
from freeze_knowledge_context import freeze
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
            self.assertTrue(report["index_sha256"])
            self.assertTrue(report["index_path"].endswith("/impact-index.v1.json"))
            self.assertEqual("file", report["resolved_target"]["kind"])

    def test_handoff_binds_report_bytes_to_run_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            revision = self.make_repo(root)
            index = build_index(root, revision, trusted_ref="refs/heads/main")
            publish_index(root, index, root / "logs/ci")
            scan(root)
            bundle = {
                "schema": "godot-project-knowledge.context-candidates.v2",
                "status": "ready",
                "consumer": "chapter6",
                "task_id": "1",
                "revision": revision,
                "policy_revision": "test",
                "publication_state": "published-current",
                "bundle_sha256": "bundle",
                "candidates": [{"path": "Game.Core/FeatureService.cs"}],
            }
            frozen = freeze(
                bundle,
                {"decisions":[{"path":"Game.Core/FeatureService.cs","accepted":True,"reason":"test","satisfies":"test"}]},
            )
            report = ImpactAnalyzer(root).analyze(
                "Game.Core/FeatureService.cs",
                strict=True,
                frozen_context_sha256=frozen["frozen_sha256"],
            )
            report["status"] = "ok"
            report_bytes = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
            report_path = "logs/ci/impact/test/impact-report.v1.json"
            manifest = {
                "schema": "godot-project-impact.run-manifest.v1",
                "run_id": "test-run",
                "report_path": report_path,
                "report_sha256": __import__("hashlib").sha256(report_bytes).hexdigest(),
                "status": "ok",
                "revision": revision,
            }
            result = validate(
                frozen,
                report,
                repo_root=root,
                impact_report_bytes=report_bytes,
                run_manifest=manifest,
                impact_report_path=report_path,
            )
            self.assertEqual("ok", result["status"])

            bad_manifest = dict(manifest)
            bad_manifest["report_sha256"] = "0" * 64
            result = validate(
                frozen,
                report,
                repo_root=root,
                impact_report_bytes=report_bytes,
                run_manifest=bad_manifest,
                impact_report_path=report_path,
            )
            self.assertEqual("failed", result["status"])
            self.assertIn("impact_report_hash_mismatch", result["errors"])

            missing = validate(
                frozen,
                report,
                repo_root=root,
                impact_report_bytes=report_bytes,
                run_manifest=None,
                impact_report_path=report_path,
            )
            self.assertEqual("failed", missing["status"])
            self.assertIn("missing_impact_run_manifest", missing["errors"])

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

    def test_handoff_recomputes_frozen_content_hash_and_validates_index_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            revision = self.make_repo(root)
            index = build_index(root, revision, trusted_ref="refs/heads/main")
            published = publish_index(root, index, root / "logs/ci")
            scan(root)
            bundle = {
                "schema": "godot-project-knowledge.context-candidates.v2",
                "status": "ready",
                "consumer": "chapter6",
                "task_id": "1",
                "revision": revision,
                "policy_revision": "test",
                "publication_state": "published-current",
                "bundle_sha256": "bundle",
                "candidates": [{"path": "Game.Core/FeatureService.cs"}],
            }
            frozen = freeze(
                bundle,
                {"decisions":[{"path":"Game.Core/FeatureService.cs","accepted":True,"reason":"test","satisfies":"test"}]},
            )
            report = ImpactAnalyzer(root).analyze(
                "Game.Core/FeatureService.cs",
                strict=True,
                frozen_context_sha256=frozen["frozen_sha256"],
            )
            result = validate(frozen, report, repo_root=root, expected_consumer="chapter6", expected_task_id="1")
            self.assertEqual("ok", result["status"])

            tampered = json.loads(json.dumps(frozen))
            tampered["accepted_paths"].append("Game.Core/Other.cs")
            result = validate(tampered, report, repo_root=root)
            self.assertEqual("failed", result["status"])
            self.assertIn("frozen_content_hash_mismatch", result["errors"])

            index_path = root / published["index_path"]
            index_path.write_text("{}\n", encoding="utf-8")
            result = validate(frozen, report, repo_root=root)
            self.assertEqual("failed", result["status"])
            self.assertIn("index_hash_mismatch", result["errors"])




if __name__ == "__main__":
    unittest.main()
