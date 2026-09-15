from __future__ import annotations

import sys
import tempfile
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

from analyze_impact import _failure_evidence, _publish_pair
from impact_analysis_index import ImpactIndexError


class ImpactOutputCollisionTests(unittest.TestCase):
    def report(self) -> dict:
        return {"schema": "godot-project-impact.report.v3", "status": "ok", "revision": "a" * 40, "target": "FeatureService", "evidence": []}

    def test_existing_pair_is_a_deterministic_identity_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "logs/ci/run/impact-report.v1.json"
            _publish_pair(root, output, self.report(), uuid.uuid4().hex)
            with self.assertRaises(ImpactIndexError) as caught:
                _publish_pair(root, output, self.report(), uuid.uuid4().hex)
            self.assertEqual(caught.exception.code, "index_identity_collision")
            self.assertIn("already exists", caught.exception.reason)

    def test_collision_failure_evidence_prefers_isolated_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "logs/ci/shared/impact-report.v1.json"
            _publish_pair(root, output, self.report(), uuid.uuid4().hex)
            reason = ImpactIndexError("index_identity_collision", "output report or run manifest already exists")
            evidence = _failure_evidence(root, output, "losing-writer", "FeatureService", "a" * 40, reason)
            self.assertTrue(evidence["evidence_saved"])
            self.assertIn("failed-losing-writer", evidence["report_path"])
            self.assertNotEqual(Path(evidence["report_path"]).parent, Path("logs/ci/shared"))

    def test_live_writer_lock_also_redirects_failure_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "logs/ci/shared/impact-report.v1.json"
            output.parent.mkdir(parents=True)
            (output.parent / ".impact-report-publish.lock").mkdir()
            reason = ImpactIndexError("index_identity_collision", "another writer owns the output directory")
            evidence = _failure_evidence(root, output, "lock-loser", "FeatureService", "a" * 40, reason)
            self.assertTrue(evidence["evidence_saved"])
            self.assertIn("failed-lock-loser", evidence["report_path"])


if __name__ == "__main__":
    unittest.main()
