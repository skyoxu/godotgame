from __future__ import annotations

import sys
import unittest
from pathlib import Path

PYTHON_SCRIPTS = Path(__file__).resolve().parents[2] / "python"
if str(PYTHON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PYTHON_SCRIPTS))

from chapter6_knowledge import _semantic_prompt_entries, _validate_semantic_entries


class SemanticKnowledgeCiTests(unittest.TestCase):
    def entries(self):
        return [
            {"id":"config:7:Game.Core/Data/settings.json","task_id":"7","path":"Game.Core/Data/settings.json","kind":"config","parameters":[{"pointer":"/speed","value":3,"line":2,"kind":"numeric_parameter"}],"bindings":[]},
            {"id":"asset:7:Game.Godot/Art/icon.png","task_id":"7","path":"Game.Godot/Art/icon.png","kind":"asset","parameters":[],"bindings":[{"source":"Game.Godot/Scripts/View.gd","line":12,"evidence":"icon = preload(...)"}]},
            {"id":"scene:7:Game.Godot/Scenes/View.tscn","task_id":"7","path":"Game.Godot/Scenes/View.tscn","kind":"scene","parameters":[],"bindings":[{"node_path":"Root/Icon","type":"TextureRect","line":8,"properties":[]}]},
        ]

    def test_prompt_exposes_only_real_evidence(self):
        prompt = _semantic_prompt_entries(self.entries())
        self.assertEqual("/speed", next(item for item in prompt if item["kind"]=="config")["available_parameters"][0]["pointer"])
        self.assertEqual("Root/Icon", next(item for item in prompt if item["kind"]=="scene")["available_bindings"][0]["node_path"])

    def test_invented_pointer_is_rejected(self):
        valid, _, reason = _validate_semantic_entries([{"path":"Game.Core/Data/settings.json","parameters":[{"pointer":"/fake","meaning":"x"}],"bindings":[]}], self.entries())
        self.assertFalse(valid)
        self.assertIn("unknown parameter pointer", reason or "")

    def test_exact_asset_and_scene_bindings_are_accepted(self):
        model = [
            {"path":"Game.Godot/Art/icon.png","parameters":[],"bindings":[{"source":"Game.Godot/Scripts/View.gd","line":12,"meaning":"displayed icon"}]},
            {"path":"Game.Godot/Scenes/View.tscn","parameters":[],"bindings":[{"node_path":"Root/Icon","line":8,"meaning":"player-facing node"}]},
        ]
        valid, normalized, reason = _validate_semantic_entries(model, self.entries())
        self.assertTrue(valid, reason)
        self.assertEqual("static_binding_semantic_explanation", normalized[0]["bindings"][0]["evidence_status"])


if __name__ == "__main__":
    unittest.main()
