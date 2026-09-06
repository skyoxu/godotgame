# Source Coverage

## Required Books

- 00 split index
- 01 authority, scope, invariants
- 02 contracts and severity
- 03 Chapter 3-5 profiles
- 04 Chapter 6 ingestion and residual closure
- 05 Chapter 7 UI evidence
- 06 pipeline/recovery/compatibility
- 07 observability/replay/performance
- 08 implementation phases
- 09 risks/DoD/glossary
- 96 global review/validation
- 97 requirements ledger
- 98 research audit
- 99 source coverage

## Coverage Dimensions

| Dimension | Covered by |
| --- | --- |
| authority and policy precedence | top-level, 00, 01 |
| shared schema, anchors, states, proof, severity, verdict | 02 |
| Chapter 3 task review | 03 |
| Chapter 4 overlay/contract review | 03 |
| Chapter 5 semantic review | 03 |
| Chapter 6 code/security/test/semantic/architecture/performance review | 04 |
| empty residual and idempotency | 04, 06 |
| Chapter 7 visual/accessibility/localization review | 05 |
| sidecar and compatibility ownership | 06 |
| recovery, route, Unknown, rollback | 06 |
| metrics, replay, retention, performance | 07 |
| sequential delivery and task sizing | 08 |
| risks, DoD, glossary, stop conditions | 09 |
| plan and phase-exit review | 96 |
| stable requirement preservation | 97 |
| research source mapping | 98 |

## Source Inputs

| Source | Used by |
| --- | --- |
| ECC `agents/code-reviewer.md` fixed commit | 01, 02, 04, 97 |
| ECC false-positive guard test | 04, 07, 97 |
| completed local research report | all books through 98 mapping |
| `workflow.md` Chapter 3-7 | 01, 03, 04, 05, 06, 08 |
| Chapter 3-7 component routing | 03, 04, 05 |
| UI/UX implementation policy | 03, 04, 05 |
| ADR-0005 | top-level, 01, 06, 08, 09 |
| ADR-0017 | 07, 08 |
| current LLM review prompting/engine | 02, 04, 06 |
| current agent-review contract/builder | 02, 04, 06 |
| NewRouge durable residual evidence | 04, 07, 97 |
| LastKing durable residual evidence | 04, 07, 97 |
| Sanguo raw reviewer and pipeline evidence | 04, 07, 97 |

## Explicit Requirement Coverage

| Owner | RGR IDs |
| --- | --- |
| 01 | RGR-001, RGR-002 |
| 02 | RGR-003, RGR-004, RGR-005, RGR-006, RGR-007, RGR-008, RGR-009, RGR-034, RGR-035, RGR-037, RGR-038, RGR-039 |
| 03 | RGR-022, RGR-023, RGR-024, RGR-025, RGR-026 |
| 04 | RGR-010, RGR-011, RGR-012, RGR-013, RGR-014, RGR-015 |
| 05 | RGR-027, RGR-028 |
| 06 | RGR-016, RGR-017, RGR-029, RGR-036 |
| 07 | RGR-018, RGR-019, RGR-020, RGR-021 |
| 08 | RGR-030 |
| 09 | RGR-031 |
| 96 | RGR-032 |
| 99 | RGR-033 |

## Research Source Range Coverage

Every source range declared by book 98 appears exactly once in this table. Owner lists may contain multiple books, but the source ID itself cannot be duplicated or omitted.

| Source IDs | Covered content owner books |
| --- | --- |
| SRC-000 | 00, 98 |
| SRC-001 | 00, 01, 98 |
| SRC-002 | 01, 04, 06, 07 |
| SRC-003 | 01, 02, 04, 06 |
| SRC-004 | 01, 02, 03, 04, 05, 06, 07, 08 |
| SRC-005 | 04, 07, 08 |
| SRC-006 | 03 |
| SRC-007 | 03 |
| SRC-008 | 03 |
| SRC-009 | 02, 04, 06 |
| SRC-010 | 05 |
| SRC-011 | 02, 06, 07, 08, 09 |
| SRC-012 | 00, 01, 07, 08 |
| SRC-013 | 03, 04, 05 |
| SRC-014 | 08 |
| SRC-015 | 09, 96, 99 |

## Assertions

- Every active RGR entry appears exactly once in the owner table.
- Every required book is linked from `00-index.md` and the top-level plan.
- Every research recommendation family maps in book 98.
- Every `SRC-*` range from book 98 appears exactly once, ranges cover lines 1-815 without gaps or overlaps, and every source H2-H4 heading belongs to exactly one range.
- No book duplicates another book's normative contract.
- Chapter 3, 4, and 7 deterministic authority is preserved.
- Durable implemented rules migrate to ADR/workflow/docs before RG-5 exit.

## Completion

Coverage is complete only when the focused split validator passes, schema/example validation passes, all active RGR entries are closed or explicitly superseded, and global review finds no unmapped requirement.
