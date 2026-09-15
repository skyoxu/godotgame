from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

from chapter6_element_capture import capture_element_manifest


class Chapter6ElementCaptureTests(unittest.TestCase):
    def test_capture_projects_neutral_scene_evidence_without_business_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Scenes").mkdir()
            (root / "Scripts").mkdir()
            (root / "docs/knowledge/generated").mkdir(parents=True)
            (root / "logs/ci/project-health-knowledge").mkdir(parents=True)
            (root / "project.godot").write_text('[application]\nrun/main_scene="res://Scenes/Main.tscn"\n', encoding="utf-8")
            (root / "Scenes/Main.tscn").write_text('[gd_scene]\n[ext_resource type="Script" path="res://Scripts/Feature.gd" id="1"]\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n', encoding="utf-8")
            (root / "Scripts/Feature.gd").write_text("extends Node\n", encoding="utf-8")
            (root / "logs/ci/project-health-knowledge/latest.json").write_text(json.dumps({"revision": "workspace", "records": [], "config": {}}), encoding="utf-8")
            (root / "docs/knowledge/generated/task-resource-links.json").write_text(json.dumps({"generated": [{"task_id": "1", "path": "Scenes/Main.tscn", "kind": "scene", "confidence": "confirmed", "evidence": [{"focus": "core", "source": "neutral-fixture"}]}]}), encoding="utf-8")

            result = capture_element_manifest(root, "1", "workspace")
            payload = json.loads((root / result["path"]).read_text(encoding="utf-8"))

            self.assertEqual(payload["schema"], "godot-project-knowledge.chapter6-element-capture.v1")
            self.assertFalse(payload["blocking"])
            scene = next(item for item in payload["elements"] if item["path"] == "Scenes/Main.tscn")
            self.assertEqual(scene["status"], "verified")
            self.assertIn("Scripts/Feature.gd", scene["scripts"])
            self.assertEqual(payload["documentation_gaps"], [])
            self.assertTrue((root / "docs/knowledge/generated/chapter6-task-1-documentation-gaps.md").exists())


if __name__ == "__main__":
    unittest.main()
