from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/publish-knowledge-catalog.yml"


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


if __name__ == "__main__":
    unittest.main()
