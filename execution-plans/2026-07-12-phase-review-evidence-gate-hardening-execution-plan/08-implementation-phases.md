# Implementation Phases

## Mandatory Sequential Dependency Matrix

| Phase | Immediate predecessor |
| --- | --- |
| RG-HANDOFF | completed research and split-plan validation |
| RG-0 | RG-HANDOFF |
| RG-1 | RG-0 |
| RG-2 | RG-1 |
| RG-3 | RG-2 |
| RG-4 | RG-3 |
| RG-5 | RG-4 |

Only one phase may be active. Missing predecessor evidence keeps the next phase paused.

## Phase RG-HANDOFF: Research And Plan Freeze

Deliver:

- fixed ECC commit and source links
- local harness architecture analysis
- NewRouge, LastKing, and Sanguo evidence baseline with limitations
- split plan, ledger, audit, coverage, and schema drafts
- existing execution-plan validation result

Exit:

- research workflow complete
- every split book exists and is linked
- no unresolved plan P0/P1
- implementation remains unstarted

## Phase RG-0: Policy, ADR, Schema, And Ownership Freeze

Deliver:

- accepted ADR or ADR-0005 addendum
- implementation owner, reviewer, and rollback owner
- frozen review-evidence schema v1
- reason-code catalog
- severity and compatibility mapping
- explicit distinction between original, pre-validation normalized, and post-validation final severity
- evidence mode semantics: legacy-observe, advisory, warn, require
- exact derived-verdict-to-agent-review verdict/action projection, including Unknown
- non-empty task/run identity and synthetic non-task scope identity semantics
- retention/redaction policy
- exact code ownership and script-split plan
- focused split/coverage/schema validator and mutation fixtures
- phase-sequence validator that rejects an exit when its required implementation or evidence belongs only to a later phase
- schema-level P0/P1 proof-presence and verdict-consistency validation
- summary count and highest-actionable-final-severity consistency validation

Exit:

- schema example validates
- mutation fixtures fail missing proof, duplicate authority, broken coverage, and invalid compatibility mapping
- mutation fixtures reject P1 normalized to medium before validation, empty identity fields, and an Unknown projection outside the existing agent-review vocabulary
- mutation fixtures reject a demoted P1 summarized as high and zero actionable findings summarized above none
- mutation fixtures fail a later-phase validator dependency used by an earlier exit
- no edited implementation script is projected beyond the 400-line guardrail without an approved module split
- RG-1 task may be created

## Phase RG-1: Chapter 6 Capture And Residual Correctness

Deliver:

- repository-owned prompt policy
- reviewer-specific structured evidence output
- parser and sidecar writer
- minimum runtime evidence validator for repository path, line/heading bounds, quote/snippet agreement, required proof, disposition, and verdict derivation
- derived verdict
- LLM summary fields
- agent-review compatibility projection
- empty-residual suppression
- residual idempotency
- Unknown/timeout projection

Exit:

- Needs Fix always has a surviving actionable finding
- P0/P1 proof mutation tests pass
- zero findings derives OK
- malformed output derives Unknown
- empty residual fixtures create no decision or plan
- same-family replay creates one durable record

## Phase RG-2: Expanded Validation, Replay, And Advisory Metrics

Deliver:

- expanded scope, duplicate-family, cross-run, false-positive, and chapter-profile validation beyond the RG-1 minimum validator
- sanitized replay corpus
- evidence metrics schema and reports
- retention-after-cleanup tests
- advisory comparison between raw and derived verdicts
- performance smoke

Exit:

- replay is deterministic
- known Sanguo/NewRouge/LastKing fixtures produce expected dispositions
- no extra LLM call is introduced
- no unresolved validator P0/P1
- live behavior remains advisory

## Phase RG-3: Chapter 5 Semantic Evidence

Deliver:

- obligation/acceptance structured finding profile
- missing-input Unknown behavior
- pre-rewrite evidence preservation
- deterministic-restatement and invented-obligation filters
- repeated-family stop-loss integration

Exit:

- semantic rewrite requires a validated finding
- missing input cannot produce Needs Fix
- equivalent wording fixtures do not trigger rewrite
- failure-family and rewrite-idempotency tests pass

## Phase RG-4: Chapter 3, 4, And 7 Profiles

Deliver:

- Chapter 3 task-planning evidence profile
- Chapter 4 overlay/contract document profile
- Chapter 7 UI/screenshot/accessibility/localization profile
- chapter-specific false-positive fixtures
- status patch and duplicate-task review integration

Exit:

- deterministic validators remain authoritative
- no broad code-review gate is added to Chapter 3, 4, or 7
- visual Needs Fix requires inspectable evidence
- duplicate task and scope-creep fixtures are rejected

## Phase RG-5: Profile Promotion And Durable Closure

Deliver:

- advisory trial report
- adjudicated false-drop and retained-defect samples
- accepted profile promotion decision
- warn/require configuration for selected profiles only
- rollback drill
- updated workflow, agent, testing, delivery-profile, ADR, and recovery docs
- closed requirements ledger and source coverage

Exit:

- promotion decision cites measurements and owners
- rollback to advisory is tested
- no unresolved P0/P1
- P2 is zero or has owner, expiry, and recheck trigger
- durable rules no longer depend on execution-plan prose

## Task Sizing

One task handles one schema/validator family, one reviewer profile, one compatibility projection, one residual-routing correction, one replay/metrics family, or one chapter integration.

Do not combine prompt policy, parser, Chapter 5 semantics, Chapter 7 UI, and recovery migration into one task.

Every task records:

- RG phase and requirement IDs
- owner, reviewer, and rollback owner
- allowed files and protected schemas
- accepted ADR refs
- red test and target test set
- expected evidence path
- compatibility mode
- rollback action
- stop-loss and exception expiry
