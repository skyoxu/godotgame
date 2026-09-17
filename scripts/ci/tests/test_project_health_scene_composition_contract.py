from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class ProjectHealthSceneCompositionContractTests(unittest.TestCase):
    def test_scene_composition_is_template_safe_and_refresh_synchronized(self) -> None:
        script = (ROOT / "scripts/python/project_health_scenes.js").read_text(encoding="utf-8")
        self.assertIn("Scene composition", script)
        self.assertIn("routeTreeClosure", script)
        self.assertIn("include-unreachable", script)
        self.assertIn("if(activeView==='composition')renderComposition();", script)
        self.assertIn("compositionToolbar.hidden=graphVisible", script)
        self.assertIn("row.dataset.resourcePath=item.path", script)
        self.assertNotIn("Game.Godot/Scenes/", script)
        self.assertNotIn("Task ", script)
        self.assertNotIn("simulated-llm", script)


if __name__ == "__main__":
    unittest.main()
