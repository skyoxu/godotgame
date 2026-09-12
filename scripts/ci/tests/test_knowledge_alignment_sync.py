from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "scripts/python"
if str(PYTHON) not in sys.path:
    sys.path.insert(0, str(PYTHON))

from sync_knowledge_impact_alignment import collect_expected


class KnowledgeImpactAlignmentSyncTests(unittest.TestCase):
    def test_generated_alignment_surfaces_are_current(self):
        stale = []
        for path, expected in collect_expected(ROOT).items():
            if path.read_text(encoding="utf-8") != expected:
                stale.append(path.relative_to(ROOT).as_posix())
        self.assertFalse(stale, "Knowledge/Impact alignment drift: " + ", ".join(stale))

    def test_dev_cli_exposes_stable_knowledge_and_impact_commands(self):
        text = (ROOT / "scripts/python/dev_cli.py").read_text(encoding="utf-8")
        for command in (
            "knowledge-publish",
            "knowledge-check",
            "knowledge-restore-lkg",
            "knowledge-locate",
            "knowledge-context",
            "impact-build-index",
            "impact-analyze",
        ):
            self.assertIn(f'sub.add_parser("{command}"', text)
        self.assertEqual(1, text.count("# KNOWLEDGE_IMPACT_CLI_FUNCTIONS_BEGIN"))
        self.assertEqual(1, text.count("# KNOWLEDGE_IMPACT_CLI_FUNCTIONS_END"))
        self.assertEqual(1, text.count("# KNOWLEDGE_IMPACT_CLI_PARSERS_BEGIN"))
        self.assertEqual(1, text.count("# KNOWLEDGE_IMPACT_CLI_PARSERS_END"))

    def test_temporary_alignment_artifacts_are_absent(self):
        self.assertFalse((ROOT / ".alignment-sync-diagnostic.txt").exists())
        self.assertFalse((ROOT / ".github/workflows/apply-knowledge-impact-alignment-once.yml").exists())


if __name__ == "__main__":
    unittest.main()
