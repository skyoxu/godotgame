# Workflow Rule Feedback Records

Use this directory for durable, git-tracked workflow rule feedback gathered from business repositories.

Scope:

- Workflow 5.1 light-lane execution findings
- Chapter 6 routing, recovery, rerun, and residual-routing findings

Do not store:

- raw `logs/ci/**` artifacts
- temporary debugging notes
- one-off local experiments with no stable artifact evidence

Use the template:

- `docs/workflows/templates/workflow-rule-feedback-template.md`

Recommended filename pattern:

- `YYYY-MM-DD-<repo>-<workflow-family>-<rule-slug>.md`

Examples:

- `2026-04-19-sanguo-chapter6-p1-floor-acceptance-refs.md`
- `2026-04-19-newrouge-5.1-extract-timeout-retry-boost.md`

Template repo example records:

- `2026-04-19-newrouge-5.1-extract-timeout-retry-boost.md`
- `2026-04-19-newrouge-chapter6-p1-floor-acceptance-refs.md`
- `2026-04-19-sanguo-5.1-acceptance-extract-preflight.md`
