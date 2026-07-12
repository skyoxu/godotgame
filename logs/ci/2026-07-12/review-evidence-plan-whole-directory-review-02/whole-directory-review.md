# Whole-Directory Review 02: Review Evidence Gate Hardening Plan

- Review date: 2026-07-12
- Scope: `execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/`
- Protocol: `96-global-review-and-split-validation.md`
- Package manifest SHA-256: `bd991379d17b2f19eb4a7c95eaf4055cdf1b86c40391102156d68f0a81aef353`
- Evidence policy: ECC-style fact gate; zero findings is legal
- Result meaning: implementation readiness only; no claim that implementation code is complete
- Verdict: **NOT READY FOR IMPLEMENTATION**
- Current findings: P0=0, P1=3, P2=2

## Deterministic Checks

| Check | Result |
| --- | --- |
| All Markdown books read | PASS, 14/14 |
| All files under `schemas/**` read | PASS, 2/2 |
| Markdown paths and heading anchors | PASS, 0 broken |
| JSON parsing | PASS |
| Draft 2020-12 schema meta-validation | PASS |
| Example validates against schema | PASS |
| Recovery-document validator | PASS |
| Active RGR rows | PASS, 34 unique rows |
| RGR owner coverage in book 99 | PASS, 34/34 exactly once |
| RGR explicit owner and acceptance link | PASS, 34/34 |
| Historical book-96 finding ledger | PASS, 5 rows and 0 historical Open rows |
| Historical closure evidence paths | PASS |
| Research source hash and line count | PASS, 815 lines |
| Research source range registry | PASS, 16 contiguous non-overlapping ranges |
| Research H2-H4 coverage | PASS, 77/77 headings exactly once |
| Book-99 source IDs | PASS, 16/16 exactly once |

## Current Finding Ledger

| Finding ID | Severity | Status | Owner | Expiry | Recheck trigger |
| --- | --- | --- | --- | --- | --- |
| RG-WDR-006 | P1 | Open | book 02 schema/severity owner | before schema v1 freeze | schema example or severity semantics change |
| RG-WDR-007 | P1 | Open | books 04/06 compatibility projection owners | before RG-1 implementation | agent-review verdict/action projection changes |
| RG-WDR-008 | P1 | Open | top-level completion owner with books 01/06 compatibility owners | before RG-HANDOFF exit | producer-status or global-completion semantics change |
| RG-WDR-009 | P2 | Open | book 02 schema owner | before RG-0 exit | identity-field schema changes |
| RG-WDR-010 | P2 | Open | books 02/99 coverage owners | before RG-0 exit | profile catalog or coverage-dimension changes |

## Findings

### RG-WDR-006 - P1 - The schema example normalizes P1 to medium before validation

**Exact evidence**

- `02-review-evidence-contracts-and-severity.md:69-74` defines P1/HIGH -> `high`.
- `02-review-evidence-contracts-and-severity.md:78-88` requires the full proof contract for critical/high findings and says missing proof causes deterministic demotion or drop.
- `schemas/review-evidence.v1.example.json:17-18` records `original_severity: P1` with `normalized_severity: medium`.
- The same example records `validation.state: demoted` and `validation.final_severity: medium` at lines 48-53, so normalized and final severity are indistinguishable.
- The frozen research source states that mapping occurs before proof thresholds at lines 194-202 and maps P1 -> high at lines 310-319.

**Failure mode**

An implementer follows the canonical example for a proposed P1 finding and stores `normalized_severity=medium` before validation. A validator selecting proof requirements from normalized severity applies the medium profile instead of the mandatory high profile. The finding can survive without the P1 proof contract, and later metrics cannot determine whether medium was the normalization result or the post-validation demotion result.

**Context inspected**

Book 02 severity mapping, elevated proof and compatibility sections; schema finding and validation fields; example; source research severity architecture.

**Why safeguards do not catch it**

The JSON Schema constrains both fields only to the severity enum. It does not enforce P1 -> high or distinguish pre-validation normalized severity from final severity, so the contradictory example validates successfully.

**Severity rationale**

