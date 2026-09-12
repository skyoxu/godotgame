"""CI discovery shim for the reusable Knowledge / Impact regression suite."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUITE = ROOT / "scripts/python/tests/test_template_knowledge_impact.py"
SPEC = importlib.util.spec_from_file_location("template_knowledge_impact_suite", SUITE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {SUITE}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

TemplateKnowledgeImpactTests = MODULE.TemplateKnowledgeImpactTests


class ProjectHealthWebContractTests(unittest.TestCase):
    def test_javascript_references_existing_html_ids(self):
        html = (ROOT / "scripts/python/project_health_knowledge.html").read_text(encoding="utf-8")
        javascript = (ROOT / "scripts/python/project_health_knowledge.js").read_text(encoding="utf-8")
        import re

        html_ids = set(re.findall(r'\bid="([^"]+)"', html))
        referenced_ids = set(re.findall(r"\bel\('([^']+)'\)", javascript))
        self.assertFalse(referenced_ids - html_ids, f"JS references missing HTML ids: {sorted(referenced_ids - html_ids)}")

    def test_javascript_syntax_when_node_is_available(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        result = subprocess.run(
            [node, "--check", str(ROOT / "scripts/python/project_health_knowledge.js")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
