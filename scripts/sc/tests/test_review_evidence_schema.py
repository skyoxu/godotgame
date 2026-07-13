#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[3]
SC_DIR = REPO_ROOT / "scripts" / "sc"
sys.path.insert(0, str(SC_DIR))

from _review_evidence_schema import (  # noqa: E402
    ReviewEvidenceSchemaError,
    load_review_evidence_schema,
    review_evidence_schema_path,
    validate_review_evidence_payload,
)


EXAMPLE_PATH = (
    REPO_ROOT
    / "execution-plans"
    / "2026-07-12-phase-review-evidence-gate-hardening-execution-plan"
    / "schemas"
    / "review-evidence.v1.example.json"
)


class ReviewEvidenceSchemaTests(unittest.TestCase):
    def _example(self) -> dict:
        return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_canonical_schema_should_load_from_scripts_sc(self) -> None:
        path = review_evidence_schema_path()
        self.assertEqual(SC_DIR / "schemas" / "review-evidence.v1.schema.json", path)
        self.assertEqual("Review Evidence Sidecar v1", load_review_evidence_schema()["title"])

    def test_invalid_utf8_canonical_schema_should_return_stable_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "review-evidence.schema.json"
            path.write_bytes(b"\xff")
            with patch("_review_evidence_schema.review_evidence_schema_path", return_value=path):
                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-000"):
                    load_review_evidence_schema()

    def test_invalid_draft_canonical_schema_should_return_stable_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "review-evidence.schema.json"
            path.write_text('{"type": 7}', encoding="utf-8", newline="\n")
            with patch("_review_evidence_schema.review_evidence_schema_path", return_value=path):
                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-000"):
                    load_review_evidence_schema()

    def test_example_should_validate_with_primary_and_fallback_paths(self) -> None:
        payload = self._example()
        validate_review_evidence_payload(payload)
        validate_review_evidence_payload(payload, force_fallback=True)

    def test_elevated_finding_should_require_complete_proof(self) -> None:
        payload = self._example()
        payload["findings"][0]["validation"]["state"] = "validated"
        payload["findings"][0]["validation"]["final_severity"] = "high"
        payload["findings"][0]["existing_safeguard_gap"] = ""
        payload["summary"]["validated_count"] = 1
        payload["summary"]["demoted_count"] = 0
        payload["summary"]["highest_severity"] = "high"

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-006"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_elevated_finding_missing_proof_should_allow_demoted_or_dropped_disposition(self) -> None:
        for state, final_severity in (("demoted", "medium"), ("dropped", "none")):
            with self.subTest(state=state):
                payload = self._example()
                finding = payload["findings"][0]
                finding["existing_safeguard_gap"] = ""
                finding["validation"]["state"] = state
                finding["validation"]["final_severity"] = final_severity
                payload["derived_verdict"] = "Needs Fix" if state == "demoted" else "OK"
                payload["summary"]["validated_count"] = 0
                payload["summary"]["demoted_count"] = 1 if state == "demoted" else 0
                payload["summary"]["dropped_count"] = 1 if state == "dropped" else 0
                payload["summary"]["actionable_count"] = 1 if state == "demoted" else 0
                payload["summary"]["highest_severity"] = final_severity
                validate_review_evidence_payload(payload, force_fallback=True)

    def test_non_validated_disposition_should_require_reason_code(self) -> None:
        for state, final_severity in (("demoted", "medium"), ("dropped", "none"), ("unknown", "none")):
            with self.subTest(state=state):
                payload = self._example()
                finding = payload["findings"][0]
                finding["validation"] = {"state": state, "reason_codes": [], "final_severity": final_severity}
                payload["derived_verdict"] = "Needs Fix" if state == "demoted" else "Unknown" if state == "unknown" else "OK"
                payload["summary"].update({
                    "validated_count": 0, "demoted_count": int(state == "demoted"),
                    "dropped_count": int(state == "dropped"), "unknown_count": int(state == "unknown"),
                    "actionable_count": int(state == "demoted"), "highest_severity": final_severity,
                })
                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_identity_should_reject_empty_task_id(self) -> None:
        payload = self._example()
        payload["task_id"] = ""

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-002"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_synthetic_identity_should_match_chapter_and_stable_scope(self) -> None:
        payload = self._example()
        payload["task_id"] = "scope:6:chapter6-review-policy"
        validate_review_evidence_payload(payload, force_fallback=True)

        payload["task_id"] = "scope:7:chapter6-review-policy"
        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-002"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_reject_invalid_top_level_enums(self) -> None:
        mutations = {
            "schema_version": "2.0.0",
            "mode": "off",
            "chapter": 8,
            "review_domain": "generic",
            "derived_verdict": "Clean",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                payload = self._example()
                payload[field] = value
                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-001"):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_reject_unhashable_top_level_enum_without_crashing(self) -> None:
        payload = self._example()
        payload["mode"] = []

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-001"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_integral_float_chapter_should_match_canonical_integer_semantics(self) -> None:
        payload = self._example()
        payload["chapter"] = 6.0
        validate_review_evidence_payload(payload)
        validate_review_evidence_payload(payload, force_fallback=True)

    def test_integral_float_chapter_should_match_synthetic_identity(self) -> None:
        payload = self._example()
        payload["chapter"] = 6.0
        payload["task_id"] = "scope:6:chapter6-review-policy"
        validate_review_evidence_payload(payload)
        validate_review_evidence_payload(payload, force_fallback=True)

    def test_integral_float_anchor_lines_should_match_canonical_integer_semantics(self) -> None:
        payload = self._example()
        anchor = payload["findings"][0]["anchors"][0]
        anchor["start_line"] = float(anchor["start_line"])
        anchor["end_line"] = float(anchor["end_line"])
        validate_review_evidence_payload(payload)
        validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_reject_invalid_anchor_and_duplicate_reason_code(self) -> None:
        payload = self._example()
        payload["findings"][0]["anchors"][0]["start_line"] = 0
        payload["findings"][0]["validation"]["reason_codes"] = ["anchor.valid", "anchor.valid"]

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_reject_unhashable_anchor_type_without_crashing(self) -> None:
        payload = self._example()
        payload["findings"][0]["anchors"][0]["anchor_type"] = []

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_reject_unhashable_verdict_and_state_without_crashing(self) -> None:
        mutations = (("raw_verdict", []), ("validation.state", []))
        for field, value in mutations:
            with self.subTest(field=field):
                payload = self._example()
                if field == "raw_verdict":
                    payload[field] = value
                    payload["findings"] = []
                    payload["summary"] = {
                        "proposed_count": 0, "validated_count": 0, "demoted_count": 0,
                        "dropped_count": 0, "unknown_count": 0, "actionable_count": 0,
                        "highest_severity": "none",
                    }
                    payload["derived_verdict"] = "OK"
                else:
                    payload["findings"][0]["validation"]["state"] = value
                with self.assertRaises(ReviewEvidenceSchemaError):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_elevated_code_finding_should_reject_placeholder_anchor(self) -> None:
        payload = self._example()
        payload["findings"][0]["validation"]["state"] = "validated"
        payload["findings"][0]["validation"]["final_severity"] = "high"
        payload["summary"]["validated_count"] = 1
        payload["summary"]["demoted_count"] = 0
        payload["summary"]["highest_severity"] = "high"
        anchor = payload["findings"][0]["anchors"][0]
        anchor["path"] = ""
        anchor["start_line"] = None
        anchor["end_line"] = None
        anchor["quote"] = ""

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-006"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_report_non_string_reason_code_instead_of_crashing(self) -> None:
        payload = self._example()
        payload["findings"][0]["validation"]["reason_codes"] = [{"bad": "shape"}]

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_reject_additional_contract_fields(self) -> None:
        payload = self._example()
        payload["unexpected"] = True

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-001"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_validate_proof_field_shapes_for_medium_findings(self) -> None:
        payload = self._example()
        finding = payload["findings"][0]
        finding["original_severity"] = "P2"
        finding["normalized_severity"] = "medium"
        finding["validation"]["state"] = "validated"
        finding["validation"]["final_severity"] = "medium"
        finding["failure_chain"] = None
        finding["context_inspected"] = "not-a-list"
        payload["summary"]["highest_severity"] = "medium"
        payload["summary"]["validated_count"] = 1
        payload["summary"]["demoted_count"] = 0

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_needs_fix_should_require_actionable_finding(self) -> None:
        payload = self._example()
        payload["findings"] = []
        payload["summary"] = {
            "proposed_count": 0,
            "validated_count": 0,
            "demoted_count": 0,
            "dropped_count": 0,
            "unknown_count": 0,
            "actionable_count": 0,
            "highest_severity": "none",
        }

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-009"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_unparsed_raw_verdict_should_never_derive_ok(self) -> None:
        payload = self._example()
        payload["raw_verdict"] = "Unparsed"
        payload["derived_verdict"] = "OK"
        payload["findings"] = []
        payload["summary"] = {
            "proposed_count": 0,
            "validated_count": 0,
            "demoted_count": 0,
            "dropped_count": 0,
            "unknown_count": 0,
            "actionable_count": 0,
            "highest_severity": "none",
        }

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-009"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_unparsed_raw_verdict_should_allow_unknown_without_actionable_findings(self) -> None:
        payload = self._example()
        payload["raw_verdict"] = "Unparsed"
        payload["derived_verdict"] = "Unknown"
        payload["findings"] = []
        payload["summary"] = {
            "proposed_count": 0,
            "validated_count": 0,
            "demoted_count": 0,
            "dropped_count": 0,
            "unknown_count": 0,
            "actionable_count": 0,
            "highest_severity": "none",
        }

        validate_review_evidence_payload(payload, force_fallback=True)

    def test_unparsed_raw_verdict_should_not_override_actionable_findings(self) -> None:
        payload = self._example()
        payload["raw_verdict"] = "Unparsed"

        validate_review_evidence_payload(payload, force_fallback=True)
        validate_review_evidence_payload(payload)

    def test_actionable_finding_should_reject_final_severity_none(self) -> None:
        for state in ("validated", "demoted"):
            with self.subTest(state=state):
                payload = self._example()
                finding = payload["findings"][0]
                finding["validation"]["state"] = state
                finding["validation"]["final_severity"] = "none"
                payload["summary"]["validated_count"] = 1 if state == "validated" else 0
                payload["summary"]["demoted_count"] = 1 if state == "demoted" else 0
                payload["summary"]["highest_severity"] = "none"

                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-005"):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_fallback_should_require_string_identity_and_policy_fields(self) -> None:
        mutations = {
            "policy_version": 1,
            "reviewer": 7,
            "task_id": 225,
            "run_id": {"id": "run"},
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                payload = self._example()
                payload[field] = value
                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-00[12]"):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_reason_code_should_use_declared_family(self) -> None:
        payload = self._example()
        payload["findings"][0]["validation"]["reason_codes"] = ["banana.anything"]

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_chapter_should_reject_another_chapters_review_domain(self) -> None:
        payload = self._example()
        payload["chapter"] = 4
        payload["review_domain"] = "architecture"

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-001"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_medium_actionable_finding_should_require_exact_anchor(self) -> None:
        payload = self._example()
        finding = payload["findings"][0]
        finding["original_severity"] = "P2"
        finding["normalized_severity"] = "medium"
        finding["anchors"] = []
        finding["validation"] = {"state": "validated", "reason_codes": [], "final_severity": "medium"}
        payload["summary"]["validated_count"] = 1
        payload["summary"]["demoted_count"] = 0
        payload["summary"]["highest_severity"] = "medium"

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-006"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_duplicate_finding_identity_should_be_rejected(self) -> None:
        for field in ("finding_id", "fingerprint"):
            with self.subTest(field=field):
                payload = self._example()
                duplicate = copy.deepcopy(payload["findings"][0])
                if field == "finding_id":
                    duplicate["fingerprint"] = "different-family"
                else:
                    duplicate["finding_id"] = "different-id"
                payload["findings"].append(duplicate)
                payload["summary"]["proposed_count"] = 2
                payload["summary"]["demoted_count"] = 2
                payload["summary"]["actionable_count"] = 2

                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-010"):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_elevated_finding_should_reject_blank_context_item(self) -> None:
        payload = self._example()
        finding = payload["findings"][0]
        finding["validation"] = {"state": "validated", "reason_codes": [], "final_severity": "high"}
        finding["context_inspected"] = [""]
        payload["summary"]["validated_count"] = 1
        payload["summary"]["demoted_count"] = 0
        payload["summary"]["highest_severity"] = "high"

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-006"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_actionable_anchor_should_reject_absolute_or_escaping_path(self) -> None:
        for path in (
            "C:/outside/review.py", "C:outside.txt", "../outside/review.py",
            "https://example.invalid/review.py", "res://outside.cs",
        ):
            with self.subTest(path=path):
                payload = self._example()
                payload["findings"][0]["anchors"][0]["path"] = path
                with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-006"):
                    validate_review_evidence_payload(payload, force_fallback=True)

    def test_canonical_schema_should_reject_validated_severity_escalation(self) -> None:
        payload = self._example()
        finding = payload["findings"][0]
        finding["original_severity"] = "P2"
        finding["normalized_severity"] = "medium"
        finding["validation"] = {"state": "validated", "reason_codes": [], "final_severity": "critical"}
        payload["summary"]["validated_count"] = 1
        payload["summary"]["demoted_count"] = 0
        payload["summary"]["highest_severity"] = "critical"

        errors = list(jsonschema.Draft202012Validator(load_review_evidence_schema()).iter_errors(payload))
        self.assertTrue(errors)

    def test_fallback_should_reject_boolean_summary_counts(self) -> None:
        payload = self._example()
        payload["summary"]["actionable_count"] = True

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-007"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_integral_float_summary_count_should_match_canonical_integer_semantics(self) -> None:
        payload = self._example()
        payload["summary"]["proposed_count"] = 1.0
        validate_review_evidence_payload(payload)
        validate_review_evidence_payload(payload, force_fallback=True)

    def test_arbitrary_precision_summary_integer_should_not_crash_fallback(self) -> None:
        payload = self._example()
        payload["summary"]["proposed_count"] = 10**10000
        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-007"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_arbitrary_precision_text_scalar_should_not_crash_fallback(self) -> None:
        payload = self._example()
        payload["findings"][0]["validation"]["state"] = 10**10000
        for force_fallback in (False, True):
            with self.subTest(force_fallback=force_fallback):
                with self.assertRaises(ReviewEvidenceSchemaError):
                    validate_review_evidence_payload(payload, force_fallback=force_fallback)

    def test_canonical_schema_should_enforce_complete_derived_verdict_matrix(self) -> None:
        schema = load_review_evidence_schema()
        clean = self._example()
        clean["raw_verdict"] = "OK"
        clean["derived_verdict"] = "Needs Fix"
        clean["findings"] = []
        clean["summary"] = {
            "proposed_count": 0, "validated_count": 0, "demoted_count": 0,
            "dropped_count": 0, "unknown_count": 0, "actionable_count": 0,
            "highest_severity": "none",
        }
        self.assertTrue(list(jsonschema.Draft202012Validator(schema).iter_errors(clean)))

        unknown = self._example()
        unknown["raw_verdict"] = "OK"
        unknown["derived_verdict"] = "OK"
        unknown["findings"][0]["validation"] = {
            "state": "unknown", "reason_codes": ["input.unverifiable"], "final_severity": "none",
        }
        unknown["summary"] = {
            "proposed_count": 1, "validated_count": 0, "demoted_count": 0,
            "dropped_count": 0, "unknown_count": 1, "actionable_count": 0,
            "highest_severity": "none",
        }
        self.assertTrue(list(jsonschema.Draft202012Validator(schema).iter_errors(unknown)))

    def test_malformed_finding_identity_should_return_schema_error_without_crashing(self) -> None:
        payload = self._example()
        payload["findings"][0]["finding_id"] = ["bad-id"]
        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-003"):
            validate_review_evidence_payload(payload, force_fallback=True)

    def test_dropped_duplicate_fingerprint_should_remain_auditable(self) -> None:
        payload = self._example()
        duplicate = copy.deepcopy(payload["findings"][0])
        duplicate["finding_id"] = "duplicate-proposal"
        duplicate["validation"] = {
            "state": "dropped", "reason_codes": ["duplicate.family"], "final_severity": "none",
        }
        payload["findings"].append(duplicate)
        payload["summary"].update({"proposed_count": 2, "dropped_count": 1})
        validate_review_evidence_payload(payload, force_fallback=True)

    def test_summary_should_use_final_severity_after_demotion(self) -> None:
        payload = copy.deepcopy(self._example())
        finding = payload["findings"][0]
        finding["validation"]["state"] = "demoted"
        finding["validation"]["final_severity"] = "medium"
        payload["summary"]["validated_count"] = 0
        payload["summary"]["demoted_count"] = 1
        payload["summary"]["highest_severity"] = "high"

        with self.assertRaisesRegex(ReviewEvidenceSchemaError, "RGE-SCHEMA-008"):
            validate_review_evidence_payload(payload, force_fallback=True)


if __name__ == "__main__":
    unittest.main()
