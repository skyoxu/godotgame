from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

import generate_knowledge_links as links


class GenerateKnowledgeLinksTests(unittest.TestCase):
    def test_full_rebuild_replaces_stale_generated_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "docs/knowledge/generated/task-resource-links.json"
            out.parent.mkdir(parents=True)
            out.write_text(
                json.dumps({
                    "schema": "godot-project-knowledge.task-resource-links.v2",
                    "generated": [{
                        "id": "scene:old:Old.tscn",
                        "task_id": "old",
                        "path": "Old.tscn",
                        "source_revision": "old",
                    }],
                }),
                encoding="utf-8",
            )
            state = {
                "revision": "a" * 40,
                "config": {"task_scene_bindings": []},
            }
            rows = [{
                "id": "2",
                "title": "Neutral task",
                "task": {"id": 2, "title": "Neutral task", "test_refs": []},
                "mappings": {},
            }]
            navigation = {
                "configs": [{"path": "Data/feature.json", "focus": "core"}],
                "assets": [],
                "scenes": [],
                "code": [],
            }
            with mock.patch.object(links, "latest", return_value=state), \
                    mock.patch.object(links, "task_rows", return_value=rows), \
                    mock.patch.object(links, "build_navigation", return_value=navigation):
                result = links.generate(root)

            self.assertEqual(1, result["entries"])
            rebuilt = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(["2"], rebuilt["task_ids"])
            self.assertEqual(["2"], sorted({item["task_id"] for item in rebuilt["generated"]}))
            self.assertNotIn("Old.tscn", json.dumps(rebuilt))

    def test_cli_without_task_ids_requests_full_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(links, "generate", return_value={"status": "ok"}) as generate:
            self.assertEqual(0, links.main(["--repo-root", tmp]))
        self.assertIsNone(generate.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
