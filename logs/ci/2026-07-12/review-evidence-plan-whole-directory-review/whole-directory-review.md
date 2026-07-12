# Whole-Directory Review: Review Evidence Gate Hardening Plan

- Review date: 2026-07-12
- Review scope: `execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/`
- Protocol: `96-global-review-and-split-validation.md`
- Evidence policy: ECC-style fact gate; zero findings is legal
- Result meaning: readiness to implement only; no claim that implementation is complete
- Verdict: **NOT READY FOR IMPLEMENTATION**
- Open findings: P0=0, P1=3, P2=2

## Deterministic Checks

| Check | Result |
| --- | --- |
| All 14 Markdown books read | PASS |
| Both files under `schemas/**` read | PASS |
| Markdown relative links resolve | PASS, 0 broken links |
| JSON files parse | PASS |
| Draft 2020-12 schema is valid | PASS |
| Example validates against schema | PASS |
| Required book set | PASS |
| 97 requirement IDs | PASS, 33 rows and 33 unique IDs |
| 99 owner coverage of active RGR IDs | PASS, 33 IDs covered exactly once |
| 97 explicit acceptance references | FAIL, 0 of 33 rows |
| Historical Whole-directory finding ledger discoverable from 96 | FAIL, none existed before this review |
| Research section coverage mechanically provable | FAIL, 77 H2-H4 source headings map only to 15 broad families |

## Finding Ledger

| Finding ID | Severity | Status | Owner | Closure deadline / recheck |
| --- | --- | --- | --- | --- |
| RG-WDR-001 | P1 | Open | Book 08 phase owner with Books 04/96 validator owners | Before RG-HANDOFF exit; recheck phase matrix and mutation tests |
| RG-WDR-002 | P1 | Open | Book 06 compatibility owner with Book 04 residual owner | Before RG-0 exit; recheck one complete mode matrix |
| RG-WDR-003 | P1 | Open | Book 02 schema owner with Books 01/04/98/99 owners | Before schema v1 freeze; recheck schema and source-section coverage |
| RG-WDR-004 | P2 | Open | Book 96 global-review owner | Before RG-0 approval; recheck linked historical ledger and statuses |
| RG-WDR-005 | P2 | Open | Book 97 ledger owner | Before RG-0 exit; recheck every RGR row against an explicit acceptance anchor |

## Findings

### RG-WDR-001 - P1 - Validator work is assigned after gates that require it

**Exact evidence**

- `04-chapter6-review-ingestion-and-residual-closure.md:173-176` requires exact-line/quote validation, P0/P1 proof mutations, and zero-survivor verdict behavior in the Chapter 6 test set.
- `04-chapter6-review-ingestion-and-residual-closure.md:187-195` requires machine-complete, source-anchor-valid P0/P1 proof at Chapter 6 acceptance.
- `08-implementation-phases.md:55-76` makes those conditions RG-1 exit requirements.
- `08-implementation-phases.md:78-94` assigns anchor, quote, and proof validation to RG-2, which cannot start before RG-1 exits under `08:7-15`.
- `97-post-split-requirements-ledger.md:44` assigns the phase-validator test itself to RG-5.

**Failure mode**

An implementer follows the mandatory sequence, reaches RG-1 exit, and must prove that P0/P1 evidence is source-anchor-valid. The phase matrix assigns the validator that checks anchors, quotes, and proof to RG-2, while RG-2 is blocked until RG-1 exits. Following Book 04 instead moves validator work into RG-1 and contradicts Book 08 task/phase ownership.

**Context inspected**

Books 02, 04, 08, 09, 96, and 97; the top-level Gate Summary; ADR-0005's single-entry and artifact rules.

**Why safeguards do not catch it**

The generic recovery-doc validator cannot decide phase ownership. The planned focused validator is itself part of the disputed schedule, and the RG-5 phase-validator test is too late to protect earlier exits.

**Severity rationale**

