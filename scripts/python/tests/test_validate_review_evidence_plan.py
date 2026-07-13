#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON_DIR = REPO_ROOT / "scripts" / "python"
sys.path.insert(0, str(PYTHON_DIR))

from validate_review_evidence_plan import validate_plan  # noqa: E402
from _review_evidence_plan_contract import compatibility_contract_errors, ledger_status_errors  # noqa: E402


PLAN_NAME = "2026-07-12-phase-review-evidence-gate-hardening-execution-plan"


class ValidateReviewEvidencePlanTests(unittest.TestCase):
    def _copy_fixture(self, destination: Path) -> Path:
        plan_source = REPO_ROOT / "execution-plans" / PLAN_NAME
        plan_target = destination / "execution-plans" / PLAN_NAME
        plan_target.parent.mkdir(parents=True)
        shutil.copytree(plan_source, plan_target)
        shutil.copy2(REPO_ROOT / "execution-plans" / f"{PLAN_NAME}.md", plan_target.parent)

        research_rel = Path(
            "_bmad-output/planning-artifacts/research/technical-ecc-review-anti-hallucination-research-2026-07-12.md"
        )
        research_target = destination / research_rel
        research_target.parent.mkdir(parents=True)
        shutil.copy2(REPO_ROOT / research_rel, research_target)

        schema_rel = Path("scripts/sc/schemas/review-evidence.v1.schema.json")
        schema_target = destination / schema_rel
        schema_target.parent.mkdir(parents=True)
        shutil.copy2(REPO_ROOT / schema_rel, schema_target)
        shutil.copy2(
            REPO_ROOT / "scripts/sc/_review_evidence_schema_fallback.py",
            destination / "scripts/sc/_review_evidence_schema_fallback.py",
        )
        adr_target = destination / "docs/adr/ADR-0032-review-evidence-gate.md"
        adr_target.parent.mkdir(parents=True)
        shutil.copy2(REPO_ROOT / "docs/adr/ADR-0032-review-evidence-gate.md", adr_target)
        config_rel = Path("scripts/sc/config/delivery_profiles.json")
        config_target = destination / config_rel
        config_target.parent.mkdir(parents=True)
        shutil.copy2(REPO_ROOT / config_rel, config_target)
        return destination

    def _mutate(self, root: Path, relative: str, old: str, new: str) -> None:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

    def test_repository_plan_should_pass(self) -> None:
        self.assertEqual([], validate_plan(REPO_ROOT))

    def test_missing_book_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            (root / "execution-plans" / PLAN_NAME / "05-chapter7-ui-review-evidence.md").unlink()
            self.assertIn("RGE-PLAN-001", {finding.rule_id for finding in validate_plan(root)})

    def test_missing_source_audit_book_should_return_stable_findings_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            (root / "execution-plans" / PLAN_NAME / "98-research-to-split-audit.md").unlink()
            findings = validate_plan(root)
            self.assertIn("RGE-PLAN-001", {finding.rule_id for finding in findings})

    def test_broken_markdown_link_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/00-index.md",
                "01-authority-scope-and-invariants.md",
                "01-missing.md",
            )
            self.assertIn("RGE-PLAN-002", {finding.rule_id for finding in validate_plan(root)})

    def test_ledger_row_without_acceptance_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/97-post-split-requirements-ledger.md",
                "[01 Acceptance](01-authority-scope-and-invariants.md#acceptance)",
                "missing acceptance",
            )
            self.assertIn("RGE-PLAN-004", {finding.rule_id for finding in validate_plan(root)})

    def test_duplicate_source_coverage_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/99-source-coverage.md",
                "| SRC-001 |",
                "| SRC-000 |",
            )
            self.assertIn("RGE-PLAN-006", {finding.rule_id for finding in validate_plan(root)})

    def test_research_source_directory_should_return_stable_finding_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            audit = root / f"execution-plans/{PLAN_NAME}/98-research-to-split-audit.md"
            text = audit.read_text(encoding="utf-8")
            text = re.sub(
                r"Primary source:\s*\n\s*- `[^`]+`\s*\n\s*- SHA-256: `[0-9a-f]{64}`\s*\n\s*- UTF-8 line count: `\d+`",
                "Primary source:\n\n- `docs`\n- SHA-256: `" + "0" * 64 + "`\n- UTF-8 line count: `0`",
                text,
                count=1,
            )
            audit.write_text(text, encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-006", {finding.rule_id for finding in validate_plan(root)})

    def test_invalid_utf8_research_source_should_return_stable_finding_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            source = root / "invalid-research.bin"
            source.write_bytes(b"\xff")
            source_hash = hashlib.sha256(b"\xff").hexdigest()
            audit = root / f"execution-plans/{PLAN_NAME}/98-research-to-split-audit.md"
            text = audit.read_text(encoding="utf-8")
            text = re.sub(
                r"Primary source:\s*\n\s*- `[^`]+`\s*\n\s*- SHA-256: `[0-9a-f]{64}`\s*\n\s*- UTF-8 line count: `\d+`",
                f"Primary source:\n\n- `invalid-research.bin`\n- SHA-256: `{source_hash}`\n- UTF-8 line count: `1`",
                text,
                count=1,
            )
            audit.write_text(text, encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-006", {finding.rule_id for finding in validate_plan(root)})

    def test_invalid_utf8_source_audit_control_doc_should_return_stable_finding_without_crashing(self) -> None:
        for name in (
            "06-pipeline-integration-recovery-and-compatibility.md",
            "98-research-to-split-audit.md",
            "99-source-coverage.md",
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                root = self._copy_fixture(Path(td))
                path = root / f"execution-plans/{PLAN_NAME}/{name}"
                path.write_bytes(b"\xff")
                self.assertTrue(validate_plan(root))

    def test_open_historical_finding_without_expiry_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/96-global-review-and-split-validation.md",
                "| RG-WDR-001 | P1 | Closed |",
                "| RG-WDR-001 | P1 | Open |",
            )
            self.assertIn("RGE-PLAN-010", {finding.rule_id for finding in validate_plan(root)})

    def test_compatibility_contract_should_reject_clean_resume_projection(self) -> None:
        errors = compatibility_contract_errors(
            adr_text="Derived OK projects to the existing pass/resume vocabulary.",
            compatibility_text="| derived OK | `pass` | none | `none` | no rerun |",
        )
        self.assertTrue(errors)

    def test_ledger_status_should_require_closed_requirement_transition(self) -> None:
        ledger = """## Requirements
| RGR-001 | Closed | 01 | RG-0 | Requirement | [Acceptance](01.md#acceptance) | test |
## Requirement Status Registry
| ID | Previous status | New status | Superseded by | Reason |
"""
        self.assertTrue(ledger_status_errors(ledger))

    def test_ledger_status_should_reject_transition_for_active_requirement(self) -> None:
        ledger = """## Requirements
| RGR-001 | Active | 01 | RG-1 | Requirement | [Acceptance](01.md#acceptance) | test |
## Requirement Status Registry
| ID | Previous status | New status | Superseded by | Reason |
| RGR-001 | Active | Closed | n/a | premature |
## Research Finding Coverage
"""
        self.assertTrue(ledger_status_errors(ledger))

    def test_duplicate_superseded_requirement_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / f"execution-plans/{PLAN_NAME}/97-post-split-requirements-ledger.md"
            text = path.read_text(encoding="utf-8")
            row = next(line for line in text.splitlines() if line.startswith("| RGR-001 | Closed |"))
            superseded = row.replace("| Closed |", "| Superseded |")
            text = text.replace(row, superseded, 1).replace("| RGR-001 | Active | Closed |", "| RGR-001 | Active | Superseded |", 1)
            text = text.replace(superseded, superseded + "\n" + superseded, 1)
            path.write_text(text, encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-004", {finding.rule_id for finding in validate_plan(root)})

    def test_removed_requirement_transition_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / f"execution-plans/{PLAN_NAME}/97-post-split-requirements-ledger.md"
            text = path.read_text(encoding="utf-8")
            row = "| RGR-001 | Active | Closed | n/a | ADR-0032 and RGE-PLAN-014 freeze repository policy precedence. |\n"
            self.assertIn(row, text)
            path.write_text(text.replace(row, "", 1), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-004", {finding.rule_id for finding in validate_plan(root)})

    def test_invalid_phase_predecessor_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/08-implementation-phases.md",
                "| RG-2 | RG-1 |",
                "| RG-2 | RG-0 |",
            )
            self.assertIn("RGE-PLAN-011", {finding.rule_id for finding in validate_plan(root)})

    def test_plan_schema_pointer_should_not_become_second_normative_copy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            shutil.copy2(
                root / "scripts/sc/schemas/review-evidence.v1.schema.json",
                root / f"execution-plans/{PLAN_NAME}/schemas/review-evidence.v1.schema.json",
            )
            self.assertIn("RGE-PLAN-008", {finding.rule_id for finding in validate_plan(root)})

    def test_plan_schema_pointer_should_reject_embedded_normative_content(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / f"execution-plans/{PLAN_NAME}/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["$defs"] = {"duplicate": {"type": "string"}}
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-008", {finding.rule_id for finding in validate_plan(root)})

    def test_canonical_schema_should_reject_removed_mandatory_field(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["required"].remove("task_id")
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_canonical_schema_should_reject_loosened_additional_properties(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["additionalProperties"] = True
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_canonical_schema_should_reject_loosened_failure_chain_contract(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            failure_chain = payload["$defs"]["failure_chain"]
            failure_chain["required"].remove("bad_result_or_consequence")
            failure_chain["additionalProperties"] = True
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_canonical_schema_should_reject_removed_conditional_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.pop("allOf")
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_malformed_canonical_schema_should_return_stable_finding_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["properties"] = []
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_truthy_non_mapping_schema_node_should_return_stable_finding_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["properties"] = ["bad"]
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_invalid_utf8_canonical_schema_should_return_plan_schema_finding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            path.write_bytes(b"\xff")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

    def test_unknown_projection_mutation_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/06-pipeline-integration-recovery-and-compatibility.md",
                "review-evidence-unknown",
                "generic-unknown",
            )
            self.assertIn("RGE-PLAN-009", {finding.rule_id for finding in validate_plan(root)})

    def test_moving_rg0_validator_to_later_phase_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/08-implementation-phases.md",
                "- focused split/coverage/schema validator and mutation fixtures",
                "- focused split/coverage/schema validator and mutation fixtures (delivered in RG-1)",
            )
            self.assertIn("RGE-PLAN-011", {finding.rule_id for finding in validate_plan(root)})

    def test_phase_exit_registry_should_not_unlock_later_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}.md",
                "RG-1 task is created and ready-for-dev; RG-1 implementation has not started.",
                "RG-2 exited; RG-3 implementation is allowed.",
            )
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/96-global-review-and-split-validation.md",
                "RG-1 task creation only; RG-1 implementation remains unstarted",
                "RG-3 implementation",
            )
            self.assertIn("RGE-PLAN-011", {finding.rule_id for finding in validate_plan(root)})

    def test_phase_exit_should_reject_additional_contradictory_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "execution-plans" / f"{PLAN_NAME}.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text + "\n- Current step override: RG-3 implementation is allowed.\n", encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-011", {finding.rule_id for finding in validate_plan(root)})

    def test_profile_mode_promotion_before_rg5_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                "scripts/sc/config/delivery_profiles.json",
                '"review_evidence": {\n        "mode": "advisory"',
                '"review_evidence": {\n        "mode": "require"',
            )
            self.assertIn("RGE-PLAN-013", {finding.rule_id for finding in validate_plan(root)})

    def test_malformed_profile_should_return_finding_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/config/delivery_profiles.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["profiles"]["standard"] = "invalid"
            path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-013", {finding.rule_id for finding in validate_plan(root)})

    def test_required_rg0_adversarial_mutation_families_should_fail(self) -> None:
        mutations = [
            (
                f"execution-plans/{PLAN_NAME}/96-global-review-and-split-validation.md",
                "| authority, scope, invariants | 01 |",
                "| authority, scope, invariants | 01 |\n| authority, scope, invariants | 03 |",
            ),
            (
                f"execution-plans/{PLAN_NAME}/02-review-evidence-contracts-and-severity.md",
                "| P1 / HIGH | high | high |",
                "| P1 / HIGH | high | high |\n| P1 / HIGH | medium | medium |",
            ),
            (
                f"execution-plans/{PLAN_NAME}/04-chapter6-review-ingestion-and-residual-closure.md",
                "- no decision log",
                "- create an empty decision log",
            ),
            (
                f"execution-plans/{PLAN_NAME}/03-chapter3-5-evidence-profiles.md",
                "Deterministic validators remain authoritative for schema, refs, IDs, and coverage thresholds.",
                "LLM reviewers are authoritative for schema, refs, IDs, and coverage thresholds.",
            ),
        ]
        for relative, old, new in mutations:
            with self.subTest(relative=relative, old=old):
                with tempfile.TemporaryDirectory() as td:
                    root = self._copy_fixture(Path(td))
                    self._mutate(root, relative, old, new)
                    self.assertIn("RGE-PLAN-015", {finding.rule_id for finding in validate_plan(root)})

        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "execution-plans" / f"{PLAN_NAME}.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text + "\n## Severity Normalization\n\nP1 maps to medium in this top-level authority.\n",
                encoding="utf-8",
                newline="\n",
            )
            self.assertIn("RGE-PLAN-015", {finding.rule_id for finding in validate_plan(root)})

    def test_research_source_should_not_escape_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            outside = root.parent / "outside-review-source.md"
            outside.write_text("# Outside\n", encoding="utf-8", newline="\n")
            path = root / f"execution-plans/{PLAN_NAME}/98-research-to-split-audit.md"
            text = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(outside.read_bytes()).hexdigest()
            text = re.sub(r"- `_bmad-output/[^`]+`", "- `../outside-review-source.md`", text, count=1)
            text = re.sub(r"- SHA-256: `[0-9a-f]{64}`", f"- SHA-256: `{digest}`", text, count=1)
            text = re.sub(r"- UTF-8 line count: `\d+`", "- UTF-8 line count: `1`", text, count=1)
            path.write_text(text, encoding="utf-8", newline="\n")
            findings = validate_plan(root)
            self.assertTrue(any(item.rule_id == "RGE-PLAN-006" and "escapes" in item.message for item in findings))

    def test_other_malformed_required_inputs_should_return_stable_findings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            (root / f"execution-plans/{PLAN_NAME}/01-authority-scope-and-invariants.md").unlink()
            self.assertIn("RGE-PLAN-001", {finding.rule_id for finding in validate_plan(root)})

        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/99-source-coverage.md",
                "| 01 | RGR-001, RGR-002 |",
                "| 01 | RGR-001, RGR-002 | unexpected |",
            )
            self.assertIn("RGE-PLAN-005", {finding.rule_id for finding in validate_plan(root)})

        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
            path.write_text("[]\n", encoding="utf-8", newline="\n")
            self.assertIn("RGE-PLAN-007", {finding.rule_id for finding in validate_plan(root)})

        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/96-global-review-and-split-validation.md",
                "## Authority Families",
                "## Removed Authority Families",
            )
            findings = validate_plan(root)
            self.assertIn("RGE-PLAN-015", {finding.rule_id for finding in findings})

    def test_removing_untrusted_reviewer_invariant_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/01-authority-scope-and-invariants.md",
                "1. A reviewer is an evidence proposer, not an authority.",
                "1. A reviewer is the final authority.",
            )
            self.assertIn("RGE-PLAN-014", {finding.rule_id for finding in validate_plan(root)})

    def test_removing_chapter6_domain_should_fail_with_stable_rule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._copy_fixture(Path(td))
            self._mutate(
                root,
                f"execution-plans/{PLAN_NAME}/04-chapter6-review-ingestion-and-residual-closure.md",
                "### Performance Reviewer",
                "### Generic Reviewer",
            )
            self.assertIn("RGE-PLAN-014", {finding.rule_id for finding in validate_plan(root)})


if __name__ == "__main__":
    unittest.main()
