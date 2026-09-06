# Post-Split Requirements Ledger

## Rules

- Every new requirement receives a stable `RGR-*` ID before implementation.
- One owner book and one RG phase own each active requirement.
- Status is explicit: `Active`, `Closed`, or `Superseded`.
- An explicit owner-book acceptance anchor and a separate test/evidence intent are mandatory.
- Supersession uses the status registry; prose deletion is not sufficient.
- Adversarial-review findings map to ledger IDs before code changes.

## Requirements

| ID | Status | Owner | Phase | Requirement | Acceptance reference | Test/evidence intent |
| --- | --- | --- | --- | --- | --- | --- |
| RGR-001 | Closed | 01 | RG-0 | Repository evidence policy outranks external agent prompts | [01 Acceptance](01-authority-scope-and-invariants.md#acceptance) | precedence regression test |
| RGR-002 | Closed | 01 | RG-0 | Reviewer output remains untrusted until validation | [01 Acceptance](01-authority-scope-and-invariants.md#acceptance) | authority/unit test |
| RGR-003 | Closed | 02 | RG-0 | Versioned evidence schema and example | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | JSON Schema validation |
| RGR-004 | Closed | 02 | RG-0 | Stable anchor types and reason-code families | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | schema and enum tests |
| RGR-005 | Closed | 02 | RG-0 | P0/P1 full proof contract | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | proof-removal mutation tests |
| RGR-006 | Closed | 02 | RG-0 | One severity normalization mapping | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | duplicate/missing mapping tests |
| RGR-007 | Active | 02 | RG-1 | Derived verdict follows actionable finding states | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | verdict matrix tests |
| RGR-008 | Active | 02 | RG-1 | Zero actionable findings derives OK | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | zero-finding test |
| RGR-009 | Active | 02 | RG-1 | Missing/unparseable evidence derives Unknown | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | parser/input tests |
| RGR-010 | Active | 04 | RG-1 | Chapter 6 prompt includes ECC-style fact gate and zero-findings rule | [04 Acceptance](04-chapter6-review-ingestion-and-residual-closure.md#acceptance) | prompt contract test |
| RGR-011 | Active | 04 | RG-1 | Chapter 6 preserves individual findings before aggregation | [04 Acceptance](04-chapter6-review-ingestion-and-residual-closure.md#acceptance) | summary/sidecar test |
| RGR-012 | Active | 04 | RG-1 | Agent review projects surviving findings instead of generic medium reviewer verdict | [04 Acceptance](04-chapter6-review-ingestion-and-residual-closure.md#acceptance) | projection test |
| RGR-013 | Active | 04 | RG-1 | Empty validated low-priority set cannot create residual state | [04 Acceptance](04-chapter6-review-ingestion-and-residual-closure.md#acceptance) | NewRouge/LastKing fixture |
| RGR-014 | Active | 04 | RG-1 | Residual write is idempotent by normalized finding identity | [04 Acceptance](04-chapter6-review-ingestion-and-residual-closure.md#acceptance) | repeated-family test |
| RGR-015 | Active | 04 | RG-1 | Timeout and Unknown remain distinct from clean | [04 Acceptance](04-chapter6-review-ingestion-and-residual-closure.md#acceptance) | timeout matrix test |
| RGR-016 | Active | 06 | RG-1 | `summary.json` remains stable and existing consumers remain compatible | [06 Acceptance](06-pipeline-integration-recovery-and-compatibility.md#acceptance) | schema regression tests |
| RGR-017 | Active | 06 | RG-1 | Repair and route consumers use actionable findings only | [06 Acceptance](06-pipeline-integration-recovery-and-compatibility.md#acceptance) | route/repair tests |
| RGR-018 | Active | 07 | RG-2 | Sanitized replay corpus covers valid and invalid reviewer families | [07 Acceptance](07-observability-replay-and-performance.md#acceptance) | deterministic replay test |
| RGR-019 | Active | 07 | RG-2 | Metrics record completeness, dispositions, verdict drift, repeats, timeout, and cost | [07 Acceptance](07-observability-replay-and-performance.md#acceptance) | metrics schema test |
| RGR-020 | Active | 07 | RG-2 | Aggregate evidence survives raw-output cleanup | [07 Acceptance](07-observability-replay-and-performance.md#acceptance) | retention fixture |
| RGR-021 | Active | 07 | RG-2 | Validation requires no additional LLM call | [07 Acceptance](07-observability-replay-and-performance.md#acceptance) | backend invocation assertion |
| RGR-022 | Active | 03 | RG-3 | Chapter 5 finding binds source obligation to acceptance and consequence | [03 Acceptance](03-chapter3-5-evidence-profiles.md#acceptance) | semantic fixture |
| RGR-023 | Active | 03 | RG-3 | Missing Chapter 5 input stops as Unknown | [03 Acceptance](03-chapter3-5-evidence-profiles.md#acceptance) | preflight/extract test |
| RGR-024 | Active | 03 | RG-3 | Chapter 5 cannot invent obligations or rewrite equivalent wording | [03 Acceptance](03-chapter3-5-evidence-profiles.md#acceptance) | false-positive fixtures |
| RGR-025 | Active | 03 | RG-4 | Chapter 3 findings use task/requirement/source anchors | [03 Acceptance](03-chapter3-5-evidence-profiles.md#acceptance) | planning fixtures |
| RGR-026 | Active | 03 | RG-4 | Chapter 4 findings use document authority and consequence chain | [03 Acceptance](03-chapter3-5-evidence-profiles.md#acceptance) | overlay fixtures |
| RGR-027 | Active | 05 | RG-4 | Chapter 7 visual findings require screenshot evidence | [05 Acceptance](05-chapter7-ui-review-evidence.md#acceptance) | UI fixture |
| RGR-028 | Active | 05 | RG-4 | Chapter 7 does not create duplicate tasks or apply status patches directly | [05 Acceptance](05-chapter7-ui-review-evidence.md#acceptance) | duplicate/status tests |
| RGR-029 | Active | 06 | RG-5 | Evidence modes and rollback are explicit and profile-owned | [06 Acceptance](06-pipeline-integration-recovery-and-compatibility.md#acceptance) | config/rollback test |
| RGR-030 | Closed | 08 | RG-0 | Phases remain strictly sequential with evidence-backed exits | [08 RG-0 Exit](08-implementation-phases.md#phase-rg-0-policy-adr-schema-and-ownership-freeze) | phase validator test |
| RGR-031 | Active | 09 | RG-5 | No unresolved P0/P1; P2 has owner/expiry/recheck | [09 Global DoD](09-risks-dod-and-glossary.md#global-definition-of-done) | closure validator |
| RGR-032 | Closed | 96 | RG-0 | Split validator covers books, links, ledger, schema, audit, and coverage | [96 Acceptance](96-global-review-and-split-validation.md#acceptance) | mutation suite |
| RGR-033 | Active | 99 | RG-5 | Every active requirement maps exactly once in source coverage | [99 Completion](99-source-coverage.md#completion) | coverage validator |
| RGR-034 | Closed | 02 | RG-0 | Chapter 6 architecture findings have an explicit domain distinct from Chapter 4 architecture-document findings | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | schema enum and profile-routing tests |
| RGR-035 | Closed | 02 | RG-0 | Original severity maps to pre-validation normalized severity before proof evaluation and remains distinct from final severity | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | severity mapping and proof-profile mutation tests |
| RGR-036 | Closed | 06 | RG-0 | Derived OK/Needs Fix/Unknown states map exactly into the existing agent-review verdict/action vocabulary | [06 Acceptance](06-pipeline-integration-recovery-and-compatibility.md#acceptance) | projection matrix and contract regression tests |
| RGR-037 | Closed | 02 | RG-0 | Every sidecar has non-empty task/run identity with a stable synthetic scope identity for non-task reviews | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | empty-identity rejection and synthetic-scope tests |
| RGR-038 | Closed | 02 | RG-0 | Chapter 6 profile ownership and coverage enumerate code, security, test, semantic, architecture, and performance | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | profile catalog and source-coverage enumeration test |
| RGR-039 | Closed | 02 | RG-0 | Summary counts and highest severity derive from final actionable dispositions, not pre-validation normalized severity | [02 Acceptance](02-review-evidence-contracts-and-severity.md#acceptance) | demoted-P1 and zero-actionable summary mutation tests |

## Requirement Status Registry

| ID | Previous status | New status | Superseded by | Reason |
| --- | --- | --- | --- | --- |
| RGR-001 | Active | Closed | n/a | ADR-0032 and RGE-PLAN-014 freeze repository policy precedence. |
| RGR-002 | Active | Closed | n/a | ADR-0032, canonical schema validation, and fallback tests keep reviewer output untrusted. |
| RGR-003 | Active | Closed | n/a | Canonical schema, plan pointer, example, primary validation, and fallback validation are executable. |
| RGR-004 | Active | Closed | n/a | Canonical anchor enums and stable reason-code validation have mutation coverage. |
| RGR-005 | Active | Closed | n/a | Elevated-proof removal fails with RGE-SCHEMA-006. |
| RGR-006 | Active | Closed | n/a | Original-to-normalized severity mapping is unique and mutation tested. |
| RGR-030 | Active | Closed | n/a | RGE-PLAN-011 validates the predecessor matrix and RG-0-owned exit dependencies. |
| RGR-032 | Active | Closed | n/a | The focused validator and thirteen plan mutation tests cover the required split controls. |
| RGR-034 | Active | Closed | n/a | The schema and focused validator preserve distinct architecture and architecture-document domains. |
| RGR-035 | Active | Closed | n/a | Tests preserve original, normalized, and final severity through demotion. |
| RGR-036 | Active | Closed | n/a | RGE-PLAN-009 freezes the OK/Needs Fix/Unknown compatibility projection. |
| RGR-037 | Active | Closed | n/a | Empty identity and synthetic-scope tests pass in fallback and primary validation paths. |
| RGR-038 | Active | Closed | n/a | Schema and RGE-PLAN-014 cover all six Chapter 6 reviewer domains. |
| RGR-039 | Active | Closed | n/a | Summary derivation tests reject pre-demotion highest severity and invalid zero-actionable severity. |

Status transitions are append-only in this registry.

## Research Finding Coverage

| Research finding | Required closure |
| --- | --- |
| ECC gate is prompt-level, not runtime verification | RGR-002, RGR-003, RGR-010, RGR-032 |
| Local parser retains only terminal verdict | RGR-007, RGR-011 |
| Generic fixed-medium agent-review projection loses evidence | RGR-012, RGR-016 |
| NewRouge empty residual records | RGR-013, RGR-014 |
| LastKing missing concrete finding retention | RGR-011, RGR-020 |
| Sanguo exact-line and failure-chain gaps | RGR-004, RGR-005, RGR-018 |
| Sanguo reviewer verdict flips and repeated runs | RGR-014, RGR-018, RGR-019 |
| Chapter 5 missing-input and rewrite risk | RGR-022, RGR-023, RGR-024 |
| Chapter 3/4/7 are deterministic-first | RGR-025, RGR-026, RGR-027, RGR-028 |
| Raw artifact cleanup destroys analysis | RGR-019, RGR-020 |
| Advisory must precede require | RGR-029, RGR-030 |
| Chapter 6 architecture profile must remain distinct from Chapter 4 architecture-document review | RGR-034 |
| Severity normalization must precede proof evaluation and remain auditable after demotion | RGR-035 |
| Unknown must project compatibly without becoming clean or a product finding | RGR-036 |
| Shared Chapter 3-7 sidecars require unambiguous task/run identity | RGR-037 |
| Chapter 6 profile summaries must include every declared reviewer domain | RGR-038 |
| Summary severity must preserve final demotion semantics for recovery routing | RGR-039 |

## Acceptance

- Validator rejects missing/duplicate active IDs.
- Every active row has explicit status, owner, phase, acceptance anchor, and test/evidence intent.
- Every research finding maps to one or more active requirements.
- New adversarial-review requirements are added here before implementation.