P1 is justified because the plan has no single executable ownership boundary for a mandatory RG-1 exit condition. The defect blocks trustworthy phase exit but does not itself cause production data loss or a security incident.

**Required correction**

Define a minimum validator delivered no later than RG-1 for schema shape, anchor/quote validity, P0/P1 proof completeness, disposition, and verdict derivation. Reserve RG-2 for replay, expanded false-positive rules, metrics, retention, and performance. Move the phase-sequence validator to RG-0 or RG-HANDOFF.

### RG-WDR-002 - P1 - Advisory compatibility has contradictory verdict and residual semantics

**Exact evidence**

- `04-chapter6-review-ingestion-and-residual-closure.md:128-129` says raw non-OK with zero survivors cannot create Needs Fix and a missing sidecar is advisory Unknown.
- `04-chapter6-review-ingestion-and-residual-closure.md:141-146` unconditionally suppresses decisions, plans, and `record-residual` for an empty validated list.
- `06-pipeline-integration-recovery-and-compatibility.md:42-45` says advisory keeps legacy routing, while only warn explicitly blocks empty residual creation.
- `06-pipeline-integration-recovery-and-compatibility.md:69-72` says a missing sidecar in advisory retains legacy behavior, not Unknown.
- `01-authority-scope-and-invariants.md:43-53` makes zero-survivor OK, missing-input Unknown, and empty-residual suppression global invariants.

**Failure mode**

With `mode=advisory`, a reviewer returns raw `Needs Fix` but the evidence sidecar is missing or validates to zero actionable findings. Book 04 routes this to Unknown or OK and suppresses residuals. Book 06 preserves legacy routing, which can retain Needs Fix and create the residual work the plan is intended to eliminate.

**Context inspected**

Books 01, 02, 04, 06, 08, and 09; schema mode enum; current Chapter 6 recovery and residual workflow sources.

**Why safeguards do not catch it**

Book 06 is the declared compatibility owner, but Book 04 and the global invariants state stronger contradictory behavior. No complete mode-by-condition matrix defines which rule wins.

**Severity rationale**

P1 is justified because two compliant implementations can produce opposite durable recovery state for the same input, reopening the exact rerun and empty-residual failure this plan must close.

**Required correction**

Add one authoritative matrix for every mode covering missing sidecar, parse failure, raw Needs Fix with zero actionable findings, Unknown, route action, and residual creation. Preserve legacy producer status if required, but keep empty-residual suppression invariant in every mode.

### RG-WDR-003 - P1 - Source coverage claims miss a declared Chapter 6 architecture profile

**Exact evidence**

- The source research report at `technical-ecc-review-anti-hallucination-research-2026-07-12.md:504` requires code, semantic, security, architecture, performance, and test-specific Chapter 6 profiles; line 694 repeats architecture as a Chapter 6 reviewer domain.
- `04-chapter6-review-ingestion-and-residual-closure.md:72-74` retains an Architecture/Performance Reviewer.
- `schemas/review-evidence.v1.schema.json:40-50` has `performance` but no `architecture` review domain.
- `01-authority-scope-and-invariants.md:23-30` lists `architecture-document`, which is the Chapter 4 document profile, but does not list the Chapter 6 architecture profile.
- `98-research-to-split-audit.md:21-37` maps only broad content families without stable source section IDs or anchors, then claims complete mapping at line 59.
- `99-source-coverage.md:75-82` repeats the complete-coverage assertion without enumerating source sections.

**Failure mode**

A Chapter 6 architecture reviewer produces a finding about code/system architecture. The v1 schema cannot label it `architecture`; the producer must fail schema validation or misclassify it as `architecture-document`, `code`, or `performance`. The broad 98/99 mapping can still report full coverage, so the omitted source requirement is not detected.

**Context inspected**

Source research architecture, Chapter 6, and decision-matrix sections; Books 01, 02, 04, 96, 98, and 99; schema and example.

**Why safeguards do not catch it**

`additionalProperties: false` and the enum make the representational gap hard. The planned coverage check has no source-section registry against which it can detect the omission.