P1 is justified because this can bypass the plan's mandatory elevated-severity proof gate and corrupt the audit trail for demotion, directly undermining the anti-hallucination control.

**Required correction**

Set the example's `normalized_severity` to `high` and retain `validation.final_severity=medium` for the demotion. Add a deterministic mutation test proving original P1 normalizes to high before proof evaluation.

### RG-WDR-007 - P1 - Unknown has no defined projection into the existing agent-review verdict/action vocabulary

**Exact evidence**

- `02-review-evidence-contracts-and-severity.md:141-146` requires projection into the current `agent-review.json` contract.
- `04-chapter6-review-ingestion-and-residual-closure.md:124-133` requires the agent-review builder to consume validated evidence and makes missing/unparseable evidence derive Unknown.
- `06-pipeline-integration-recovery-and-compatibility.md:71-83` requires Unknown to produce an inspection/evidence action rather than a code-fix instruction.
- The existing contract at `scripts/sc/_agent_review_contract.py:8-10` permits only verdicts `pass|needs-fix|block` and actions `none|resume|refresh|fork`.
- `docs/agents/07-agent-to-agent-review.md:31-40` gives each existing verdict a different operational meaning. There is no `unknown` verdict or `inspect` action.

**Failure mode**

A missing sidecar derives Unknown and must be projected into `agent-review.json`. Mapping it to `pass` treats Unknown as clean; mapping it to `needs-fix` tells the operator to repair findings that do not exist; mapping it to `block` invokes deterministic-artifact failure semantics. Adding `inspect` or `unknown` directly fails the existing contract. Different implementers can therefore produce incompatible recovery actions for the same evidence state.

**Context inspected**

Books 02, 04 and 06; current agent-review contract, policy and operator documentation; route priority and repair-guide rules.

**Why safeguards do not catch it**

The plan requests compatibility tests but supplies no normative mapping table. The existing contract validator rejects the vocabulary that the plan's prose naturally implies.

**Severity rationale**

P1 is justified because the missing mapping blocks a compatible implementation of a mandatory RG-1 output and can misroute operators into clean, repair, or blocking paths.

**Required correction**

Define an explicit derived-verdict-to-agent-review matrix using only the accepted contract vocabulary, including verdict, finding/category representation, recommended action, reason code, and repair-guide behavior for Unknown. If a new verdict/action is required, route it through a separately approved contract migration.

### RG-WDR-008 - P1 - Global completion contradicts compatibility-mode producer-status retention

**Exact evidence**

- The top-level plan states at lines 23-29 that it owns global completion.
- Its global completion rule at line 78 says `Needs Fix` cannot survive without an actionable finding.
- `01-authority-scope-and-invariants.md:43` narrows this rule to the derived reviewer verdict and compatibility projection, while allowing legacy producer status to be retained.
- `06-pipeline-integration-recovery-and-compatibility.md:40-47` retains producer status in every mode, including legacy-observe/advisory cases with zero actionable findings or Unknown evidence.

**Failure mode**

In advisory mode, a producer emits Needs Fix while validation yields zero actionable findings. Book 06 retains the producer status and produces derived OK. This satisfies the compatibility matrix but violates the top-level global completion rule, which does not distinguish producer status from derived or projected status. RG-5 completion can therefore pass or fail depending on which authority an implementer follows.

**Context inspected**

Top-level authority and global completion; Books 01, 02, 04 and 06; compatibility and rollback behavior.

**Why safeguards do not catch it**

The top-level file is explicitly the global-completion owner, while Book 06 is the sole compatibility owner. No precedence rule resolves contradictory statements owned by different layers.

**Severity rationale**

P1 is justified because the contradiction makes a mandatory phase-completion invariant non-deterministic and can force an incompatible `summary.json` change to satisfy the stricter reading.

**Required correction**

Change the top-level rule to state that a derived reviewer Needs Fix and compatibility projection cannot survive without actionable findings, while producer status may be retained only as declared compatibility data.

### RG-WDR-009 - P2 - Missing task/run identity has no canonical schema representation

**Exact evidence**

