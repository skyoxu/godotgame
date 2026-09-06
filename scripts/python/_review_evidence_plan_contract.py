from __future__ import annotations

import hashlib
import json
from typing import Any


SCHEMA_REQUIRED = {
    "top": {
        "schema_version", "policy_version", "mode", "chapter", "review_domain", "reviewer",
        "task_id", "run_id", "raw_verdict", "derived_verdict", "findings", "summary",
    },
    "anchor": {
        "anchor_type", "path", "start_line", "end_line", "heading", "field_path",
        "stable_id", "quote", "artifact_hash",
    },
    "failure_chain": {"source_or_trigger", "state_or_representation", "bad_result_or_consequence"},
    "validation": {"state", "reason_codes", "final_severity"},
    "finding": {
        "finding_id", "title", "message", "original_severity", "normalized_severity", "confidence",
        "anchors", "quote_or_snippet", "failure_chain", "context_inspected", "existing_safeguard_gap",
        "severity_rationale", "suggested_change", "fingerprint", "validation",
    },
    "summary": {
        "proposed_count", "validated_count", "demoted_count", "dropped_count",
        "unknown_count", "actionable_count", "highest_severity",
    },
}
SCHEMA_CONTRACT_SHA256 = "29a135fc4b31de14448e7c54f79730c7986f16d78fa4674e994b4cd8cf7c19fe"
POINTER_FIELDS = {"$schema", "$id", "title", "$comment", "type", "x-canonical-schema"}
EXPECTED_DOMAINS = {
    "task-planning", "architecture-document", "semantic", "code", "security",
    "test", "architecture", "performance", "ui",
}
EXPECTED_MODES = {"playable-ea": "legacy-observe", "fast-ship": "advisory", "standard": "advisory"}
PHASE_PREDECESSORS = {
    "RG-HANDOFF": "completed research and split-plan validation",
    "RG-0": "RG-HANDOFF", "RG-1": "RG-0", "RG-2": "RG-1",
    "RG-3": "RG-2", "RG-4": "RG-3", "RG-5": "RG-4",
}
RG0_DELIVERABLES = {
    "- focused split/coverage/schema validator and mutation fixtures",
    "- phase-sequence validator that rejects an exit when its required implementation or evidence belongs only to a later phase",
    "- schema-level P0/P1 proof-presence and verdict-consistency validation",
    "- summary count and highest-actionable-final-severity consistency validation",
}
RG0_CURRENT_STEP = "- Current step: RG-1 task is created and ready-for-dev; RG-1 implementation has not started."
RG0_EXIT_SCOPE = "| RG-0 | Closed | ADR-0032 and RG-0 exit review | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/` | RG-1 task creation only; RG-1 implementation remains unstarted |"
AUTHORITY_FAMILIES = {
    "authority, scope, invariants", "schema, anchors, states, severity, verdict", "Chapter 3-5 profiles",
    "Chapter 6 ingestion and residual closure", "Chapter 7 UI evidence", "pipeline, recovery, compatibility, rollback",
    "metrics, replay, retention, performance", "phases and task sizing", "risks, DoD, glossary, stop conditions",
    "global review and validation", "post-split requirements", "research mapping", "source coverage",
}
SEVERITY_ROWS = {
    "| P0 / CRITICAL | critical | high |", "| P1 / HIGH | high | high |",
    "| P2 / MEDIUM | medium | medium |", "| P3 / LOW | low | low |",
}
TOP_LEVEL_H2 = {"## Authority", "## Gate Summary", "## Implementation Books", "## Global Order", "## Global Completion"}
REQUIRED_AUTHORITY = {
    "1. A reviewer is an evidence proposer, not an authority.",
    "2. A derived reviewer `Needs Fix` verdict and its compatibility projection require one or more validated actionable findings; legacy producer status may be retained only as explicitly declared compatibility data.",
    "3. Zero surviving actionable findings derives `OK`.",
    "4. Missing input, a missing/unparseable required sidecar, parse failure, or unverifiable evidence derives `Unknown`; compatibility modes may retain producer status but cannot relabel the derived verdict.",
    "2. Accepted ADR and workflow policy", "5. User-scoped or external agent prompt",
}
EXPECTED_REVIEWER_PROFILES = {
    "### Code Reviewer", "### Security Auditor", "### Test Reviewer",
    "### Semantic Reviewer", "### Architecture Reviewer", "### Performance Reviewer",
}


