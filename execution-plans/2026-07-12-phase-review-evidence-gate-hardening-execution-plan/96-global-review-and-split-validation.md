# Global Review And Split Validation

## Purpose

Prevent missing books, broken links, duplicate authority, uncovered requirements, schema drift, and top-level plan re-expansion.

## Planning-Time Validation

Before implementation:

```powershell
py -3 scripts/python/validate_recovery_docs.py --dir execution-plans
```

RG-0 adds a focused deterministic validator for this split package and schema.

## Required RG-0 Validator

The validator must check:

- exact required book set from `00-index.md`
- top-level recovery metadata and relative links
- required headings by book
- top-level file remains an index rather than detailed normative authority
- one owner book per requirement family
- every active `RGR-*` ledger entry maps to one owner book, one phase, acceptance, and test intent
- the research source hash and line count match book 98, its source ranges are contiguous and non-overlapping, and every H2-H4 heading belongs to exactly one range
- `99-source-coverage.md` covers every owner book and active ledger row
- schema and example validation
- severity and compatibility mapping uniqueness
- original-to-normalized severity mapping occurs before proof evaluation and remains distinct from final severity
- summary counts and highest severity are derived from final dispositions; zero actionable uses none and a demoted P1 cannot remain summary high
- task/run identity is non-empty, with the synthetic non-task scope form declared and tested
- every derived verdict has exactly one projection into the existing agent-review verdict/action vocabulary for each applicable mode
- no orphan or superseded requirement remains active without status mapping
- no phase exit depends on a validator, fixture, or evidence producer assigned only to a later phase
- the compatibility matrix has one outcome per mode for missing sidecar, zero actionable findings, Unknown, route source, and residual legality
- every historical review finding has a stable status; Open P2 has owner, expiry, and recheck, while Closed findings have closure evidence

Mutation fixtures deliberately:

- remove a book
- break a link
- duplicate one authority family
- remove a ledger mapping
- add a second severity mapping
- normalize P1/HIGH to medium before validation
- allow an empty task or run identity
- remove or change the Unknown-to-agent-review projection
- summarize a demoted P1 as high
- summarize zero actionable findings with a severity other than none
- delete a mandatory schema field
- allow P0/P1 without proof
- allow Needs Fix with zero actionable findings
- map Unknown to OK
- reintroduce empty residual creation
- move a deterministic Chapter 3/4/7 decision to LLM authority

Every mutation fails with a stable rule ID.

## Authority Families

| Requirement family | Owner book |
| --- | --- |
| authority, scope, invariants | 01 |
| schema, anchors, states, severity, verdict | 02 |
| Chapter 3-5 profiles | 03 |
| Chapter 6 ingestion and residual closure | 04 |
| Chapter 7 UI evidence | 05 |
| pipeline, recovery, compatibility, rollback | 06 |
| metrics, replay, retention, performance | 07 |
| phases and task sizing | 08 |
| risks, DoD, glossary, stop conditions | 09 |
| global review and validation | 96 |
| post-split requirements | 97 |
| research mapping | 98 |
| source coverage | 99 |

## Global Review Inputs

- top-level plan and all books
- schema and example
- research report
- ECC fixed-commit source refs
- ADR-0005 and ADR-0017
- Chapter 3-7 workflow and policy docs
- implementation diff, tests, and evidence for phase exit
- replay and metrics summaries after RG-2
- requirement ledger, research audit, and source coverage

## Review Method

1. Verify predecessor phase exit.
2. Run recovery, split, schema, and link validators.
3. Verify authority uniqueness and Chapter 3-7 deterministic boundaries.
4. Review P0/P1/P2 findings against implementation and evidence, not plan prose.
5. Replay valid and false-positive fixtures.
6. Verify raw/derived verdict and residual behavior.
7. Verify compatibility and rollback.
8. Verify durable rules migrated to ADR/workflow/docs.
9. Record immutable review result under `logs/**`.

## Historical Whole-Directory Finding Ledger

This table is the canonical status index for Whole-directory findings against this split package. Immutable review and closure evidence remains under `logs/**`. Finding IDs are never reused or deleted.

Allowed status values are `Open`, `Closed`, and `Superseded`.