- `02-review-evidence-contracts-and-severity.md:10` says task/run identity is recorded only when available.
- `schemas/review-evidence.v1.schema.json:7-19` requires `task_id` and `run_id` for every Chapter 3-7 sidecar.
- The field definitions at schema lines 57-61 accept any string, including an empty string, but not null.
- The existing compatibility contract rejects empty task and run IDs at `scripts/sc/_agent_review_contract.py:108-111`.

**Failure mode**

A non-task-scoped Chapter 3/4/5/7 review has no task or run identity. Omitting/nulling the fields fails the evidence schema, while empty strings pass the evidence schema but can fail compatibility projection and collapse unrelated metrics or deduplication identities into the same empty key.

**Context inspected**

Shared finding contract, schema root requirements, Chapter 3-7 profiles, metrics dimensions, and existing agent-review identity validation.

**Why safeguards do not catch it**

Schema validation explicitly accepts the ambiguous empty-string representation and the plan does not define a synthetic scope identity or nullable/optional policy.

**Severity rationale**

P2 is justified because Chapter 6 task-scoped runs normally have both IDs; the defect primarily affects shared-schema attribution and non-task-scoped chapter integrations.

**Required correction**

Define one representation: require non-empty IDs and specify stable synthetic scope/run IDs, or make unavailable identity explicitly nullable/optional and prevent projection into consumers requiring non-empty IDs.

### RG-WDR-010 - P2 - Chapter 6 profile ownership summaries omit architecture and performance

**Exact evidence**

- `01-authority-scope-and-invariants.md:27` includes architecture and performance profiles.
- `04-chapter6-review-ingestion-and-residual-closure.md:72-78` defines both reviewer profiles.
- `02-review-evidence-contracts-and-severity.md:134-139` labels Book 04's Chapter 6 false-positive catalog only as code/security/test.
- `99-source-coverage.md:29` summarizes Chapter 6 coverage only as code/security/test/semantic.
- The source research requires Chapter 6 architecture and performance profiles at line 504.

**Failure mode**

An RG-0 ownership or coverage validator follows the Book 02/99 summaries and verifies no architecture/performance catalog dimension. The implementation can omit domain-specific false-positive ownership or coverage assertions while still satisfying the summarized coverage tables.

**Context inspected**

Books 01, 02, 04, 97, 98 and 99; source range SRC-009; schema review-domain enum.

**Why safeguards do not catch it**

Book 98's byte-range registry proves source inclusion but does not make the Book 02/99 semantic summaries enumerate every profile. RGR-034 covers architecture domain distinction, not both profile catalog ownership entries.

**Severity rationale**

P2 is justified because the actual profiles and source range exist; the gap is cross-document ownership and coverage traceability rather than total requirement loss.

**Required correction**

Update Book 02 catalog ownership and Book 99 Chapter 6 coverage dimension to enumerate code, security, test, semantic, architecture, and performance consistently.

## Historical Ledger Check

Book 96 contained five historical findings, all `Closed`, with an existing closure-evidence path. It contained zero historical `Open` rows at the reviewed package hash. The five findings in this report are new findings against that later package state and are intentionally not represented as pre-existing historical rows.

## 97 Owner And Acceptance Check

All 34 active RGR rows have explicit status, owner book, RG phase, owner-book acceptance link, and separate test/evidence intent. All linked paths and heading anchors resolve.

## 98/99 Coverage Check

The original frozen research source matches its declared SHA-256 and 815-line count. Sixteen contiguous, non-overlapping `SRC-*` ranges cover lines 1-815, all 77 H2-H4 headings occur in exactly one range, and Book 99 contains all 16 IDs exactly once. Mechanical source coverage passes. RG-WDR-010 records a narrower semantic-summary inconsistency; it does not invalidate the byte/range coverage result.

## Final Verdict

The plan is **not ready to implement** while RG-WDR-006, RG-WDR-007, and RG-WDR-008 remain Open. RG-WDR-009 and RG-WDR-010 require owner, expiry, and recheck as recorded above. A future PASS means only that the plan can be implemented; it does not mean implementation code is complete.
