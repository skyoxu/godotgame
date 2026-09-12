from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chapter6_knowledge import _semantic_prompt_entries, _validate_semantic_entries


class SemanticKnowledgeTests(unittest.TestCase):
    def sample_entries(self):
        return [
            {
                "id": "config:7:Game.Core/Data/settings.json",
                "task_id": "7",
                "path": "Game.Core/Data/settings.json",
                "kind": "config",
                "parameters": [
                    {"pointer": "/speed", "value": 3, "line": 2, "kind": "numeric_parameter"},
                    {"pointer": "/label", "value": "fast", "line": 3, "kind": "data_field"},
                ],
                "bindings": [],
            },
            {
                "id": "asset:7:Game.Godot/Art/icon.png",
                "task_id": "7",
                "path": "Game.Godot/Art/icon.png",
                "kind": "asset",
                "parameters": [],
                "bindings": [
                    {"source": "Game.Godot/Scripts/View.gd", "line": 12, "evidence": "icon = preload(...)"}
                ],
            },
            {
                "id": "scene:7:Game.Godot/Scenes/View.tscn",
                "task_id": "7",
                "path": "Game.Godot/Scenes/View.tscn",
                "kind": "scene",
                "parameters": [],
                "bindings": [
                    {"node_path": "Root/Icon", "type": "TextureRect", "line": 8, "properties": []}
                ],
            },
        ]

    def test_prompt_only_exposes_bounded_real_evidence(self):
        prompt = _semantic_prompt_entries(self.sample_entries())
        config = next(item for item in prompt if item["kind"] == "config")
        self.assertEqual(["/speed", "/label"], [item["pointer"] for item in config["available_parameters"]])
        asset = next(item for item in prompt if item["kind"] == "asset")
        self.assertEqual("Game.Godot/Scripts/View.gd", asset["available_bindings"][0]["source"])
        scene = next(item for item in prompt if item["kind"] == "scene")
        self.assertEqual("Root/Icon", scene["available_bindings"][0]["node_path"])

    def test_validator_rejects_invented_pointer(self):
        model = [{
            "path": "Game.Core/Data/settings.json",
            "parameters": [{"pointer": "/invented", "meaning": "not real"}],
            "bindings": [],
        }]
        valid, _, reason = _validate_semantic_entries(model, self.sample_entries())
        self.assertFalse(valid)
        self.assertIn("unknown parameter pointer", reason or "")

    def test_validator_rejects_invented_scene_binding(self):
        model = [
            {
                "path": "Game.Godot/Art/icon.png",
                "parameters": [],
                "bindings": [{"source": "Game.Godot/Scripts/View.gd", "line": 12, "meaning": "icon source"}],
            },
            {
                "path": "Game.Godot/Scenes/View.tscn",
                "parameters": [],
                "bindings": [{"node_path": "Root/Missing", "line": 99, "meaning": "invented"}],
            },
        ]
        valid, _, reason = _validate_semantic_entries(model, self.sample_entries())
        self.assertFalse(valid)
        self.assertIn("unknown or unexplained scene binding", reason or "")

    def test_validator_accepts_exact_evidence_and_preserves_actual_values(self):
        model = [
            {
                "path": "Game.Core/Data/settings.json",
                "explanation": "Settings used by the feature.",
                "parameters": [{"pointer": "/speed", "meaning": "Movement tuning"}],
                "bindings": [],
            },
            {
                "path": "Game.Godot/Art/icon.png",
                "parameters": [],
                "bindings": [{"source": "Game.Godot/Scripts/View.gd", "line": 12, "meaning": "Displayed icon"}],
            },
            {
                "path": "Game.Godot/Scenes/View.tscn",
                "parameters": [],
                "bindings": [{"node_path": "Root/Icon", "line": 8, "meaning": "Player-facing icon node"}],
            },
        ]
        valid, normalized, reason = _validate_semantic_entries(model, self.sample_entries())
        self.assertTrue(valid, reason)
        config = next(item for item in normalized if item["kind"] == "config")
        self.assertEqual(3, config["parameters"][0]["value"])
        self.assertEqual(2, config["parameters"][0]["line"])
        self.assertEqual("field_exists_semantic_inference", config["parameters"][0]["evidence_status"])


if __name__ == "__main__":
    unittest.main()
