# Review Evidence Gate Hardening Split Index

Status: Primary split implementation plan for evidence-gated Chapter 3-7 review.

## Authority

- The top-level execution plan is the recovery entry and metadata owner.
- This directory is the implementation-detail authority.
- The completed ECC research report is the empirical and external-source baseline.
- `workflow.md` remains the Chapter 3-7 execution-policy source until approved changes are implemented.
- `docs/adr/ADR-0005-quality-gates.md` remains the current accepted quality-gate decision.
- No book may redefine `summary.json`, task triplet, overlay, contract, acceptance, security profile, or Chapter 7 artifact authority.
- Implemented durable rules must migrate from this plan into accepted ADRs, workflow docs, agent docs, schemas, and tests.

## Reading Order

1. [Authority, Scope, And Invariants](01-authority-scope-and-invariants.md)
2. [Review Evidence Contracts And Severity](02-review-evidence-contracts-and-severity.md)
3. [Chapter 3-5 Evidence Profiles](03-chapter3-5-evidence-profiles.md)
4. [Chapter 6 Review Ingestion And Residual Closure](04-chapter6-review-ingestion-and-residual-closure.md)
5. [Chapter 7 UI Review Evidence](05-chapter7-ui-review-evidence.md)
6. [Pipeline Integration, Recovery, And Compatibility](06-pipeline-integration-recovery-and-compatibility.md)
7. [Observability, Replay, And Performance](07-observability-replay-and-performance.md)
8. [Implementation Phases](08-implementation-phases.md)
9. [Risks, Definition Of Done, And Glossary](09-risks-dod-and-glossary.md)
10. [Global Review And Split Validation](96-global-review-and-split-validation.md)
11. [Post-Split Requirements Ledger](97-post-split-requirements-ledger.md)
12. [Research-To-Split Audit](98-research-to-split-audit.md)
13. [Source Coverage](99-source-coverage.md)

## Change Rules

- Every normative requirement has one owner book.
- Cross-book summaries link to owners and do not copy full contracts.
- Schema, severity, reason-code, compatibility, and promotion changes require ADR ownership and second review.
- Every implementation task records Gate, owner, reviewer, allowed paths, tests, evidence, rollback, and source requirement IDs.
- Chapter-specific review profiles may strengthen the shared contract but cannot weaken global invariants.
- New adversarial-review requirements enter `97-post-split-requirements-ledger.md` before implementation.
- `96-global-review-and-split-validation.md` defines mechanical split validation and phase-exit review.

## Required Schemas

- [Review evidence JSON Schema](schemas/review-evidence.v1.schema.json)
- [Review evidence example](schemas/review-evidence.v1.example.json)
