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

from knowledge_locator import locate
from prepare_knowledge_context import prepare
from publish_knowledge_catalog import PublicationBlocked, check_current, publish


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


class KnowledgeCatalogPublicationTests(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        git(root, "init", "-b", "main")
        git(root, "config", "user.email", "test@example.invalid")
        git(root, "config", "user.name", "KCP Test")
        (root / "docs/prd").mkdir(parents=True)
        (root / "knowledge/policies").mkdir(parents=True)
        (root / "knowledge/evaluation").mkdir(parents=True)
        (root / "AGENTS.md").write_text("# Repository Rules\nUse FeatureService.\n", encoding="utf-8")
        (root / "docs/prd/feature.md").write_text("# Feature System\nFeatureService applies deterministic behavior.\n", encoding="utf-8")
        policies = {
            "schema": "godot-project-knowledge.consumer-policies.v2",
            "policy_revision": "test-v1",
            "consumers": {"chapter6": {"task_id_required": True, "freeze_before_red": True}},
            "policies": [{
                "consumer": "chapter6",
                "domains": ["toolchain", "game-design", "game-runtime", "delivery"],
                "visibility": ["active", "dependency", "conditional"],
                "lifecycles": ["repository-source"],
                "statuses": ["active", "conditional", "historical"],
                "historical_mode": "exact-only",
                "path_prefixes": ["docs/prd/"],
                "exact_paths": ["AGENTS.md"],
                "max_candidates": 12,
            }],
        }
        exclusions = {"schema": "godot-project-knowledge.source-exclusions.v1", "rules": []}
        suite = {"schema": "godot-project-knowledge.evaluation-suite.v1", "cases": [{
            "id": "feature",
            "consumer": "chapter6",
            "query": "FeatureService",
            "expected_status": "matched",
            "must_include_paths": ["docs/prd/feature.md"],
        }]}
        (root / "knowledge/policies/consumer-policies.v1.json").write_text(json.dumps(policies), encoding="utf-8")
        (root / "knowledge/policies/source-exclusions.v1.json").write_text(json.dumps(exclusions), encoding="utf-8")
        (root / "knowledge/evaluation/queries.v1.json").write_text(json.dumps(suite), encoding="utf-8")
        git(root, "add", ".")
        git(root, "commit", "-m", "seed")

    def test_publish_check_locator_and_formal_prepare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            result = publish(root)
            self.assertEqual("published", result["status"])
            self.assertEqual("passed", result["evaluation"]["status"])
            self.assertEqual("current", check_current(root)["status"])
            located = locate(root, consumer="chapter6", text="FeatureService", task_id="7", require_published=True)
            self.assertEqual("published-current", located["publication_state"])
            self.assertEqual("matched", located["status"])
            self.assertEqual("docs/prd/feature.md", located["candidates"][0]["path"])
            bundle = prepare(root, "chapter6", "FeatureService", "7")
            self.assertEqual("ready", bundle["status"])
            self.assertEqual("published-current", bundle["publication_state"])

    def test_dirty_policy_blocks_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            policy = root / "knowledge/policies/consumer-policies.v1.json"
            policy.write_text(policy.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaises(PublicationBlocked) as caught:
                publish(root)
            self.assertEqual("dirty_control_plane", caught.exception.reason)


if __name__ == "__main__":
    unittest.main()
