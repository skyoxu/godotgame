from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/publish-knowledge-catalog.yml"
ALLOWLIST = ROOT / "scripts/python/config/workflow-gate-allowlist.json"


class KnowledgePublicationWorkflowContractTests(unittest.TestCase):
    def test_workflow_only_creates_sha_scoped_derived_pull_request(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('branches: [main]', text)
        self.assertIn('$branch = "automation/knowledge-catalog-$short"', text)
        self.assertIn('git ls-remote --heads origin $branch', text)
        self.assertIn('gh pr list --base main --head $branch --state open', text)
        self.assertIn('gh pr create --base main --head $branch', text)
        self.assertIn('publication_result=read-only reason=unable-to-push-derived-branch', text)
        self.assertIn('publication_result=read-only reason=unable-to-create-derived-pr', text)
        self.assertNotIn('git push origin main', text)
        self.assertNotIn('git push --force origin main', text)
        self.assertNotRegex(text, re.compile(r'git\s+push[^\n]*\bmain\b'))

    def test_publication_job_validates_before_branch_creation(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        publish = text.index('publish_knowledge_catalog.py --repository-root . --publish')
        check = text.index('publish_knowledge_catalog.py --repository-root . --check')
        validate = text.index('validate_knowledge_control_plane.py --repository-root . --require-generated')
        branch = text.index('git switch -c $branch')
        self.assertLess(publish, check)
        self.assertLess(check, validate)
        self.assertLess(validate, branch)

    def test_workflow_gate_allowlist_is_minimal_and_trigger_paths_do_not_look_like_commands(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        trigger_block = text.split('workflow_dispatch:', 1)[0]
        self.assertIn('"scripts/python/*knowledge*.py"', trigger_block)
        for internal in (
            '_knowledge_catalog_builder.py',
            '_knowledge_locator_core.py',
            'build_knowledge_catalog.py',
            'knowledge_locator.py',
            'prepare_knowledge_context.py',
            'freeze_knowledge_context.py',
        ):
            self.assertNotIn(internal, trigger_block)

        allowlist = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
        allowed = set(allowlist["allowed_direct_scripts"])
        self.assertIn("scripts/python/publish_knowledge_catalog.py", allowed)
        self.assertIn("scripts/python/validate_knowledge_control_plane.py", allowed)
        self.assertNotIn("scripts/python/_knowledge_catalog_builder.py", allowed)
        self.assertNotIn("scripts/python/_knowledge_locator_core.py", allowed)
        self.assertNotIn("scripts/python/build_knowledge_catalog.py", allowed)
        self.assertNotIn("scripts/python/knowledge_locator.py", allowed)
        self.assertNotIn("scripts/python/prepare_knowledge_context.py", allowed)
        self.assertNotIn("scripts/python/freeze_knowledge_context.py", allowed)


if __name__ == "__main__":
    unittest.main()
