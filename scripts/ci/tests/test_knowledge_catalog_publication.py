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
from project_health_knowledge import scan
from publish_knowledge_catalog import PublicationBlocked, check_current, publish, restore_lkg


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
            candidate_paths = {item["path"] for item in located["candidates"]}
            self.assertIn("docs/prd/feature.md", candidate_paths)
            self.assertIn("AGENTS.md", candidate_paths)
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

    def test_failed_evaluation_does_not_advance_current_or_lkg(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            publish(root)
            current_path = root / "knowledge/indexes/current.json"
            lkg_path = root / "knowledge/indexes/last-known-good.json"
            current_before = current_path.read_text(encoding="utf-8")
            lkg_before = lkg_path.read_text(encoding="utf-8")

            suite_path = root / "knowledge/evaluation/queries.v1.json"
            suite = json.loads(suite_path.read_text(encoding="utf-8"))
            suite["cases"][0]["must_include_paths"] = ["docs/prd/does-not-exist.md"]
            suite_path.write_text(json.dumps(suite), encoding="utf-8")
            git(root, "add", "knowledge/evaluation/queries.v1.json")
            git(root, "commit", "-m", "make evaluation fail")

            with self.assertRaises(PublicationBlocked) as caught:
                publish(root)
            self.assertEqual("repository_query_evaluation_failed", caught.exception.reason)
            self.assertEqual(current_before, current_path.read_text(encoding="utf-8"))
            self.assertEqual(lkg_before, lkg_path.read_text(encoding="utf-8"))

    def test_restore_lkg_rebuilds_current_and_canonical_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            publish(root)
            lkg_path = root / "knowledge/indexes/last-known-good.json"
            expected_pointer = json.loads(lkg_path.read_text(encoding="utf-8"))
            (root / "knowledge/indexes/current.json").write_text("{}\n", encoding="utf-8")
            (root / "knowledge/catalogs/repository-knowledge-catalog.v1.json").write_text("{}\n", encoding="utf-8")

            result = restore_lkg(root)
            self.assertEqual("restored", result["status"])
            current = json.loads((root / "knowledge/indexes/current.json").read_text(encoding="utf-8"))
            self.assertEqual(expected_pointer, current)
            self.assertEqual("current", check_current(root)["status"])

    def test_ephemeral_locator_uses_exact_project_health_scan_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            state = scan(root)
            scanned_revision = state["revision"]
            (root / "docs/prd/later.md").write_text("FeatureService later evidence.\n", encoding="utf-8")
            git(root, "add", "docs/prd/later.md")
            git(root, "commit", "-m", "advance main after scan")
            self.assertNotEqual(scanned_revision, git(root, "rev-parse", "refs/heads/main"))

            located = locate(root, consumer="chapter6", text="FeatureService", task_id="7", require_published=False)
            self.assertEqual("ephemeral", located["publication_state"])
            self.assertEqual(scanned_revision, located["revision"])
            self.assertNotIn("docs/prd/later.md", {item["path"] for item in located["candidates"]})


if __name__ == "__main__":
    unittest.main()
