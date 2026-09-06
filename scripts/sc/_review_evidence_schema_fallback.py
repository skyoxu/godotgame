from __future__ import annotations

import re
from typing import Any


SEVERITIES = {"critical", "high", "medium", "low", "none"}
ACTIONABLE_STATES = {"validated", "demoted"}
SEVERITY_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
NORMALIZED_SEVERITY = {
    "P0": "critical",
    "CRITICAL": "critical",
    "P1": "high",
    "HIGH": "high",
    "P2": "medium",
    "MEDIUM": "medium",
    "P3": "low",
    "LOW": "low",
}
MODES = {"legacy-observe", "advisory", "warn", "require"}
CHAPTERS = {3, 4, 5, 6, 7}
DOMAINS = {
    "task-planning", "architecture-document", "semantic", "code", "security",
    "test", "architecture", "performance", "ui",
}
RAW_VERDICTS = {"OK", "Needs Fix", "Unknown", "Unparsed"}
DERIVED_VERDICTS = {"OK", "Needs Fix", "Unknown"}
ANCHOR_TYPES = {"code-line", "document-line", "structured-field", "task", "artifact", "screenshot"}
REASON_CODE_RE = re.compile(r"^[a-z][a-z0-9_-]*\.[a-z0-9_.-]+$")
REASON_CODE_FAMILIES = {
    "schema", "anchor", "quote", "context", "failure_chain", "safeguard_gap",
    "severity", "scope", "duplicate", "false_positive", "input", "verdict",
}
CHAPTER_DOMAINS = {
    3: {"task-planning"},
    4: {"architecture-document"},
    5: {"semantic"},
    6: {"code", "security", "test", "semantic", "architecture", "performance"},
    7: {"ui"},
}


def _text(value: Any) -> str:
    try:
        return str(value or "").strip()
    except (ValueError, OverflowError):
        return ""


def _error(rule_id: str, path: str, message: str) -> str:
    return f"{rule_id} {path}: {message}"


def _is_allowed(value: Any, allowed: set[Any]) -> bool:
    try:
        return value in allowed
    except TypeError:
        return False


def _chapter_key(value: Any) -> int | None:
    return int(value) if _is_allowed(value, CHAPTERS) and not isinstance(value, bool) else None


