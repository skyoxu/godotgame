---
ADR-ID: ADR-0032
title: Review Evidence Gate
status: Accepted
decision-time: '2026-07-12'
deciders: [repository maintainers]
archRefs: [CH07, CH09]
verification:
  - path: scripts/sc/schemas/review-evidence.v1.schema.json
    assert: Canonical sidecar schema preserves evidence, disposition, severity, identity, and derived-summary invariants
  - path: scripts/sc/_review_evidence_schema.py
    assert: Runtime-capable schema loader validates with jsonschema when available and a repository fallback otherwise
  - path: scripts/python/validate_review_evidence_plan.py
    assert: Split-plan authority, coverage, source audit, schema, compatibility, and phase sequencing remain deterministic
  - path: scripts/sc/config/delivery_profiles.json
    assert: Review evidence mode is configured independently from agent review enforcement
impact-scope:
  - scripts/sc/
  - scripts/python/
  - docs/workflows/
  - docs/agents/
  - execution-plans/
tech-tags: [review, evidence, llm, sidecar, quality-gates, recovery]
depends-on: [ADR-0005, ADR-0017]
depended-by: []
supersedes: []
---

# ADR-0032: Review Evidence Gate

## Context

Chapter 3-7 workflows use deterministic checks and LLM-assisted review, but reviewer prose is currently able to create expensive repair and rerun pressure without retaining enough evidence to verify the claim. Historical business-repository runs show empty residual records, missing exact anchors, unsupported severity, verdict flips, and repeated review cycles. ECC demonstrates a useful prompt-level fact gate, but prompt instructions alone are not a trusted runtime boundary.

## Decision

### 1) Trust boundary

- Raw LLM Markdown or JSON is untrusted evidence proposal.
- Repository validators own schema validation, evidence disposition, severity demotion, duplicate identity, summary derivation, and derived verdict.
- Zero surviving actionable findings is a valid `OK` result.
- Missing or unparseable required evidence is `Unknown`, never clean and never a product defect by itself.
- `summary.json` remains producer-owned and unchanged.

### 2) Canonical contract

- Review evidence v1 is a JSON-only sidecar. Raw reviewer Markdown is retained separately when produced.
- `scripts/sc/schemas/review-evidence.v1.schema.json` is the only executable schema authority.
- Every sidecar has non-empty `task_id` and `run_id`; non-task reviews use `scope:<chapter>:<stable-scope-id>`.
- Original severity, pre-validation normalized severity, and final severity remain distinct.
- P0/P1 requires an exact anchor and quote/snippet, a concrete failure or consequence chain, surrounding context, an existing-safeguard gap, and a defensible severity rationale. Missing proof causes demotion or drop.
- Only `validated` and `demoted` findings are actionable. `Needs Fix` requires at least one actionable finding.

### 3) Compatibility

- Existing `agent-review.json` remains the compatibility projection.
- Derived `OK` projects as `review_verdict=pass` and `recommended_action=none`.
- Derived `Needs Fix` projects from actionable evidence into the existing block/action vocabulary.
- Derived `Unknown` projects as `review_verdict=block`, category and reason `review-evidence-unknown`, and `recommended_action=resume`, without creating an actionable product finding or changing producer status.

### 4) Modes and initial profile policy

- Modes are `legacy-observe`, `advisory`, `warn`, and `require`.
- Review-evidence mode is independently owned and must not be inferred from `agent_review.mode`.
- Initial modes are: `playable-ea=legacy-observe`, `fast-ship=advisory`, and `standard=advisory`.
- No profile may move to `warn` or `require` before RG-5 accepts replay metrics, adjudication, rollback evidence, and named ownership.

### 5) Retention and redaction

- Raw logs follow the existing cleanup policy and must not contain newly introduced secrets or absolute user paths.
- Structured summaries, validation dispositions, and aggregate metrics are retained for 30 days by default.
- Sanitized replay fixtures are git-tracked; they contain repository-relative paths and no secrets or personal data.

### 6) Ownership and rollback

- Implementation owner: review-evidence maintainer.
- Independent reviewer: phase-exit reviewer, separate from the implementation pass.
- Rollback owner: review-pipeline maintainer.
- Rollback means restoring the affected profile to `advisory` or `legacy-observe`; it does not delete evidence or mutate producer status.
- New modules use focused `_review_evidence_*` boundaries and remain below the repository 400-line guardrail.

## Consequences

- Reviewer findings become inspectable and deterministic before they influence recovery work.
- Unsupported high severity is demoted or dropped instead of silently trusted.
- The repository gains another versioned sidecar and must maintain schema, fallback validation, compatibility tests, replay fixtures, and retention policy.
- RG-0 freezes policy and contracts only; runtime capture and residual behavior remain RG-1 work.

## Verification

- Canonical schema and example validation, including fallback-path tests.
- Mutation tests for missing elevated proof, invalid identity, severity drift, summary drift, and verdict inconsistency.
- Focused split validator checks authority, ledger, research coverage, compatibility, and phase sequencing.
- Delivery-profile tests prove review-evidence mode is independent from agent-review mode.