def schema_contract_errors(schema: dict[str, Any], pointer: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    canonical = json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != SCHEMA_CONTRACT_SHA256:
        errors.append(("schema", "canonical schema content differs from the frozen v1 contract"))
        if pointer.get("x-canonical-schema") != "scripts/sc/schemas/review-evidence.v1.schema.json":
            errors.append(("pointer", "plan schema must reference the canonical schema"))
        if set(pointer) != POINTER_FIELDS:
            errors.append(("pointer", "plan schema pointer must contain only non-normative pointer fields"))
        return errors
    if schema.get("$id") != "https://godotgame.local/schemas/review-evidence.v1.schema.json":
        errors.append(("schema", "canonical schema ID is not repository-owned"))
    domains = set((((schema.get("properties") or {}).get("review_domain") or {}).get("enum") or []))
    if domains != EXPECTED_DOMAINS:
        errors.append(("schema", "review domain catalog is incomplete or duplicated"))
    if schema.get("additionalProperties") is not False:
        errors.append(("schema", "top-level additionalProperties must remain false"))
    required_sets = {"top": set(schema.get("required") or [])}
    definitions = schema.get("$defs") or {}
    for name in ("anchor", "failure_chain", "validation", "finding", "summary"):
        definition = definitions.get(name) or {}
        required_sets[name] = set((definition.get("required") or []))
        if definition.get("additionalProperties") is not False:
            errors.append(("schema", f"{name} additionalProperties must remain false"))
    for name, expected in SCHEMA_REQUIRED.items():
        if required_sets.get(name) != expected:
            errors.append(("schema", f"{name} required-field catalog differs from the frozen v1 contract"))
    if pointer.get("x-canonical-schema") != "scripts/sc/schemas/review-evidence.v1.schema.json":
        errors.append(("pointer", "plan schema must reference the canonical schema"))
    if set(pointer) != POINTER_FIELDS:
        errors.append(("pointer", "plan schema pointer must contain only non-normative pointer fields"))
    return errors


def phase_contract_errors(
    *, phase_text: str, top_text: str, history_text: str, actual_predecessors: dict[str, str]
) -> list[str]:
    errors: list[str] = []
    if actual_predecessors != PHASE_PREDECESSORS:
        errors.append(f"phase predecessor matrix differs: {actual_predecessors}")
    rg0_start = phase_text.find("## Phase RG-0:")
    rg1_start = phase_text.find("## Phase RG-1:")
    rg0_lines = set(phase_text[rg0_start:rg1_start].splitlines()) if 0 <= rg0_start < rg1_start else set()
    errors.extend(f"RG-0 deliverable is missing or assigned later: {item}" for item in sorted(RG0_DELIVERABLES - rg0_lines))
    if RG0_CURRENT_STEP not in top_text:
        errors.append("top-level current step must preserve the RG-0 exit and RG-1 task-only boundary")
    current_steps = [line for line in top_text.splitlines() if line.startswith("- Current step")]
    if current_steps != [RG0_CURRENT_STEP]:
        errors.append("top-level plan must contain exactly one non-contradictory current-step statement")
    if RG0_EXIT_SCOPE not in history_text:
        errors.append("phase exit registry must unlock RG-1 task creation only")
    return errors


def adversarial_contract_errors(*, top: str, book02: str, book03: str, book04: str, book96: str) -> list[str]:
    errors: list[str] = []
    if "## Authority Families" not in book96 or "## Global Review Inputs" not in book96:
        errors.append("authority family registry must contain one unique owner row per frozen family")
    else:
        authority_section = book96.split("## Authority Families", 1)[1].split("## Global Review Inputs", 1)[0]
        authority_rows = [line.strip().strip("|").split("|")[0].strip() for line in authority_section.splitlines() if line.startswith("|") and "---" not in line and "Requirement family" not in line]
        if set(authority_rows) != AUTHORITY_FAMILIES or len(authority_rows) != len(set(authority_rows)):
            errors.append("authority family registry must contain one unique owner row per frozen family")
    severity_rows = {line for line in book02.splitlines() if line.startswith("| P") and " / " in line}
    if severity_rows != SEVERITY_ROWS:
        errors.append("severity normalization table must contain exactly one frozen mapping per severity family")
    if "- no decision log" not in book04 or "create an empty decision log" in book04:
        errors.append("empty residual state must not create a decision log")
    if "Deterministic validators remain authoritative for schema, refs, IDs, and coverage thresholds." not in book03:
        errors.append("Chapter 3-5 deterministic authority statement is missing")
    h2 = {line for line in top.splitlines() if line.startswith("## ")}
    if h2 != TOP_LEVEL_H2:
        errors.append("top-level recovery file must remain an index without normative contract expansion")
    return errors


def core_policy_errors(*, authority: str, chapter6: str) -> list[tuple[str, str]]:
    errors = [
        ("authority", f"core authority invariant is missing: {statement}")
        for statement in sorted(REQUIRED_AUTHORITY) if statement not in authority
    ]
    profiles = {line for line in chapter6.splitlines() if line.startswith("### ") and line.endswith(("Reviewer", "Auditor"))}
    if not EXPECTED_REVIEWER_PROFILES.issubset(profiles):
        errors.append(("chapter6", "Chapter 6 reviewer profile catalog is incomplete"))
    return errors


def compatibility_contract_errors(*, adr_text: str, compatibility_text: str) -> list[str]:
    errors: list[str] = []
    for mode in ("legacy-observe", "advisory", "warn", "require"):
        if sum(line.startswith(f"| `{mode}` |") for line in compatibility_text.splitlines()) != 1:
            errors.append(f"compatibility mode must appear exactly once: {mode}")
    unknown_row = next((line for line in compatibility_text.splitlines() if line.startswith("| derived Unknown with zero actionable findings |")), "")
    if not unknown_row or not all(value in unknown_row for value in ("`block`", "review-evidence-unknown", "`resume`")):
        errors.append("Unknown projection must be block/review-evidence-unknown/resume")
    if "Derived `OK` projects as `review_verdict=pass` and `recommended_action=none`." not in adr_text:
        errors.append("ADR clean projection must be pass/none")
    return errors


def ledger_status_errors(text: str) -> list[str]:
    errors: list[str] = []
    if "## Requirements" not in text or "## Requirement Status Registry" not in text:
        return ["requirements ledger must contain requirements and status registry sections"]
    requirement_text = text.split("## Requirements", 1)[1].split("## Requirement Status Registry", 1)[0]
    registry_text = text.split("## Requirement Status Registry", 1)[1].split("## Research Finding Coverage", 1)[0]
    requirements: dict[str, str] = {}
    for line in requirement_text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("| RGR-") and len(cells) == 7:
            requirements[cells[0]] = cells[1]
    transitions: dict[str, list[tuple[str, str]]] = {}
    for line in registry_text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("| RGR-"):
            continue
        if len(cells) != 5:
            errors.append(f"status transition row must have five fields: {line}")
            continue
        transitions.setdefault(cells[0], []).append((cells[1], cells[2]))
    for req_id, status in requirements.items():
        rows = transitions.get(req_id, [])
        if status in {"Closed", "Superseded"} and rows != [("Active", status)]:
            errors.append(f"{req_id} must have exactly one Active-to-{status} status transition")
        if status == "Active" and rows:
            errors.append(f"{req_id} is Active but already has a terminal status transition")
    for req_id in transitions.keys() - requirements.keys():
        errors.append(f"status transition references unknown requirement: {req_id}")
    return errors


def profile_contract_errors(payload: Any) -> list[str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("profiles"), dict):
        return ["profiles must be an object"]
    errors: list[str] = []
    for profile, mode in EXPECTED_MODES.items():
        item = payload["profiles"].get(profile)
        if not isinstance(item, dict):
            errors.append(f"{profile} profile must be an object")
            continue
        review_evidence = item.get("review_evidence")
        agent_review = item.get("agent_review")
        if not isinstance(review_evidence, dict) or review_evidence.get("mode") != mode:
            errors.append(f"{profile} review_evidence.mode must remain {mode} through RG-4")
        if not isinstance(agent_review, dict):
            errors.append(f"{profile} must configure review_evidence independently from agent_review")
    return errors
