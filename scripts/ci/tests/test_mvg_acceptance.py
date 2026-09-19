"""Failure-oriented neutral tests for reusable MVG acceptance and impact recommendation."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/python"))

from _mvg_execution import read_test_evidence
from _mvg_manifest import recommend, validate_manifest
from run_mvg_acceptance import changed_paths, register_arguments, run
from run_mvg_mutation_probe import _validate_spec


class MvgAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for name in [
            "Game.Core/Feature.cs",
            "Game.Core/Contract.cs",
            "Game.Core.Tests/Integration/MvgFeatureTests.cs",
        ]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("content", encoding="utf-8")
        tasks = self.root / ".taskmaster/tasks/tasks.json"
        tasks.parent.mkdir(parents=True)
        tasks.write_text(
            json.dumps({"master": {"tasks": [{"id": 1, "status": "done"}, {"id": 2, "status": "done"}]}}),
            encoding="utf-8",
        )
        self.manifest = {
            "schema_version": "godotgame.mvg-integration.v1",
            "mvg_id": "neutral-pilot",
            "coverage": {
                "mode": "pilot",
                "scope_id": "neutral-template-pilot",
                "required_flow_ids": ["feature-flow"],
                "blocking_task_ids": [],
                "excluded_claims": [
                    "Neutral template fixture does not represent project-wide MVG coverage."
                ],
            },
            "flows": [
                {
                    "id": "feature-flow",
                    "outcome": "A neutral feature crosses one explicit contract boundary.",
                    "task_ids": [1, 2],
                    "source_paths": ["Game.Core/Feature.cs"],
                    "handoffs": [
                        {
                            "contract_ref": "Game.Core/Contract.cs",
                            "behavior": "The consumer observes one stable handoff.",
                            "producer_task": 1,
                            "consumer_task": 2,
                            "owner_task": 2,
                            "test_ids": ["feature-core"],
                        }
                    ],
                    "test_ids": ["feature-core"],
                }
            ],
            "tests": [
                {
                    "id": "feature-core",
                    "kind": "dotnet",
                    "state": "implemented",
                    "evidence_level": "domain-integration",
                    "path": "Game.Core.Tests/Integration/MvgFeatureTests.cs",
                    "selector": "Game.Core.Tests.Integration.MvgFeatureTests",
                    "min_tests": 1,
                }
            ],
        }

    def test_coverage_contract_rejects_missing_or_mismatched_scope(self) -> None:
        for mutate in [
            lambda doc: doc.pop("coverage"),
            lambda doc: doc["coverage"].__setitem__("required_flow_ids", ["other-flow"]),
            lambda doc: doc["coverage"].__setitem__("excluded_claims", []),
        ]:
            with self.subTest(mutate=mutate):
                doc = copy.deepcopy(self.manifest)
                mutate(doc)
                self.assertTrue(validate_manifest(self.root, doc))

    def test_critical_and_full_scopes_fail_closed_on_incomplete_scope(self) -> None:
        tasks = self.root / ".taskmaster/tasks/tasks.json"
        tasks.write_text(
            json.dumps({
                "master": {
                    "tasks": [
                        {"id": 1, "status": "done"},
                        {"id": 2, "status": "pending"},
                    ]
                }
            }),
            encoding="utf-8",
        )
        critical = copy.deepcopy(self.manifest)
        critical["coverage"] = {
            "mode": "critical",
            "scope_id": "neutral-critical",
            "required_flow_ids": ["feature-flow", "second-flow"],
            "blocking_task_ids": [2],
            "excluded_claims": ["Human product acceptance remains outside this fixture."],
        }
        critical["flows"].append({**copy.deepcopy(critical["flows"][0]), "id": "second-flow"})
        self.assertEqual([], validate_manifest(self.root, critical, executable=False))
        errors = validate_manifest(self.root, critical, executable=True)
        self.assertTrue(any("blocked by non-done tasks [2]" in item for item in errors))

        full = copy.deepcopy(critical)
        full["coverage"]["mode"] = "full"
        full["coverage"]["scope_id"] = "neutral-full"
        full["coverage"]["required_flow_ids"] = ["feature-flow", "second-flow", "third-flow"]
        full["flows"].append({**copy.deepcopy(full["flows"][0]), "id": "third-flow"})
        errors = validate_manifest(self.root, full, executable=True)
        self.assertTrue(any("executable full scope blocked" in item for item in errors))

    def test_manifest_requires_real_task_and_handoff_ownership(self) -> None:
        self.assertEqual([], validate_manifest(self.root, self.manifest))
        missing_tasks = self.root / ".taskmaster/tasks/tasks.json"
        missing_tasks.unlink()
        self.assertTrue(validate_manifest(self.root, self.manifest))
        missing_tasks.write_text(
            json.dumps({"master": {"tasks": [{"id": 1, "status": "done"}, {"id": 2, "status": "done"}]}}),
            encoding="utf-8",
        )
        no_ownership = copy.deepcopy(self.manifest)
        no_ownership["flows"][0].pop("task_ids")
        for key in ("producer_task", "consumer_task", "owner_task"):
            no_ownership["flows"][0]["handoffs"][0].pop(key)
        self.assertTrue(validate_manifest(self.root, no_ownership))

    def test_planning_allows_missing_planned_test_but_run_rejects_it(self) -> None:
        doc = copy.deepcopy(self.manifest)
        doc["tests"][0].update(
            state="planned", path="Game.Core.Tests/Integration/FutureMvgTests.cs"
        )
        self.assertEqual([], validate_manifest(self.root, doc, executable=False))
        self.assertTrue(validate_manifest(self.root, doc, executable=True))

    def test_impact_recommendation_never_removes_required_tests(self) -> None:
        known = recommend(self.manifest, ["Game.Core/Feature.cs"])
        self.assertEqual("related-first", known["recommendation"])
        self.assertEqual(["feature-flow"], known["matched_flows"])
        self.assertEqual(["feature-core"], known["required_tests"])
        self.assertFalse(known["authorizes_test_exclusion"])

        unknown = recommend(self.manifest, ["Game.Godot/NewFeature.gd"])
        self.assertEqual("full-mvg", unknown["recommendation"])
        self.assertEqual("pilot", unknown["manifest_coverage_mode"])
        self.assertEqual("neutral-template-pilot", unknown["manifest_scope_id"])
        self.assertEqual([], unknown["manifest_blocking_task_ids"])
        self.assertEqual(["Game.Godot/NewFeature.gd"], unknown["unmapped_changes"])
        self.assertEqual(["feature-core"], unknown["required_tests"])

    def test_report_identity_counts_skips_and_suite_errors_fail_closed(self) -> None:
        trx = self.root / "results.trx"
        self.assertFalse(read_test_evidence(self.root, "dotnet", "Expected", 1)["passed"])
        for content in [
            "bad xml",
            '<TestRun><UnitTestResult testName="Other.A" outcome="Passed"/></TestRun>',
            '<TestRun><UnitTestResult testName="Expected.A" outcome="NotExecuted"/></TestRun>',
            '<TestRun><UnitTestResult testName="Expected.A" outcome="Passed"/>'
            '<Counters total="2" passed="2" failed="0"/></TestRun>',
        ]:
            trx.write_text(content, encoding="utf-8")
            self.assertFalse(read_test_evidence(self.root, "dotnet", "Expected", 1)["passed"])

        trx.write_text(
            '<TestRun><UnitTestResult testName="Expected.A" outcome="Passed"/></TestRun>',
            encoding="utf-8",
        )
        self.assertTrue(read_test_evidence(self.root, "dotnet", "Expected", 1)["passed"])

        trx.unlink()
        xml = self.root / "results.xml"
        xml.write_text(
            '<testsuites><testsuite name="expected" errors="1">'
            '<testcase name="a"/></testsuite></testsuites>',
            encoding="utf-8",
        )
        result = read_test_evidence(self.root, "gdunit", "expected", 1)
        self.assertFalse(result["passed"])
        self.assertEqual("reported-suite-failure", result["reason"])


    def test_duplicate_test_identity_across_multiple_reports_fails_closed(self) -> None:
        one = self.root / "one"
        two = self.root / "two"
        one.mkdir()
        two.mkdir()
        xml = '<TestRun><UnitTestResult testName="Expected.A" outcome="Passed"/></TestRun>'
        (one / "results.trx").write_text(xml, encoding="utf-8")
        (two / "results.trx").write_text(xml, encoding="utf-8")
        result = read_test_evidence(self.root, "dotnet", "Expected", 1)
        self.assertFalse(result["passed"])
        self.assertEqual("duplicate-test-results", result["reason"])

    def test_planning_success_never_claims_runtime_verification(self) -> None:
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        parser = argparse.ArgumentParser()
        register_arguments(parser)
        args = parser.parse_args(["--manifest", "manifest.json", "--mode", "plan"])
        with patch("run_mvg_acceptance.git", return_value="a" * 40):
            self.assertEqual(0, run(args, self.root))
        summary = json.loads(
            next(self.root.glob("logs/ci/mvg-acceptance/*/summary.json")).read_text()
        )
        self.assertFalse(summary["runtime_verified"])
        self.assertFalse(summary["authorizes_task_status_write"])

    def test_execution_failure_blocks_runtime_acceptance(self) -> None:
        parser = argparse.ArgumentParser()
        register_arguments(parser)
        args = parser.parse_args(["--manifest", "manifest.json", "--mode", "run"])

        def snapshot(root, target, revision, mode, deadline):
            target.mkdir(parents=True)
            (target / "manifest.json").write_text(json.dumps(self.manifest))
            return {"source_revision": "workspace:digest", "snapshot_digest": "digest"}

        with patch("run_mvg_acceptance.git", return_value="a" * 40), patch(
            "run_mvg_acceptance.prepare_snapshot", side_effect=snapshot
        ), patch("run_mvg_acceptance.validate_manifest", return_value=[]), patch(
            "run_mvg_acceptance.execute_test", return_value={"status": "failed"}
        ):
            self.assertEqual(1, run(args, self.root))
        summary = json.loads(
            next(self.root.glob("logs/ci/mvg-acceptance/*/summary.json")).read_text()
        )
        self.assertEqual("blocked", summary["status"])
        self.assertFalse(summary["runtime_verified"])

    def test_godot_prewarm_is_reused_only_after_first_suite_passes(self) -> None:
        parser = argparse.ArgumentParser()
        register_arguments(parser)
        args = parser.parse_args(["--manifest", "manifest.json", "--mode", "run"])
        doc = copy.deepcopy(self.manifest)
        doc["tests"] = [
            {"id": "first", "kind": "gdunit"},
            {"id": "second", "kind": "gdunit"},
        ]

        def snapshot(root, target, revision, mode, deadline):
            target.mkdir(parents=True)
            (target / "manifest.json").write_text(json.dumps(doc))
            return {"source_revision": "workspace:digest", "snapshot_digest": "digest"}

        with patch("run_mvg_acceptance.git", return_value="a" * 40), patch(
            "run_mvg_acceptance.prepare_snapshot", side_effect=snapshot
        ), patch("run_mvg_acceptance.validate_manifest", return_value=[]), patch(
            "run_mvg_acceptance.recommend", return_value={}
        ), patch(
            "run_mvg_acceptance.execute_test", return_value={"status": "passed"}
        ) as execute:
            self.assertEqual(0, run(args, self.root))
        self.assertEqual([True, False], [call.kwargs["prewarm"] for call in execute.call_args_list])
        self.assertNotEqual(execute.call_args_list[0].args[2], execute.call_args_list[1].args[2])

    def test_commit_impact_comparison_is_revision_bound(self) -> None:
        calls = []

        def fake_git(root, *args):
            calls.append(args)
            return "base-sha" if args[0] == "rev-parse" else "Game.Core/Feature.cs\0"

        with patch("run_mvg_acceptance.git", side_effect=fake_git):
            paths, reason = changed_paths(self.root, "base", "old-commit", workspace=False)
        self.assertEqual(["Game.Core/Feature.cs"], paths)
        self.assertEqual("", reason)
        self.assertIn(
            ("diff", "--name-only", "--no-renames", "-z", "base-sha", "old-commit"),
            calls,
        )
        self.assertFalse(any("HEAD" in call or "ls-files" in call for call in calls))

    def test_workflow_scan_ignores_trigger_paths_and_step_names(self) -> None:
        from check_workflow_gate_enforcement import _extract_workflow_scripts

        workflow = """on:
  pull_request:
    paths:
      - 'scripts/python/listened.py'
