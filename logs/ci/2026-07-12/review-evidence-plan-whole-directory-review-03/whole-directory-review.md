# Whole-Directory Review 03: Review Evidence Gate Hardening Plan

- Review date: 2026-07-12
- Scope: `execution-plans/2026-07-12-phase-review-evidence-gate-hardening-execution-plan/`
- Protocol: `96-global-review-and-split-validation.md`
- Package manifest SHA-256: `061a4844924b980c06b6e4582473154d141dd0513eb2fd1d49f911477d05713b`
- Evidence policy: ECC-style fact gate; zero findings is legal
- Result meaning: implementation readiness only; no claim that implementation code is complete
- Verdict: **NOT READY FOR IMPLEMENTATION**
- Current findings: P0=0, P1=1, P2=0

## Deterministic Checks

| Check | Result |
| --- | --- |
| All Markdown books read | PASS, 14/14 |
| All files under `schemas/**` read | PASS, 2/2 |
| Markdown paths and heading anchors | PASS, 0 broken |
| JSON parsing and Draft 2020-12 schema | PASS |
| Example validates against schema | PASS |
| Severity and identity mutations | PASS, invalid mutations rejected |
| Recovery-document validator | PASS |
| Active RGR rows | PASS, 38 unique rows |
| RGR owner coverage in book 99 | PASS, 38/38 exactly once |
| RGR explicit owner and acceptance link | PASS, 38/38 |
| Historical book-96 ledger | PASS, 10 rows and 0 Open rows |
| Historical closure evidence paths | PASS |
| Research source hash and line count | PASS, 815 lines |
| Research source ranges | PASS, 16 contiguous non-overlapping ranges |
| Research H2-H4 coverage | PASS, 77/77 exactly once |
| Book-99 source IDs | PASS, 16/16 exactly once |

## Current Finding Ledger

| Finding ID | Severity | Status | Owner | Expiry | Recheck trigger |
| --- | --- | --- | --- | --- | --- |
| RG-WDR-011 | P1 | Open | books 02/04/06 schema and recovery-summary owners | before schema v1 freeze | summary severity semantics or routing fields change |

## Finding

### RG-WDR-011 - P1 - `highest_severity` has contradictory pre- and post-demotion semantics

**Exact evidence**

- `schemas/review-evidence.v1.example.json:18` records the proposed finding's pre-validation `normalized_severity` as `high`.
- The same finding is demoted and records `validation.final_severity=medium` at lines 48-53.
- The example summary records `highest_severity=medium` at line 64, so the example treats the summary field as highest surviving/final actionable severity.
- `04-chapter6-review-ingestion-and-residual-closure.md:112-120` describes the summary field as “normalized highest severity.”
- `06-pipeline-integration-recovery-and-compatibility.md:67-76` exposes “highest normalized severity” to recovery consumers.
- `06-pipeline-integration-recovery-and-compatibility.md:101-111` routes validated P0/P1 before validated medium/low findings.

**Failure mode**

A proposed P1 finding normalizes to high and is correctly demoted to medium. An implementation following the example writes summary `highest_severity=medium` and routes it as medium/low. An implementation following Books 04/06 writes `highest_severity=high`; a compact recovery consumer then treats the demoted finding as validated P0/P1, undoing the demotion and potentially selecting a stronger rerun, refresh, fork, or blocking path.

**Context inspected**

Book 02 severity normalization and final disposition; Book 04 summary integration; Book 06 recovery fields, projection matrix, routing priorities and compatibility behavior; schema finding/summary definitions; example counts and severity values.

**Why safeguards do not catch it**

The JSON Schema constrains `highest_severity` only to the severity enum and does not define whether it is computed from `normalized_severity` or `validation.final_severity`. `actionable_count` does not encode the highest actionable severity, so compact consumers cannot resolve the ambiguity without rereading every finding.

**Severity rationale**

P1 is justified because the ambiguity can deterministically reverse a validated severity demotion in recovery routing, defeating the plan's severity trust gate and changing operator actions.

**Required correction**

Define `summary.highest_severity` as the highest `validation.final_severity` among actionable `validated|demoted` findings, with `none` when no actionable finding survives. Rename the prose to “highest actionable final severity,” add count/severity consistency validation, and add a mutation proving a demoted P1 produces summary medium rather than high.

## Historical Ledger Check

Book 96 contained ten historical findings, all `Closed`, with valid closure-evidence paths. It contained zero historical `Open` rows at the reviewed package hash. RG-WDR-011 is new to this immutable review snapshot.

## 97 Owner And Acceptance Check

All 38 active RGR rows have explicit status, owner book, RG phase, owner-book acceptance link, and separate test/evidence intent. Every link and heading anchor resolves.

## 98/99 Coverage Check

The frozen research source matches its declared SHA-256 and 815-line count. Sixteen contiguous, non-overlapping `SRC-*` ranges cover lines 1-815, all 77 H2-H4 headings occur in exactly one range, and Book 99 contains all 16 source IDs and all 38 active RGR IDs exactly once. Original-source coverage passes.

## Final Verdict

The plan is **not ready to implement** while RG-WDR-011 remains Open. A future PASS means only that the plan can be implemented; it does not mean implementation code is complete.
