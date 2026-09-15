from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

from knowledge_publication_freshness import publication_freshness_reason


class KnowledgePublicationFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        subprocess.check_call(["git", "init", "-b", "main"], cwd=self.repo, stdout=subprocess.DEVNULL)
        subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=self.repo)
        subprocess.check_call(["git", "config", "user.name", "Template Test"], cwd=self.repo)
        (self.repo / "AGENTS.md").write_text("# Repository Guide\n", encoding="utf-8")
        (self.repo / "README.md").write_text("# Template\n", encoding="utf-8")
        subprocess.check_call(["git", "add", "."], cwd=self.repo)
        subprocess.check_call(["git", "commit", "-m", "baseline"], cwd=self.repo, stdout=subprocess.DEVNULL)
        self.published = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def commit(self, path: str, content: str) -> None:
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        subprocess.check_call(["git", "add", path], cwd=self.repo)
        subprocess.check_call(["git", "commit", "-m", f"change {path}"], cwd=self.repo, stdout=subprocess.DEVNULL)

    def reason(self) -> str | None:
        return publication_freshness_reason(self.repo, self.published, "refs/heads/main", {"rules": []})

    def test_generated_and_unrelated_changes_do_not_stale_publication(self) -> None:
        self.commit("knowledge/catalogs/generated.json", "{}\n")
        self.commit("scripts/python/project_health_knowledge.py", "# unrelated investigation helper\n")
        self.assertIsNone(self.reason())

    def test_authoritative_source_change_stales_publication(self) -> None:
        self.commit("AGENTS.md", "# Repository Guide\nUpdated authority.\n")
        self.assertEqual(self.reason(), "authority_inputs_changed")

    def test_control_plane_change_stales_publication(self) -> None:
        self.commit("scripts/python/knowledge_locator.py", "# changed formal consumer behavior\n")
        self.assertEqual(self.reason(), "authority_inputs_changed")

    def test_delivery_knowledge_change_stales_publication(self) -> None:
        self.commit("execution-plans/example.md", "# Plan\nStatus: draft\n")
        self.assertEqual(self.reason(), "authority_inputs_changed")


if __name__ == "__main__":
    unittest.main()
