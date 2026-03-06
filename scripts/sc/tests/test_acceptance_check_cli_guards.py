#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from _taskmaster_fixture import staged_taskmaster_triplet


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "sc" / "acceptance_check.py"


class AcceptanceCheckCliGuardTests(unittest.TestCase):
    def _pick_task_id(self) -> str:
        tasks_dir = REPO_ROOT / ".taskmaster" / "tasks"

        tasks_path = tasks_dir / "tasks.json"
        if tasks_path.exists():
            obj = json.loads(tasks_path.read_text(encoding="utf-8"))
            tasks = ((obj.get("master") or {}).get("tasks") or [])
            for task in tasks:
                if isinstance(task, dict) and str(task.get("id") or "").strip():
                    return str(task.get("id"))

        for view_name in ("tasks_back.json", "tasks_gameplay.json"):
            view_path = tasks_dir / view_name
            if not view_path.exists():
                continue
            view_obj = json.loads(view_path.read_text(encoding="utf-8"))
            if not isinstance(view_obj, list):
                continue
            for task in view_obj:
                if not isinstance(task, dict):
                    continue
                task_id = task.get("taskmaster_id")
                if str(task_id or "").strip():
                    return str(task_id)

        raise AssertionError("No task id found in taskmaster triplet")

    def _extract_out_dir(self, output: str) -> str:
        m = re.search(r"\bout=([^\r\n]+)", output or "")
        if not m:
            raise AssertionError(f"Unable to find out=... in output:\n{output}")
        return m.group(1).strip()

    def test_self_check_should_exit_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--self-check"],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        self.assertEqual(0, proc.returncode)
        self.assertIn("SC_ACCEPTANCE_SELF_CHECK status=ok", proc.stdout or "")

    def test_self_check_should_fail_on_conflicting_args(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--self-check",
                "--only",
                "links",
                "--require-headless-e2e",
            ],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        self.assertEqual(2, proc.returncode)
        self.assertIn("conflict: --require-headless-e2e", proc.stdout or "")
        self.assertIn("SC_ACCEPTANCE_SELF_CHECK status=fail", proc.stdout or "")

    def test_dry_run_plan_should_emit_step_plan_summary(self) -> None:
        with staged_taskmaster_triplet():
            task_id = self._pick_task_id()
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--task-id", task_id, "--dry-run-plan", "--only", "links,tests,perf"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
        self.assertEqual(0, proc.returncode)
        self.assertIn("SC_ACCEPTANCE_DRY_RUN_PLAN status=ok", proc.stdout or "")
        out_dir = Path(self._extract_out_dir(proc.stdout or ""))
        summary_path = out_dir / "summary.json"
        self.assertTrue(summary_path.exists())
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual("dry-run-plan", summary.get("mode"))
        self.assertIsInstance(summary.get("step_plan"), list)
        self.assertGreater(len(summary.get("step_plan") or []), 0)

    def test_normal_min_path_should_write_summary(self) -> None:
        with staged_taskmaster_triplet():
            task_id = self._pick_task_id()
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--task-id", task_id, "--only", "links"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
        self.assertIn(proc.returncode, (0, 1))
        self.assertIn("SC_ACCEPTANCE status=", proc.stdout or "")
        out_dir = Path(self._extract_out_dir(proc.stdout or ""))
        summary_path = out_dir / "summary.json"
        self.assertTrue(summary_path.exists())
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual("run", summary.get("mode"))
        self.assertIn(summary.get("status"), ("ok", "fail"))

    def test_task1_require_headless_should_force_tests_all_and_post_gate(self) -> None:
        with staged_taskmaster_triplet(include_task1=True):
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task-id",
                    "1",
                    "--dry-run-plan",
                    "--only",
                    "tests",
                    "--require-headless-e2e",
                ],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
        self.assertEqual(0, proc.returncode)
        self.assertIn("SC_ACCEPTANCE_DRY_RUN_PLAN status=ok", proc.stdout or "")
        out_dir = Path(self._extract_out_dir(proc.stdout or ""))
        summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
        plan = summary.get("step_plan") or []

        tests_all = next((x for x in plan if isinstance(x, dict) and x.get("name") == "tests-all"), {})
        self.assertEqual("all", tests_all.get("test_type"))

        headless = next((x for x in plan if isinstance(x, dict) and x.get("name") == "headless-e2e-evidence"), {})
        self.assertTrue(bool(headless.get("enabled")))

        post_gate = next((x for x in plan if isinstance(x, dict) and x.get("name") == "post-evidence-integration"), {})
        self.assertTrue(bool(post_gate.get("enabled")))


if __name__ == "__main__":
    unittest.main()