**Severity rationale**

P1 is justified because the schema freeze would otherwise omit a mandatory reviewer profile and 98/99 would falsely certify complete source coverage.

**Required correction**

Add an explicit Chapter 6 `architecture` domain or a normative, tested mapping that is distinct from Chapter 4 `architecture-document`. Give each normative research section a stable source ID/anchor in Book 98 and require Book 99 to cover every such ID exactly once.

### RG-WDR-004 - P2 - No historical Whole-directory finding ledger existed

**Exact evidence**

- `96-global-review-and-split-validation.md:79-89` requires findings to be reviewed and an immutable result to be recorded.
- `96-global-review-and-split-validation.md:91-95` requires zero unresolved P0/P1 and owner/expiry/recheck for P2.
- No stable Whole-directory finding ID, status, owner, expiry, or closure evidence was present in Book 96 or discoverable under `logs/**` for this plan before this review.
- `97-post-split-requirements-ledger.md:49-54` is an RGR requirement-status registry, not a review-finding history.

**Failure mode**

A later reviewer cannot determine whether an earlier finding remains Open, was Closed with evidence, or was Superseded. The zero-open acceptance claim becomes a fresh prose assertion on every review.

**Context inspected**

Books 96 and 97, the plan directory, and existing `logs/**` references for this plan.

**Why safeguards do not catch it**

Immutable log placement is specified, but no canonical ledger path or linkage rule exists. The RGR registry tracks implementation requirements, not review findings.

**Severity rationale**

P2 is justified because this is the first discoverable Whole-directory review and this artifact now starts a stable ledger. The control still must be linked before the next review.

**Required correction**

Link a canonical historical finding ledger from Book 96, preserving stable finding ID, severity, status, exact anchors, owner, closure evidence, expiry, and recheck trigger.

### RG-WDR-005 - P2 - All 33 RGR rows have owners but none has an explicit acceptance reference

**Exact evidence**

- `96-global-review-and-split-validation.md:25-28` requires each active RGR row to map to one owner book, one phase, acceptance, and test intent.
- `97-post-split-requirements-ledger.md:13-47` contains 33 unique rows. Every row has an owner book and phase.
- The combined `Acceptance and test intent` cells contain test phrases such as `precedence regression test` and `coverage validator`, but 0 of 33 contains an acceptance section link, acceptance ID, heading anchor, or other explicit acceptance reference.
- `97-post-split-requirements-ledger.md:72-76` asserts that acceptance and test intent are present.

**Failure mode**

The focused validator can confirm that a cell is non-empty but cannot prove which owner-book acceptance criterion closes the requirement. A row can pass while its owning acceptance section omits or contradicts the requirement.

**Context inspected**

All 33 RGR rows, owner-book Acceptance sections, Books 96 and 99.

**Why safeguards do not catch it**

Owner book numbers and free-text test intent are not acceptance anchors. Book 99 covers IDs by owner only, so it cannot validate closure criteria.

**Severity rationale**

P2 is justified because ownership and phase assignment are complete and the owner books contain acceptance sections; the gap is deterministic traceability rather than a missing requirement family.

**Required correction**

Split the last column into `Acceptance reference` and `Test/evidence intent`, using a stable heading anchor or acceptance ID for every row.

## Historical Ledger Check

No historical Whole-directory ledger existed before this run, so there were no prior Open items that could be truthfully enumerated. This report is the initial immutable ledger. All five findings above are Open.

## Coverage Conclusion

Books 98 and 99 cover all 33 current RGR IDs by owner, but they do not yet prove complete coverage of the original research/monolithic recommendation set. The missing Chapter 6 architecture domain is a concrete uncovered requirement, and the broad category mapping cannot detect comparable omissions.

## Final Verdict

The plan is **not ready to implement** while RG-WDR-001, RG-WDR-002, and RG-WDR-003 remain Open. Closing them and re-running this same review may establish implementation readiness. Even a future PASS means only that the plan can be implemented; it does not mean the code is complete.