| Finding ID | Severity | Status | Owner | Expiry | Recheck trigger | Closure evidence |
| --- | --- | --- | --- | --- | --- | --- |
| RG-WDR-001 | P1 | Closed | book 08 phase owner with books 04/96 validator owners | n/a | phase matrix or validator ownership changes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review/remediation-validation.md` |
| RG-WDR-002 | P1 | Closed | book 06 compatibility owner with book 04 residual owner | n/a | compatibility or residual semantics change | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review/remediation-validation.md` |
| RG-WDR-003 | P1 | Closed | book 02 schema owner with books 01/04/98/99 owners | n/a | schema domain or source coverage changes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review/remediation-validation.md` |
| RG-WDR-004 | P2 | Closed | book 96 global-review owner | n/a | a Whole-directory review completes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review/remediation-validation.md` |
| RG-WDR-005 | P2 | Closed | book 97 ledger owner | n/a | requirement ledger changes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review/remediation-validation.md` |
| RG-WDR-006 | P1 | Closed | book 02 schema/severity owner | n/a | schema example or severity semantics change | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-02/remediation-validation.md` |
| RG-WDR-007 | P1 | Closed | books 04/06 compatibility projection owners | n/a | agent-review verdict/action projection changes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-02/remediation-validation.md` |
| RG-WDR-008 | P1 | Closed | top-level completion owner with books 01/06 compatibility owners | n/a | producer-status or global-completion semantics change | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-02/remediation-validation.md` |
| RG-WDR-009 | P2 | Closed | book 02 schema owner | n/a | identity-field schema changes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-02/remediation-validation.md` |
| RG-WDR-010 | P2 | Closed | books 02/99 coverage owners | n/a | profile catalog or coverage-dimension changes | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-02/remediation-validation.md` |
| RG-WDR-011 | P1 | Closed | books 02/04/06 schema and recovery-summary owners | n/a | summary severity semantics or routing fields change | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-03/remediation-validation.md` |
| RG-WDR-012 | P2 | Closed | RG-0 focused-validator owner | n/a | focused-validator responsibilities or line count changes | `logs/ci/2026-07-12/review-evidence-rg0-exit-review/remediation-validation.md` |
| RG-WDR-013 | P1 | Closed | book 02 verdict-contract owner | n/a | raw/derived verdict rules change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-014 | P1 | Closed | book 02 disposition owner | n/a | proof demotion/drop semantics change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-015 | P1 | Closed | book 02 anchor owner | n/a | anchor-type or elevated-proof rules change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-016 | P1 | Closed | book 02 summary owner | n/a | actionable-state or final-severity rules change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-017 | P1 | Closed | book 96 schema-mutation owner | n/a | canonical required fields change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-018 | P1 | Closed | books 08/96 phase-exit owners | n/a | phase status or unlocked scope changes | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-019 | P2 | Closed | book 02 fallback-contract owner | n/a | identity or policy field types change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-020 | P2 | Closed | book 02 reason-code owner | n/a | reason-code family catalog changes | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-021 | P2 | Closed | books 02/04 domain owners | n/a | chapter/domain mapping changes | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-022 | P2 | Closed | book 96 focused-validator owner | n/a | required-book or profile-config parsing changes | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-023 | P2 | Closed | books 00/02/96 schema-authority owners | n/a | plan-local schema pointer fields change | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/remediation-validation.md` |
| RG-WDR-024 | P2 | Closed | book 96 schema-freeze owner | n/a | canonical nested definitions change | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-025 | P1 | Closed | books 02/96 conditional-contract owners | n/a | canonical conditional rules or schema version change | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-026 | P2 | Closed | RG-0 schema-loader and focused-validator owners | n/a | schema parsing, meta-validation, or malformed control inputs change | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-027 | P2 | Closed | book 02 fallback-contract owner | n/a | payload field types or malformed scalar handling changes | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-028 | P2 | Closed | book 02 canonical/fallback parity owner | n/a | integer, line, chapter, or identity representation changes | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-029 | P1 | Closed | books 06/ADR compatibility owners | n/a | derived OK projection or recovery action changes | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-030 | P2 | Closed | book 02 disposition owner | n/a | reason-code or disposition-state rules change | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-031 | P2 | Closed | book 97 ledger owner | n/a | requirement status or transition registry changes | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |
| RG-WDR-032 | P2 | Closed | books 98/99 source-audit owners | n/a | frozen source or control-document reading changes | `logs/ci/2026-07-13/review-evidence-rg0-final-clean-review/remediation-validation.md` |

## Phase Exit Evidence Registry

| Phase | Status | Decision authority | Validation evidence | Scope unlocked |
| --- | --- | --- | --- | --- |
| RG-HANDOFF | Closed | user authorization and handoff decision log | `logs/ci/2026-07-12/review-evidence-plan-whole-directory-review-03/` | RG-0 policy and contract freeze |
| RG-0 | Closed | ADR-0032 and RG-0 exit review | `logs/ci/2026-07-12/review-evidence-rg0-refactor-review/` | RG-1 task creation only; RG-1 implementation remains unstarted |

## Acceptance

- Required-book, link, ledger, audit, coverage, and schema mutations fail.
- Global review has zero unresolved P0/P1.
- P2 requires owner, expiry, and recheck.
- No implementation phase exits solely from LLM prose.
- Top-level plan cannot silently become the detailed policy owner.
