from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "scripts/python"
if str(PYTHON) not in sys.path:
    sys.path.insert(0, str(PYTHON))

from freeze_knowledge_context import freeze


class KnowledgeFreezeContractTests(unittest.TestCase):
    def bundle(self):
        return {
            "schema": "godot-project-knowledge.context-candidates.v2",
            "status": "ready",
            "consumer": "chapter6",
            "task_id": "7",
            "revision": "a" * 40,
            "policy_revision": "test-v1",
            "publication_state": "published-current",
            "bundle_sha256": "bundle-test",
            "candidates": [
                {"path": "docs/prd/feature.md", "score": 10},
                {"path": "Game.Core/Contracts/FeatureContract.cs", "score": 9},
            ],
        }

    def test_every_candidate_requires_exactly_one_decision(self):
        with self.assertRaisesRegex(ValueError, "every candidate requires exactly one explicit decision"):
            freeze(self.bundle(), {"decisions": [{
                "path": "docs/prd/feature.md",
                "accepted": True,
                "reason": "Defines the requested behavior.",
                "satisfies": "product intent",
            }]})

    def test_reason_and_satisfies_are_both_required(self):
        base = [
            {"path": "docs/prd/feature.md", "accepted": True, "reason": "Defines behavior.", "satisfies": "product intent"},
            {"path": "Game.Core/Contracts/FeatureContract.cs", "accepted": False, "reason": "Outside this change.", "satisfies": "contract review"},
        ]
        missing_reason = [dict(item) for item in base]
        missing_reason[0]["reason"] = ""
        with self.assertRaisesRegex(ValueError, "decision reason required"):
            freeze(self.bundle(), {"decisions": missing_reason})

        missing_satisfies = [dict(item) for item in base]
        missing_satisfies[1]["satisfies"] = ""
        with self.assertRaisesRegex(ValueError, "decision satisfies required"):
            freeze(self.bundle(), {"decisions": missing_satisfies})

    def test_formal_freeze_rejects_ephemeral_publication(self):
        bundle = self.bundle()
        bundle["publication_state"] = "ephemeral"
        with self.assertRaisesRegex(ValueError, "published-current"):
            freeze(bundle, {"decisions": []})


if __name__ == "__main__":
    unittest.main()
