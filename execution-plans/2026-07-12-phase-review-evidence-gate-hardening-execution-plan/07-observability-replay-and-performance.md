# Observability, Replay, And Performance

## Purpose

Measure whether evidence gating reduces unsupported findings and workflow churn without hiding real defects or creating excessive review cost.

## Durable Metrics

Track by repository, chapter, task, reviewer, delivery profile, policy version, and schema version:

- proposed finding count
- validated, demoted, dropped, duplicate, and unknown counts
- exact-anchor completeness
- failure/consequence-chain completeness
- safeguard-gap completeness
- severity-rationale completeness
- raw-to-derived verdict changes
- OK/Needs Fix flip rate by task-reviewer pair
- repeated-family rate
- empty residual suppression count
- timeout and Unknown rates
- prompt/output sizes
- reviewer and validation duration
- rerun count and avoided-rerun reason
- retained evidence availability after cleanup

## Baseline Evidence

Known research baseline:

- Sanguo: 361 canonical Chapter 6 LLM runs, 463 Needs Fix outputs, 25.7% exact-line rate, 37.1% failure-condition signal, 0% explicit safeguard-gap proof, 41.1% task-reviewer OK/Needs Fix flip rate.
- NewRouge: 155 of 166 durable decisions recorded no captured low-priority finding while closure state was still created.
- LastKing: 95 of 106 durable decisions retained no concrete finding.

These are comparison baselines, not enforcement thresholds.

## Replay Corpus

Create sanitized, repository-owned fixtures representing:

- valid code finding
- under-evidenced high finding
- deterministic failure restatement
- host-safe security over-hardening
- missing input with Needs Fix text
- semantic obligation gap
- semantically equivalent wording false positive
- visual claim without screenshot
- empty residual state
- repeated same-family finding
- timeout with and without retained evidence

Each fixture records expected parse, disposition, derived verdict, and recovery route.

## Historical Replay

Replay is read-only and never rewrites historical business repositories.

- source outputs are copied only after sanitization and approval
- fixture provenance records repository, original path hash, date, reviewer, and redaction status
- unavailable NewRouge/LastKing raw outputs are represented by durable residual-state fixtures, not invented reviewer prose

## Promotion Measurements

Before warn/require promotion, review:

- false-drop sample adjudication
- true-defect retention sample
- raw-to-derived verdict deltas
- Unknown causes
- rerun and residual reduction
- parser failure rate
- validation latency
- prompt/output token growth

No numeric threshold becomes policy without ADR or profile decision ownership.

## Retention

Raw Markdown may follow existing cleanup policy. The following must outlive raw cleanup for the governed retention period:

- evidence summary
- aggregate metrics
- validated/demoted finding identities and anchors
- validator and policy versions
- derived verdict
- residual idempotency key
- source artifact hashes

Sensitive snippets may be minimized or redacted while preserving hashes and source anchors.

## Performance Budget

Measure separately:

- prompt-policy character growth
- structured-output character growth
- parse/validation CPU time
- filesystem anchor-check time
- replay suite duration
- total Chapter 6 wall time and rerun savings

The validator should remain deterministic and local. No extra LLM call is required for fact-gate enforcement.

## Dashboards And Reports

Initial output is a JSON summary plus compact Markdown under `logs/ci/<date>/review-evidence-metrics/`. Project health may later consume stable aggregate fields after schema acceptance.

## Tests

- metrics schema stability
- retention after raw-output deletion fixture
- redaction/hash reproducibility
- replay determinism
- performance smoke on representative large diff and multi-reviewer result set
- no network dependency

## Acceptance

- Baseline and post-change metrics are comparable.
- Raw cleanup does not erase the ability to explain a derived verdict.
- Replay is deterministic and repository-local.
- Validation adds no LLM round.
- Promotion decisions cite measured evidence and named adjudicators.