jobs:
  check:
    steps:
      - name: scripts/python/label.py
        run: |
          python scripts/python/real.py
          python scripts/python/second.py
      - run: python scripts/python/inline.py
"""
        self.assertEqual(
            {
                "scripts/python/real.py",
                "scripts/python/second.py",
                "scripts/python/inline.py",
            },
            _extract_workflow_scripts(workflow),
        )

    def test_workflow_dispatch_inputs_are_not_interpolated_into_shell_source(self) -> None:
        workflow = (ROOT / ".github/workflows/mvg-integration.yml").read_text(encoding="utf-8")
        self.assertIn("MVG_MANIFEST_INPUT: ${{ inputs.manifest }}", workflow)
        self.assertIn("MVG_MUTATION_SPEC_INPUT: ${{ inputs.mutation_spec }}", workflow)
        run_bodies = []
        in_run = False
        run_indent = 0
        for line in workflow.splitlines():
            indent = len(line) - len(line.lstrip())
            if in_run and indent > run_indent:
                run_bodies.append(line)
                continue
            in_run = False
            if line.strip() == "run: |":
                in_run = True
                run_indent = indent
        shell_source = "\n".join(run_bodies)
        self.assertNotIn("${{ inputs.manifest }}", shell_source)
        self.assertNotIn("${{ inputs.mutation_spec }}", shell_source)
        self.assertNotIn("${{ inputs.challenge_input }}", shell_source)

    def test_parameterized_mutation_spec_has_no_business_defaults(self) -> None:
        spec = {
            "schema_version": "godotgame.mvg-mutation-probe.v1",
            "source_path": "Game.Core/Feature.cs",
            "test": {
                "id": "mutation-test",
                "kind": "dotnet",
                "evidence_level": "domain-integration",
                "path": "Game.Core.Tests/Integration/MvgFeatureTests.cs",
                "selector": "Game.Core.Tests.Integration.MvgFeatureTests",
                "min_tests": 1,
            },
            "mutants": [{"id": "boundary", "before": "content", "after": "changed"}],
        }
        self.assertEqual([], _validate_spec(self.root, spec))


if __name__ == "__main__":
    unittest.main()
