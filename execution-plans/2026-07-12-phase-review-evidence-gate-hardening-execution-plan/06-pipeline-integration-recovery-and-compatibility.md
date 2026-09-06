# Pipeline Integration, Recovery, And Compatibility

## Purpose

Integrate evidence-gated review without breaking producer schemas or losing existing recovery behavior.

## Artifact Set

Proposed new task-scoped artifacts:

- `review-evidence-<agent>.json`
- `review-evidence-summary.json`
- optional human-readable `review-evidence-summary.md`
- `review-evidence-metrics.json`

Existing artifacts retained:

- raw `review-<agent>.md`
- `sc-llm-review/summary.json`
- pipeline `summary.json`
- `execution-context.json`
- `repair-guide.json/md`
- `agent-review.json/md`
- `latest.json`
- active-task sidecars
- `run-events.jsonl`

## Ownership

| Artifact | Owner |
| --- | --- |
| raw reviewer output | LLM review producer |
| per-agent evidence | evidence parser/validator |
| evidence summary/metrics | evidence aggregation layer |
| agent-review compatibility | agent review builder |
| route and repair recommendation | existing recovery consumers using validated signals |

## Backward Compatibility

The following matrix is the sole authority for compatibility behavior. `Producer status` means the existing producer-owned `summary.json` status. `Derived verdict` and compatibility projections are evidence-layer outputs and never overwrite producer status.

| Mode | Producer status | Derived verdict | Recovery routing source | Zero actionable findings | Missing/unparseable sidecar | Residual creation |
| --- | --- | --- | --- | --- | --- | --- |
| `legacy-observe` | retained | computed when evidence is usable; otherwise Unknown | legacy producer route, tagged as observation-only | derived OK; no compatibility Needs Fix | derived Unknown; producer status retained | only a non-empty validated medium/low set; otherwise suppressed |
| `advisory` | retained | always recorded | legacy producer route plus visible drift/inspection signal | derived OK; no compatibility Needs Fix | derived Unknown with inspection signal | only a non-empty validated medium/low set; otherwise suppressed |
| `warn` | retained | authoritative for warnings and evidence inspection | derived verdict | derived OK | derived Unknown and inspection action | only a non-empty validated medium/low set; otherwise suppressed |
| `require` | retained | authoritative for evidence enforcement | derived verdict | derived OK | derived Unknown and blocking evidence action, not a product defect | only a non-empty validated medium/low set; otherwise suppressed |

Mode and schema version are recorded in every evidence summary. Empty-residual suppression, derived-verdict rules, and Unknown non-actionability are invariants in every mode.

### Agent-Review Projection Matrix

This matrix is the normative compatibility mapping into the existing `agent-review.json` vocabulary. It introduces no new contract verdict or recommended-action value.

| Evidence condition | `review_verdict` | Finding/explain representation | `recommended_action` | Routing effect |
| --- | --- | --- | --- | --- |
| derived OK and no independent deterministic/artifact block | `pass` | no evidence finding; counts and sidecar pointer remain in explain/context | `none` | clean for the evidence layer |
| derived Needs Fix | `needs-fix` | one compatibility finding per surviving actionable finding | existing policy selects `resume`, `refresh`, or `fork` from validated categories/severity | actionable repair route |
| derived Needs Fix plus an additional Unknown observation | `needs-fix` | actionable findings remain findings; Unknown is an explain reason/category only | action derives from actionable findings; Unknown may add an evidence owner step | repair route plus visible observation gap |
| derived Unknown with zero actionable findings | `block` | no actionable product finding; add category/reason `review-evidence-unknown`, evidence path or missing-input reason, and evidence-generation owner step | `resume` to regenerate or inspect required evidence | observation-only in legacy-observe/advisory; evidence pause in warn/require |
| independent deterministic or required producer-artifact failure | `block` | existing deterministic/artifact-integrity findings | existing agent-review policy | unchanged existing behavior |

The Unknown projection is a recovery evidence block, not a product-defect verdict. It never changes producer status, never creates a code-fix recommendation, and never creates a residual record. In `legacy-observe` and `advisory`, it is visible in agent-review/explain data but cannot replace the matrix's declared legacy routing source. In `warn` and `require`, `resume` means rerun or inspect the evidence-producing step, not rerun a product test that is already green.

## Recovery Fields

Recovery-facing projections should expose:

- evidence mode and schema version
- raw and derived verdict counts
- actionable finding count
- highest actionable final severity
- dropped/demoted/unknown counts
- evidence summary path
- repeated-family signal
- empty-residual suppression reason
- recommended action source

Consumers read structured fields before prose.

Recovery routing uses `highest_severity` only together with `actionable_count`, and both values must be validator-derived from final finding dispositions. Pre-validation normalized severity cannot re-elevate a demoted finding.

## Latest And Active Task

`latest.json` and active-task may add compatible sidecar pointers and compact metrics. They do not embed full findings or rewrite producer status.

If the evidence sidecar is missing or unparseable, the derived reviewer verdict is Unknown in every mode. `legacy-observe` and `advisory` retain producer status for compatibility but cannot synthesize a compatibility Needs Fix, code-fix recommendation, or residual record without surviving validated findings.

## Repair Guide

Repair recommendations are generated only from surviving actionable findings. Each recommendation links:

- finding ID
- source anchor
- evidence sidecar
- owner step
- targeted command or manual action

Unknown produces an inspection/evidence action, not a code-fix instruction.

## Chapter 6 Route

Routing priorities:

1. deterministic failure
2. artifact integrity
3. approval state
4. validated P0/P1 actionable findings
5. validated medium/low findings
6. Unknown/timeout observation gap
7. clean

`record-residual` is legal only for a non-empty validated medium/low set.

## Needs-Fix-Fast

The narrow lane consumes normalized reviewer families and anchors.

- rerun only reviewers with surviving findings or relevant Unknown
- require current edits to hit the normalized anchors
- stop when the same family returns without new evidence
- do not pay for a round that cannot change the derived verdict

## Event Protocol

Add stable event families or details for:

- evidence parse started/completed
- finding validated/demoted/dropped/unknown
- verdict derived
- residual suppressed/created/updated
- replay comparison completed

High-frequency per-finding detail may live in the sidecar; `run-events.jsonl` records compact lifecycle transitions.

## Rollback

Rollback is configuration-first:

- return mode from require/warn to advisory or legacy-observe
- retain evidence generation for diagnosis
- do not delete sidecars needed to explain prior decisions
- restore legacy route only through the declared mode switch

No rollback requires changing `summary.json`.

## Tests

- legacy summary compatibility
- sidecar missing behavior by mode
- exact OK/Needs Fix/Unknown-to-agent-review verdict/action projection
- summary count and highest-actionable-final-severity consistency
- zero-actionable, Unknown, and residual behavior in every mode
- latest and active-task pointer projection
- repair guide actionable-only behavior
- Unknown inspection route
- residual legality and idempotency
- needs-fix-fast anchor hit behavior
- event lifecycle order
- config rollback

## Acceptance

- Existing producer summaries remain valid.
- Recovery consumers can resume with or without full raw Markdown.
- Unknown cannot be mistaken for clean.
- Repair guidance cannot be created from dropped findings.
- Every compatibility mode follows the same derived-verdict and empty-residual invariants.
- Unknown projects through the existing contract without becoming clean or an actionable product finding.
- Mode rollback is tested and leaves an auditable record.
