# Example scene encoding and explicit prewarm stages

- Branch: codex/fix-example-scenes-and-prewarm
- Git Head: 749f337189481af00283f20458cf39217399729c
- Related ADRs: ADR-0005, ADR-0018
- Related task id(s): n/a - user-authorized repository follow-up
- Related run id: n/a - new PR Windows CI pending
- Related latest.json: n/a - GitHub Actions provides run state
- Related pipeline artifacts: logs/e2e/ and logs/ci/
- Title: Example scene encoding and explicit prewarm stages
- Date: 2026-09-06
- Status: accepted
- Supersedes: n/a - follow-up to PR 74
- Superseded by: n/a - current decision
- Why now: User authorized both residual fixes after merging PR 73
- Context: Eight BOM-prefixed scenes fail parsing; a combined cold editor build/import invocation times out then succeeds on retry
- Decision: Remove scene BOMs, test all eight scenes in required smoke, and import before building with bounded stages and immediate failure propagation
- Consequences: Scene validity is exercised beyond the main scene; prewarm no longer retries or ignores fallback failures
- Recovery impact: prewarm-import.txt, prewarm-build.txt and prewarm-summary.json identify failed stage and timing under logs/e2e/
- Validation: Local regression tests pass; actual Windows timing and scene results pending in PR
- Related execution plans: execution-plans/2026-09-06-example-scenes-prewarm.md

The import command uses Godot's documented --import behavior: wait for resources to finish importing and exit. Build follows in a second invocation after the resource cache exists. This targets the observed cold import/build interaction without reducing the 300-second per-stage safety bound.

Reference: https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html
