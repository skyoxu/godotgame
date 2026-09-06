# Research-To-Split Audit

## Source

Primary source:

- `_bmad-output/planning-artifacts/research/technical-ecc-review-anti-hallucination-research-2026-07-12.md`
- SHA-256: `a7ee0737ef77e15e882544b49ce8f3176943b6ddbb0e8ffff52640baf81f7241`
- UTF-8 line count: `815`

External source baseline:

- `affaan-m/ECC` commit `40927950c49f6e742d341e20ff7b9b7e1e7bfff5`

Business evidence:

- `newrouge-github-main`
- `lastking`
- `sanguo`

## Source Range Registry

The registry covers the complete frozen source byte-for-byte through contiguous, non-overlapping UTF-8 line ranges. A source heading or recommendation is covered only through the one range containing its line. The focused validator must reject a hash/line-count mismatch, a gap, an overlap, or a source H2-H4 heading outside exactly one range.

| Source ID | Source lines | Research content | Split owner |
| --- | --- | --- | --- |
| SRC-000 | 1-22 | metadata, methodology preface, and report title | 00, 98 |
| SRC-001 | 23-54 | research overview and confirmed scope | 00, 01, 98 |
| SRC-002 | 55-114 | ECC/local stack, source pinning, regression protection, orchestration, prompts, artifacts, and adoption assessment | 01, 04, 06, 07 |
| SRC-003 | 115-236 | integration flow, boundary, output protocols, code/document contracts, sidecars, severity, zero findings, false positives, and trust boundary | 01, 02, 04, 06 |
| SRC-004 | 237-370 | system architecture, validation boundary, states, severity, sidecars, Chapter 3-7 scope, security, performance, and deployment | 01, 02, 03, 04, 05, 06, 07, 08 |
| SRC-005 | 371-437 | business-repository noise baseline and adoption strategy | 04, 07, 08 |
| SRC-006 | 438-456 | Chapter 3 implementation profile | 03 |
| SRC-007 | 457-474 | Chapter 4 implementation profile | 03 |
| SRC-008 | 475-495 | Chapter 5 implementation profile | 03 |
| SRC-009 | 496-524 | Chapter 6 code, semantic, security, architecture, performance, and test profiles | 02, 04, 06 |
| SRC-010 | 525-544 | Chapter 7 implementation profile | 05 |
| SRC-011 | 545-621 | shared sidecar, testing, deployment, cost, ADR requirement, and success metrics | 02, 06, 07, 08, 09 |
| SRC-012 | 622-686 | synthesis, verified ECC findings, business evidence, and strategic recommendation | 00, 01, 07, 08 |
| SRC-013 | 687-742 | Chapter 3-7 decision matrix and cross/chapter false-positive catalogs | 03, 04, 05 |
| SRC-014 | 743-779 | five-phase implementation roadmap | 08 |
| SRC-015 | 780-815 | risks, limitations, source verification, and final conclusion | 09, 96, 99 |

## Normalization

- The top-level file keeps recovery metadata, authority, Gates, book routing, order, and completion.
- Detailed normative text exists in one owner book.
- Empirical numbers remain baseline evidence, not automatic policy thresholds.
- ECC false-positive rules are adapted into shared and chapter-specific catalogs.
- Code and document evidence chains remain distinct.
- Proposed implementation details are separated from accepted durable policy.

## Deliberate Omissions

- no implementation code changes
- no third-party dependency selection
- no enforcement threshold numbers
- no breaking `agent-review.json` version
- no direct mutation of sibling business repositories
- no claim that every historical Needs Fix was false

## Audit Result

All frozen source lines and H2-H4 headings map through one stable source range. Coverage is finalized by `99-source-coverage.md` and must be enforced by the RG-0 split validator before RG-1 implementation.
