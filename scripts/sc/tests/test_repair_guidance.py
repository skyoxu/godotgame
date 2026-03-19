#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SC_DIR = REPO_ROOT / "scripts" / "sc"
sys.path.insert(0, str(SC_DIR))

from _repair_guidance import build_repair_guide  # noqa: E402


class RepairGuidanceTests(unittest.TestCase):
    def test_build_repair_guide_should_mark_not_needed_when_no_failed_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            summary = {
                "status": "ok",
                "steps": [
                    {"name": "sc-test", "status": "ok", "rc": 0, "cmd": ["py", "-3", "scripts/sc/test.py"]},
                ],
            }
            payload = build_repair_guide(summary, task_id="1", out_dir=out_dir)
            self.assertEqual("not-needed", payload["status"])
            self.assertEqual([], payload["recommendations"])

    def test_build_repair_guide_should_suggest_project_path_fix_for_msb1009(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            log_path = out_dir / "sc-test.log"
            log_path.write_text("MSBUILD : error MSB1009: Project file does not exist.\n", encoding="utf-8")
            summary = {
                "status": "fail",
                "steps": [
                    {
                        "name": "sc-test",
                        "status": "fail",
                        "rc": 1,
                        "cmd": ["py", "-3", "scripts/sc/test.py", "--task-id", "1"],
                        "log": str(log_path),
                    },
                ],
            }
            payload = build_repair_guide(summary, task_id="1", out_dir=out_dir)
            self.assertEqual("needs-fix", payload["status"])
            ids = {item["id"] for item in payload["recommendations"]}
            self.assertIn("sc-test-project-path", ids)

    def test_build_repair_guide_should_suggest_acceptance_test_refs_fix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            log_path = out_dir / "sc-acceptance-check.log"
            log_path.write_text("validate_task_test_refs failed under require-task-test-refs\n", encoding="utf-8")
            summary = {
                "status": "fail",
                "steps": [
                    {
                        "name": "sc-acceptance-check",
                        "status": "fail",
                        "rc": 1,
                        "cmd": ["py", "-3", "scripts/sc/acceptance_check.py", "--task-id", "1"],
                        "log": str(log_path),
                    },
                ],
            }
            payload = build_repair_guide(summary, task_id="1", out_dir=out_dir)
            ids = {item["id"] for item in payload["recommendations"]}
            self.assertIn("acceptance-test-refs", ids)


if __name__ == "__main__":
    unittest.main()
