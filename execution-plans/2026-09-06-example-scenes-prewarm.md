# Example scenes and GdUnit cold prewarm

- Branch: codex/fix-example-scenes-and-prewarm
- Git Head: 749f337189481af00283f20458cf39217399729c
- Related ADRs: ADR-0005, ADR-0018
- Related task id(s): n/a - user-authorized repository follow-up
- Related run id: n/a - new PR Windows CI pending
- Related latest.json: n/a - GitHub Actions provides run state
- Related pipeline artifacts: logs/e2e/ and logs/ci/
- Title: Example scenes and GdUnit cold prewarm
- Status: active
- Goal: Load all eight example scenes and remove the observed cold prewarm retry cost
- Scope: Example scene encoding, required smoke coverage, GdUnit prewarm runner
- Current step: Windows validation
- Last completed step: Local Python regression tests
- Stop-loss: Preserve failures; do not skip scene checks or normalize timeout into success
- Next action: Verify new PR smoke, quality and export evidence
- Recovery command: git fetch origin codex/fix-example-scenes-and-prewarm
- Open questions: Cold Windows import/build duration and scene runtime results
- Exit criteria: Eight new scene checks pass; first prewarm completes without retry; release smoke passes
- Related decision logs: decision-logs/2026-09-06-example-scenes-prewarm.md

Baseline: PR 74 Smoke spent 314 seconds in its GdUnit step; prior artifact evidence showed a 300-second first prewarm timeout followed by retry success. All eight example scenes have a UTF-8 BOM and produced first-line parse errors.

Start from main after PR 73 and PR 74. Use an isolated worktree so the original workspace, including its existing image edit, is preserved. Validate on Windows before claiming the cold-start issue is resolved.
