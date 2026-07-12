# Chapter 6 Review Ingestion And Residual Closure

## Purpose

Correct the highest-cost trust boundary: conversion of raw LLM reviewer prose into Chapter 6 verdict, recovery, rerun, and residual state.

## Current Failure Chain

```text
external or default agent prompt
  -> Markdown output
  -> regex terminal Verdict only
  -> generic fixed-medium finding per non-OK reviewer
  -> agent-review Needs Fix
  -> route/rerun/residual decisions
  -> empty or repeated durable closure records
```

The implementation must preserve individual findings before verdict aggregation.

## Target Flow

```text
external agent prompt
  + repository evidence policy
  + reviewer-specific profile
  -> Markdown plus structured evidence block
  -> parse candidate findings
  -> deterministic validation and normalization
  -> evidence sidecar
  -> derived reviewer verdict
  -> compatible LLM summary
  -> compatible agent-review projection
  -> route/rerun/residual consumers
```

## Repository-Owned Prompt Policy

The policy is appended after external prompt content and includes:

1. exact anchor requirement
2. concrete failure mode or consequence chain
3. surrounding context requirement
4. severity defense
5. P0/P1 proof contract
6. zero-findings legitimacy
7. Unknown for missing input
8. false-positive catalog
9. one terminal structured evidence block
10. one terminal raw verdict retained for diagnostics only

Prompt regression tests assert that lower-precedence prompt content cannot remove these rules.

## Reviewer Profiles

### Code Reviewer

Requires code line/snippet, input-state-result, callers/tests/context, safeguard gap, and severity rationale.

### Security Auditor

Requires applicable threat model, trust boundary, attacker capability, reachable impact, existing security control gap, and security-profile alignment.

### Test Reviewer

Requires acceptance/test anchor, production behavior allegedly unproven, assertion gap, and why existing deterministic test-quality checks do not already decide it.

### Semantic Reviewer

Requires task/source obligation, acceptance representation, missing/distorted behavior, downstream consequence, and minimal delta.

### Architecture Reviewer

Requires an accepted ADR, declared architecture invariant, concrete dependency/call path, affected runtime or maintenance boundary, and a reachable consequence. General preference or hypothetical future scale is not a finding. The canonical review domain is `architecture`, not Chapter 4 `architecture-document`.

### Performance Reviewer

Requires measurable hot-path/capacity evidence, representative input or load, observed or budgeted threshold, affected runtime path, and an existing performance-control gap. Hypothetical scale without measurements is not a finding.

## Chapter 6 False-Positive Catalog

Adopt ECC's catalog and add:

- host-safe anti-tamper hardening without task requirement
- browser/web threats applied to offline single-player code without a boundary
- rough but stable UI intentionally deferred to Chapter 7
- deterministic gate failure restated as an LLM discovery
- missing acceptance input converted into a code defect
- suggestion-only best practice without reachable bad result
- same normalized finding family repeated without a new anchor
- old absolute path or unavailable artifact
- code outside changed/task scope unless critical and directly reachable
- generated fixture/example hardcoding treated as production secret or configurability defect
- framework or caller behavior ignored despite visible context

## Parser And Validator

The parser extracts the structured evidence block and retains raw output. The validator:

- resolves paths against repository root only
- rejects absolute or external paths as canonical evidence
- validates lines, headings, fields, quotes, and snippets
- validates proof requirements by severity/profile
- validates changed-scope/task relevance
- normalizes severity and finding family
- deduplicates within and across the current run
- records all dispositions and reason codes
- derives the reviewer verdict
- derives summary counts and highest severity from final dispositions, never from pre-validation normalized severity

## LLM Summary Integration

Each reviewer result adds compatible details:

- raw verdict
- derived verdict
- evidence sidecar path
- proposed/validated/demoted/dropped/unknown counts
- highest actionable final severity from surviving validated/demoted findings
- validator version
- prompt-policy version

Existing fields remain readable by older consumers during the compatibility phase.

## Agent Review Projection

`agent_to_agent_review.py` consumes validated evidence when present.

- one compatibility finding per surviving actionable finding, not one generic finding per reviewer
- evidence path points to the evidence sidecar and source anchor
- message and suggested fix come from validated fields
- severity maps through book 02
- raw non-OK with zero surviving findings cannot create Needs Fix
- missing or unparseable evidence sidecar always derives Unknown; producer-status retention and recovery routing follow the authoritative compatibility matrix in book 06, never a silent generic medium finding

## Residual Closure Correctness

Residual recording requires:

- non-empty validated low-priority finding list
- stable finding-family fingerprint
- task/run/reviewer identity
- source anchor and actionable message
- idempotency key

If the list is empty:

- no decision log
- no execution plan
- no `record-residual` recommendation
- route explains `no_actionable_residual_findings`

Repeated same-family records update or link the existing durable record instead of creating numbered duplicates.

## Unknown And Timeout

- timeout without usable evidence: Unknown
- timeout with a complete retained structured result: validate normally and record timeout separately
- malformed structured block: Unknown
- missing controlling input: Unknown
- Unknown never counts as clean and never becomes an actionable finding by itself

## Likely Implementation Areas

- `scripts/sc/_llm_review_prompting.py`
- `scripts/sc/_llm_review_engine.py`
- new small review-evidence parser/validator modules under `scripts/sc/`
- `scripts/sc/agent_to_agent_review.py`
- `scripts/sc/_agent_review_contract.py` only for compatible projection helpers, not a breaking schema change
- `scripts/python/chapter6_route.py`
- `scripts/sc/llm_review_needs_fix_fast.py`
- repair/recovery/technical-debt helpers and focused tests

No edited Python module may exceed the local 400-line guardrail without an approved split plan.

## Tests

- ECC prompt-policy regression
- exact line and quote validation
- P0/P1 missing-proof demotion/drop mutations
- demoted P1 summary-highest mutation: high fails, medium passes
- zero-actionable summary mutation: any value other than `none` fails
- raw Needs Fix plus zero surviving findings -> OK
- malformed output -> Unknown
- timeout result matrix
- deterministic-restatement false positive
- host-safe security false positive
- generic-finding compatibility migration
- empty residual suppression
- same-family residual idempotency
- replay fixtures from Sanguo
- empty residual fixtures from NewRouge and LastKing

## Acceptance

- Every Chapter 6 Needs Fix exposes at least one validated finding.
- Generic fixed-medium reviewer findings are removed from the validated path.
- P0/P1 proof is machine-complete and source-anchor-valid.
- Zero-findings review is a valid pass.
- Unknown remains visible in summary, agent review, repair guide, latest, and active-task.
- Empty residual artifacts cannot be generated.
- Replaying the same finding family cannot create another numbered durable record.
