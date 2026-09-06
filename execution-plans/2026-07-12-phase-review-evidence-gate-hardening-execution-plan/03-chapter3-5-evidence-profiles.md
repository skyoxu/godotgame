# Chapter 3-5 Evidence Profiles

## Purpose

Define task-planning, overlay-document, and semantic evidence profiles without turning Chapter 3-5 into a generic code-review pipeline.

## Chapter 3: Task Triplet Planning

### Existing Review Points

- task-intent quality audit
- requirement coverage matrix
- duplicate-candidate review
- task triplet patch review before write
- task links, refs, triplet consistency, and semantic review tier validation

Deterministic validators remain authoritative for schema, refs, IDs, and coverage thresholds.

### Evidence Profile

A Chapter 3 finding requires:

- candidate or task ID
- requirement ID and exact source reference
- affected task view and field
- conflicting task ID for duplication claims
- concrete consequence: missing coverage, duplicate implementation, invalid ownership, or unfalsifiable acceptance
- suggested minimal task-shape correction

### False-Positive Exclusions

- missing Chapter 4 overlay or final contract detail
- missing Chapter 7 visual polish, screenshots, or component kit
- absence of mature-project metadata not required by current Chapter 3 schema
- soft component-routing preference treated as a hard defect without task/ADR promotion
- requirement wording differences that preserve the same implementation obligation

### Gate Behavior

- structural validator failures: existing hard behavior
- LLM/editorial quality findings: advisory evidence gate
- duplicate-candidate write: block until explicitly merged, superseded, or accepted

## Chapter 4: Overlays And Contracts

### Existing Review Points

- LLM output JSON parsing
- dry-run, simulate, outlier repair, limited apply
- overlay front matter, headings, refs, and path validation
- contract location, BCL-only boundary, XML docs, and unit tests

### Evidence Profile

A Chapter 4 semantic finding requires:

- overlay or contract path
- exact heading, line, field, or quoted statement
- authoritative Base, ADR, task, or contract source
- contradiction, duplication, wrong ownership, or missing backlink
- downstream consequence for implementation, testing, or acceptance
- explanation of why existing overlay/contract validators do not catch it

### False-Positive Exclusions

- referencing Base/ADR thresholds rather than copying them
- concrete feature slices living in overlay chapter 08
- absence of acceptance rewrites during overlay-only generation
- incomplete content in a first scaffold before bounded repair/apply
- contract definitions referenced by path instead of copied into docs
- intentionally empty template sections clearly marked as template-owned

### Gate Behavior

- model JSON/schema/path output: hard parse validation
- overlay/contract deterministic validation: existing hard behavior
- semantic outlier review: advisory until RG-4 promotion
- first pass must never be full apply

## Chapter 5: Semantics Stabilization

### Existing Review Points

- acceptance extraction preflight
- obligation extraction
- acceptance alignment and rewrite
- subtasks coverage
- semantic equivalence gate
- rewrite-ratio, failure-family, timeout, batch, and freeze stop-loss

### Evidence Profile

A Chapter 5 Needs Fix finding requires:

- exact authoritative task field, source obligation, or source document anchor
- exact current acceptance item or explicit missing insertion location
- obligation chain: source obligation -> current representation -> missing/distorted behavior
- affected test, downstream task, or delivery decision
- explanation of why deterministic refs/anchor/schema validation does not already decide the issue
- minimal wording or item-level delta

### Unknown Conditions

- task or acceptance input missing
- extraction output unparseable
- authoritative source conflict cannot be resolved
- prompt budget truncates the controlling obligation
- referenced evidence path is unavailable

Unknown stops semantic mutation. It does not open another downstream reviewer.

### False-Positive Exclusions

- restating deterministic refs, anchors, schemas, ADR checks, or static scans
- inventing obligations absent from authoritative sources
- rewriting acceptance for style while preserving semantics
- treating equivalent acceptance wording as a gap
- promoting deliberately deferred Chapter 7 visual work into a Chapter 5 defect
- broadening one task to cover neighboring task obligations

### Gate Behavior

- preflight failure: stop and fix input
- extraction Needs Fix: validate finding before align/coverage continuation
- rewrite apply: preserve pre-rewrite finding sidecar and rewrite diff
- no validated semantic finding: no rewrite and semantic verdict OK
- repeated normalized family without new anchor: stop or record once

## Implementation Targets

Likely modules or owners:

- Chapter 3 candidate audit and patch review scripts under `scripts/python/`
- overlay generation/parser modules under `scripts/sc/_overlay_generator_*`
- overlay validators under `scripts/python/`
- Chapter 5 obligations, alignment, coverage, and semantic gate modules
- shared evidence parser/validator introduced in RG-1/RG-2

Exact file ownership is frozen in the RG-0 decision log before edits.

## Tests

- Chapter 3 duplicate and missing-coverage fixtures
- Chapter 3 false-positive fixtures for deferred overlay/UI metadata
- Chapter 4 quote/source/ownership fixtures
- Chapter 4 scaffold and Base-reference false-positive fixtures
- Chapter 5 missing-input -> Unknown fixtures
- Chapter 5 invented-obligation and equivalent-wording drop fixtures
- Chapter 5 validated missing-obligation Needs Fix fixture
- repeated-family stop-loss and rewrite-idempotency fixtures

## Acceptance

- Chapter 3-5 deterministic validators keep their current authority.
- No Chapter 3-5 review finding uses an artificial code failure scenario when a document consequence chain is appropriate.
- Missing Chapter 5 input cannot produce Needs Fix.
- Semantic rewrites require a surviving evidence-gated finding.
- Chapter 4 outlier review cannot bypass dry-run/simulate/limited-apply order.