def _is_non_negative_integer(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= 0
    return isinstance(value, float) and value >= 0 and value.is_integer()


def _is_repository_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.strip().replace("\\", "/")
    return not normalized.startswith("/") and ":" not in normalized and ".." not in normalized.split("/")


def _validate_identity(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("reviewer", "task_id", "run_id"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(_error("RGE-SCHEMA-002", f"$.{field}", "must be a non-empty string"))
    task_id = payload.get("task_id") if isinstance(payload.get("task_id"), str) else ""
    chapter = payload.get("chapter")
    if task_id.startswith("scope:"):
        parts = task_id.split(":", 2)
        if len(parts) != 3 or parts[1] != str(_chapter_key(chapter)) or not parts[2].strip():
            errors.append(
                _error("RGE-SCHEMA-002", "$.task_id", "synthetic identity must be scope:<chapter>:<stable-scope-id>")
            )
    return errors


def _validate_finding(finding: Any, index: int) -> list[str]:
    path = f"$.findings[{index}]"
    if not isinstance(finding, dict):
        return [_error("RGE-SCHEMA-003", path, "must be an object")]
    errors: list[str] = []
    required_fields = {
        "finding_id", "title", "message", "original_severity", "normalized_severity", "confidence",
        "anchors", "quote_or_snippet", "failure_chain", "context_inspected", "existing_safeguard_gap",
        "severity_rationale", "suggested_change", "fingerprint", "validation",
    }
    if set(finding) != required_fields:
        errors.append(_error("RGE-SCHEMA-003", path, "must contain exactly the canonical finding fields"))
    for field in sorted(required_fields - set(finding)):
        errors.append(_error("RGE-SCHEMA-003", f"{path}.{field}", "is required"))
    for field in ("finding_id", "title", "message", "fingerprint"):
        value = finding.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(_error("RGE-SCHEMA-003", f"{path}.{field}", "must be non-empty"))
    confidence = finding.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        errors.append(_error("RGE-SCHEMA-003", f"{path}.confidence", "must be a number from zero to one"))

    anchors = finding.get("anchors")
    if not isinstance(anchors, list):
        errors.append(_error("RGE-SCHEMA-003", f"{path}.anchors", "must be an array"))
    else:
        anchor_fields = {
            "anchor_type", "path", "start_line", "end_line", "heading", "field_path",
            "stable_id", "quote", "artifact_hash",
        }
        for anchor_index, anchor in enumerate(anchors):
            anchor_path = f"{path}.anchors[{anchor_index}]"
            if not isinstance(anchor, dict):
                errors.append(_error("RGE-SCHEMA-003", anchor_path, "must be an object"))
                continue
            if set(anchor) != anchor_fields:
                errors.append(_error("RGE-SCHEMA-003", anchor_path, "must contain exactly the canonical anchor fields"))
            if not _is_allowed(anchor.get("anchor_type"), ANCHOR_TYPES):
                errors.append(_error("RGE-SCHEMA-003", f"{anchor_path}.anchor_type", "has an invalid value"))
            for field in ("path", "heading", "field_path", "stable_id", "quote", "artifact_hash"):
                if not isinstance(anchor.get(field), str):
                    errors.append(_error("RGE-SCHEMA-003", f"{anchor_path}.{field}", "must be a string"))
            start_line = anchor.get("start_line")
            end_line = anchor.get("end_line")
            if start_line is not None and (not _is_non_negative_integer(start_line) or start_line < 1):
                errors.append(_error("RGE-SCHEMA-003", f"{anchor_path}.start_line", "must be null or an integer >= 1"))
            if end_line is not None and (not _is_non_negative_integer(end_line) or end_line < 1):
                errors.append(_error("RGE-SCHEMA-003", f"{anchor_path}.end_line", "must be null or an integer >= 1"))
            if _is_non_negative_integer(start_line) and _is_non_negative_integer(end_line) and end_line < start_line:
                errors.append(_error("RGE-SCHEMA-003", anchor_path, "end_line must not precede start_line"))

    original = _text(finding.get("original_severity")).upper()
    normalized = _text(finding.get("normalized_severity")).lower()
    expected = NORMALIZED_SEVERITY.get(original)
    if expected is None or normalized != expected:
        errors.append(
            _error("RGE-SCHEMA-004", f"{path}.normalized_severity", f"must map {original or '<empty>'} to {expected}")
        )

    for field in ("quote_or_snippet", "existing_safeguard_gap", "severity_rationale", "suggested_change"):
        if not isinstance(finding.get(field), str):
            errors.append(_error("RGE-SCHEMA-003", f"{path}.{field}", "must be a string"))
    context = finding.get("context_inspected")
    if (
        not isinstance(context, list)
        or any(not isinstance(item, str) for item in context)
        or len(context) != len(set(context))
    ):
        errors.append(_error("RGE-SCHEMA-003", f"{path}.context_inspected", "must contain unique strings"))
    failure_chain = finding.get("failure_chain")
    failure_fields = {"source_or_trigger", "state_or_representation", "bad_result_or_consequence"}
    if (
        not isinstance(failure_chain, dict)
        or set(failure_chain) != failure_fields
        or any(not isinstance(failure_chain.get(field), str) for field in failure_fields)
    ):
        errors.append(_error("RGE-SCHEMA-003", f"{path}.failure_chain", "must contain exactly the canonical string fields"))

    validation = finding.get("validation")
    if not isinstance(validation, dict):
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation", "must be an object"))
        return errors
    if set(validation) != {"state", "reason_codes", "final_severity"}:
        errors.append(_error("RGE-SCHEMA-003", f"{path}.validation", "must contain exactly the canonical validation fields"))
    state = _text(validation.get("state")).lower()
    final_severity = _text(validation.get("final_severity")).lower()
    if state not in {"validated", "demoted", "dropped", "unknown"}:
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation.state", "has an invalid disposition"))
    if not _is_allowed(final_severity, SEVERITIES):
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation.final_severity", "has an invalid severity"))
    if state in {"dropped", "unknown"} and final_severity != "none":
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation.final_severity", "must be none when non-actionable"))
    if _is_allowed(state, ACTIONABLE_STATES) and final_severity == "none":
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation.final_severity", "must be non-none when actionable"))
    if state == "validated" and final_severity != normalized:
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation.final_severity", "must equal normalized severity when validated"))
    if state == "demoted" and SEVERITY_RANK.get(final_severity, 99) >= SEVERITY_RANK.get(normalized, -1):
        errors.append(_error("RGE-SCHEMA-005", f"{path}.validation.final_severity", "must be lower after demotion"))
    reason_codes = validation.get("reason_codes")
    valid_reason_codes = isinstance(reason_codes, list) and all(isinstance(code, str) for code in reason_codes)
    if (
        not valid_reason_codes
        or len(reason_codes) != len(set(reason_codes))
        or any(not REASON_CODE_RE.fullmatch(code) or code.split(".", 1)[0] not in REASON_CODE_FAMILIES for code in reason_codes)
    ):
        errors.append(_error("RGE-SCHEMA-003", f"{path}.validation.reason_codes", "must contain unique stable reason codes"))
    if _is_allowed(state, {"demoted", "dropped", "unknown"}) and valid_reason_codes and not reason_codes:
        errors.append(_error("RGE-SCHEMA-003", f"{path}.validation.reason_codes", "must explain a non-validated disposition"))

    if _is_allowed(state, ACTIONABLE_STATES):
        exact_anchor = False
        if isinstance(anchors, list):
            for anchor in anchors:
                if not isinstance(anchor, dict):
                    continue
                anchor_type = anchor.get("anchor_type")
                path_value = anchor.get("path")
                has_path = _is_repository_relative_path(path_value)
                if _is_allowed(anchor_type, {"code-line", "document-line"}):
                    exact_anchor = has_path and _is_non_negative_integer(anchor.get("start_line")) and anchor.get("start_line") >= 1
                elif anchor_type == "structured-field":
                    exact_anchor = has_path and bool(_text(anchor.get("field_path")))
                elif anchor_type == "task":
                    exact_anchor = bool(_text(anchor.get("stable_id")))
                elif _is_allowed(anchor_type, {"artifact", "screenshot"}):
                    exact_anchor = has_path and bool(_text(anchor.get("stable_id")) or _text(anchor.get("artifact_hash")))
                if exact_anchor:
                    break
        if not exact_anchor:
            errors.append(_error("RGE-SCHEMA-006", path, "actionable finding requires an exact repository anchor"))

    if _is_allowed(state, ACTIONABLE_STATES) and _is_allowed(final_severity, {"critical", "high"}):
        proof_values = [
            bool(_text(finding.get("quote_or_snippet"))),
            isinstance(failure_chain, dict)
            and all(_text(failure_chain.get(key)) for key in (
                "source_or_trigger",
                "state_or_representation",
                "bad_result_or_consequence",
            )),
            isinstance(finding.get("context_inspected"), list)
            and bool(finding.get("context_inspected"))
            and all(_text(item) for item in finding.get("context_inspected")),
            bool(_text(finding.get("existing_safeguard_gap"))),
            bool(_text(finding.get("severity_rationale"))),
        ]
        if not all(proof_values):
            errors.append(_error("RGE-SCHEMA-006", path, "critical/high finding requires the complete proof bundle"))
    return errors


def _validate_summary(payload: dict[str, Any]) -> list[str]:
    findings = payload.get("findings")
    summary = payload.get("summary")
    if not isinstance(findings, list) or not isinstance(summary, dict):
        return [_error("RGE-SCHEMA-007", "$.summary", "findings must be an array and summary must be an object")]
    summary_fields = {
        "proposed_count", "validated_count", "demoted_count", "dropped_count",
        "unknown_count", "actionable_count", "highest_severity",
    }
    if set(summary) != summary_fields:
        return [_error("RGE-SCHEMA-007", "$.summary", "must contain exactly the canonical summary fields")]

    counts = {state: 0 for state in ("validated", "demoted", "dropped", "unknown")}
    actionable_severities: list[str] = []
    for finding in findings:
        validation = finding.get("validation") if isinstance(finding, dict) else None
        if not isinstance(validation, dict):
            continue
        state = _text(validation.get("state")).lower()
        if state in counts:
            counts[state] += 1
        if _is_allowed(state, ACTIONABLE_STATES):
            actionable_severities.append(_text(validation.get("final_severity")).lower())

    expected = {
        "proposed_count": len(findings),
        "validated_count": counts["validated"],
        "demoted_count": counts["demoted"],
        "dropped_count": counts["dropped"],
        "unknown_count": counts["unknown"],
        "actionable_count": len(actionable_severities),
    }
    errors: list[str] = []
    for key in expected:
        value = summary.get(key)
        if not _is_non_negative_integer(value):
            errors.append(_error("RGE-SCHEMA-007", f"$.summary.{key}", "must be a non-negative integer"))
    errors.extend([
        _error("RGE-SCHEMA-007", f"$.summary.{key}", f"expected {value}")
        for key, value in expected.items()
        if summary.get(key) != value
    ])
    highest = max(actionable_severities, key=lambda item: SEVERITY_RANK.get(item, -1), default="none")
    if summary.get("highest_severity") != highest:
        errors.append(_error("RGE-SCHEMA-008", "$.summary.highest_severity", f"expected {highest}"))

    verdict = payload.get("derived_verdict")
    if actionable_severities:
        expected_verdict = "Needs Fix"
    elif counts["unknown"] or _is_allowed(payload.get("raw_verdict"), {"Unknown", "Unparsed"}):
        expected_verdict = "Unknown"
    else:
        expected_verdict = "OK"
    if verdict != expected_verdict:
        errors.append(_error("RGE-SCHEMA-009", "$.derived_verdict", f"expected {expected_verdict}"))
    return errors


def validate_review_evidence_without_jsonschema(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return [_error("RGE-SCHEMA-001", "$", "must be an object")]
    required = {
        "schema_version", "policy_version", "mode", "chapter", "review_domain", "reviewer",
        "task_id", "run_id", "raw_verdict", "derived_verdict", "findings", "summary",
    }
    errors = [
        _error("RGE-SCHEMA-001", f"$.{field}", "is required")
        for field in sorted(required - set(payload))
    ]
    if errors:
        return errors
    if set(payload) != required:
        errors.append(_error("RGE-SCHEMA-001", "$", "must contain exactly the canonical top-level fields"))
    enum_expectations = {
        "schema_version": {"1.0.0"},
        "mode": MODES,
        "chapter": CHAPTERS,
        "review_domain": DOMAINS,
        "raw_verdict": RAW_VERDICTS,
        "derived_verdict": DERIVED_VERDICTS,
    }
    for field, allowed in enum_expectations.items():
        if not _is_allowed(payload.get(field), allowed):
            errors.append(_error("RGE-SCHEMA-001", f"$.{field}", "has an invalid value"))
    if not isinstance(payload.get("policy_version"), str) or not payload["policy_version"].strip():
        errors.append(_error("RGE-SCHEMA-001", "$.policy_version", "must be a non-empty string"))
    chapter = payload.get("chapter")
    chapter_domains = CHAPTER_DOMAINS.get(_chapter_key(chapter), set())
    if not _is_allowed(payload.get("review_domain"), chapter_domains):
        errors.append(_error("RGE-SCHEMA-001", "$.review_domain", "is invalid for the selected chapter"))
    errors.extend(_validate_identity(payload))
    findings = payload.get("findings")
    if not isinstance(findings, list):
        errors.append(_error("RGE-SCHEMA-003", "$.findings", "must be an array"))
        return errors
    for index, finding in enumerate(findings):
        errors.extend(_validate_finding(finding, index))
    finding_ids = [item.get("finding_id") for item in findings if isinstance(item, dict) and isinstance(item.get("finding_id"), str)]
    fingerprints = [
        item.get("fingerprint") for item in findings
        if isinstance(item, dict)
        and isinstance(item.get("fingerprint"), str)
        and isinstance(item.get("validation"), dict)
        and _is_allowed(item["validation"].get("state"), ACTIONABLE_STATES)
    ]
    if len(finding_ids) != len(set(finding_ids)):
        errors.append(_error("RGE-SCHEMA-010", "$.findings", "finding_id values must be unique"))
    if len(fingerprints) != len(set(fingerprints)):
        errors.append(_error("RGE-SCHEMA-010", "$.findings", "fingerprint values must be unique"))
    errors.extend(_validate_summary(payload))
    return errors
