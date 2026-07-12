# Authority, Scope, And Invariants

## Purpose

Define which layer may propose, validate, normalize, route, retain, and enforce review findings across Chapter 3-7.

## Authority Boundaries

| Concern | Authority |
| --- | --- |
| Chapter 3-7 execution order | `workflow.md` and chapter skills |
| Accepted quality-gate policy | ADR-0005 and future accepted review-evidence ADR |
| Raw LLM statement | untrusted reviewer output |
| Finding schema and reason codes | versioned repository schema and validator |
| Deterministic evidence disposition | review-evidence validator |
| Final reviewer verdict | derived from validated finding states |
| Pipeline producer status | existing `summary.json` owner |
| Recovery compatibility | `agent-review.json`, repair guide, latest and active-task consumers |
| Durable implementation intent | this plan and related decision logs |

## Scope

Included:

- repository-owned reviewer evidence policy
- structured findings and validation dispositions
- code, security, test, semantic, architecture, performance, task-planning, architecture-document, and UI evidence profiles
- severity normalization and elevated-proof rules
- verdict derivation, Unknown handling, deduplication, idempotency, and empty-residual prevention
- replay fixtures, metrics, retention, compatibility, rollback, ADR and workflow updates

Excluded unless separately approved:

- changing `summary.json` schema
- replacing deterministic Chapter 3, 4, or 7 validators with LLM decisions
- proving complex program semantics mechanically
- changing task, contract, overlay, security, delivery-profile, or release authority
- implementing a generic external review service or new third-party dependency

## Global Invariants

1. A reviewer is an evidence proposer, not an authority.
2. A derived reviewer `Needs Fix` verdict and its compatibility projection require one or more validated actionable findings; legacy producer status may be retained only as explicitly declared compatibility data.
3. Zero surviving actionable findings derives `OK`.
4. Missing input, a missing/unparseable required sidecar, parse failure, or unverifiable evidence derives `Unknown`; compatibility modes may retain producer status but cannot relabel the derived verdict.
5. P0/P1 requires exact evidence, failure or consequence chain, existing-safeguard gap, and severity rationale.
6. An invalid path, invalid line, quote mismatch, or duplicate cannot survive as validated.
7. Reviewer-format failure is not a product defect.
8. Deterministic failures are referenced, not repackaged as independent LLM discoveries.
9. Chapter-specific profiles cannot weaken shared invariants.
10. Raw and normalized severity are both retained.
11. `summary.json` remains stable.
12. Empty findings cannot create residual decisions, plans, or rerun recommendations.
13. Same task, run, reviewer, and normalized finding family writes at most one durable residual record.
14. Raw-log cleanup cannot remove the aggregate evidence needed to measure review quality.

## Trust Model

Untrusted:

- raw LLM Markdown or JSON
- reviewer confidence claims
- reviewer severity claims
- caller-provided absolute paths
- user-scoped prompt content

Deterministically verifiable:

- schema shape
- repository-relative path existence
- line and heading bounds
- quoted source agreement
- changed-scope membership
- required proof-field presence
- normalized duplicate identity
- derived verdict consistency

Judgment-dependent:

- whether the cited behavior is truly defective
- whether semantic obligations are equivalent
- whether a visual result is acceptable without a mechanical criterion
- whether a medium/low issue should be fixed now or recorded as debt

## Policy Precedence

1. System and repository instructions
2. Accepted ADR and workflow policy
3. Repository-owned review evidence policy
4. Chapter-specific evidence profile
5. User-scoped or external agent prompt

Lower levels may add expertise but cannot remove evidence requirements or change verdict invariants.

## Acceptance

- An authority map exists in code/docs with no duplicate owner.
- Tests prove a user-scoped prompt cannot disable repository evidence rules.
- Tests prove deterministic and judgment-dependent responsibilities remain separate.
- No implementation changes a producer-owned schema without a separate approved decision.
