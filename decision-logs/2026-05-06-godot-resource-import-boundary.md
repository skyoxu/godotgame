# 2026-05-06 Godot Resource Import Boundary

- Title: godot-resource-import-boundary
- Date: 2026-05-06
- Status: accepted
- Supersedes: none
- Superseded by: none
- Branch: chore/chapter3-skill-sync
- Git Head: 7cc060885124049389d25f9000e19dc879d2dbf7
- Why now: root Godot prewarm was timing out because documentation, BMAD authoring files, and generated logs were being scanned as runtime resources.
- Context: root `Godot --headless --path <repo> --build-solutions --quit` was blocked by non-runtime trees. `_bmad/` contained authoring CSV files that Godot treated as translation imports, `logs/` contained generated reports with duplicated Godot UIDs, and `docs/` contained documentation-side CSV/import files that should not participate in runtime asset discovery.
- Decision: treat `docs/`, `_bmad/`, and `logs/` as non-runtime trees for the root Godot project by committing `.gdignore` boundary markers at `docs/.gdignore`, `_bmad/.gdignore`, and `logs/.gdignore`; allow `_bmad/.gdignore` and `logs/.gdignore` through `.gitignore`; keep `.godot/editor/**` cleanup as local-only state repair rather than a committed template rule.
- Consequences: Godot root startup ignores documentation, BMAD workflow metadata, and generated evidence; future runtime assets must live in runtime-owned directories instead of weakening these boundaries.
- Recovery impact: if root Godot prewarm starts importing docs, BMAD CSVs, or log artifacts again, verify the three `.gdignore` files first and then clear only local editor cache state if stale imports remain.
- Validation: root prewarm stopped emitting `Error importing CSV translation`; after local editor-cache cleanup it also stopped emitting stale `res://test_db_audit_exec_query_fail.gd` navigation errors; remaining output was limited to the expected nested-project warning for `Tests.Godot`.
- Related ADRs: `docs/architecture/ADR_INDEX_GODOT.md`
- Related execution plans: n/a because this was a template boundary hardening change without a separate execution plan
- Related task id(s): n/a because this was PR cleanup and template hardening, not a task-scoped pipeline run
- Related run id: n/a because validation was not tied to one persisted pipeline run id
- Related latest.json: n/a because validation was not tied to a task-scoped latest.json pointer
- Related pipeline artifacts: n/a because validation was local template prewarm output and CI gate output, not a task-scoped artifact directory

## Notes
- `_bmad/*.csv` files are workflow metadata, not translation tables consumed by the shipped game.
- `logs/**` is generated evidence and should never be part of Godot asset indexing.
- `docs/**` is documentation and should not produce import side effects during root project prewarm.
- Directory-level exclusion is smaller and safer than rewriting the BMAD CSV/import structure to satisfy Godot translation semantics.
- If a future runtime feature genuinely needs files under `docs/` or `_bmad/`, move those assets into a dedicated runtime-owned directory instead of weakening the boundary.
