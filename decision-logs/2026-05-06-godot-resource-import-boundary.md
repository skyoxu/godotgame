# 2026-05-06 Godot Resource Import Boundary

## Context
- Root `Godot --headless --path <repo> --build-solutions --quit` was timing out during editor startup.
- The blocking noise came from two non-runtime trees being scanned as Godot resources:
  - `_bmad/` authoring CSV files with `csv_translation` imports.
  - `logs/` report outputs containing many duplicated Godot UIDs.
- `docs/` also contained documentation-side CSV imports and should not participate in runtime asset discovery.

## Decision
- Treat `docs/`, `_bmad/`, and `logs/` as non-runtime trees for the root Godot project.
- Enforce that boundary with versioned `.gdignore` files at:
  - `docs/.gdignore`
  - `_bmad/.gdignore`
  - `logs/.gdignore`
- Allow `_bmad/.gdignore` and `logs/.gdignore` through `.gitignore` so the boundary survives template copies.
- Keep `.godot/editor/**` cleanup as local-only state repair, not a committed template rule.

## Rationale
- `_bmad/*.csv` files are workflow metadata, not translation tables consumed by the shipped game.
- `logs/**` is generated evidence and should never be part of Godot asset indexing.
- `docs/**` is documentation and should not produce import side effects during root project prewarm.
- Directory-level exclusion is smaller and safer than rewriting the BMAD CSV/import structure to satisfy Godot translation semantics.

## Validation
- After adding the boundary markers, root prewarm no longer emitted `Error importing CSV translation`.
- After local editor-cache cleanup, root prewarm no longer emitted `Cannot navigate to 'res://test_db_audit_exec_query_fail.gd'`.
- Remaining root prewarm output was reduced to the expected nested-project warning for `Tests.Godot`.

## Follow-up
- If a future runtime feature genuinely needs files under `docs/` or `_bmad/`, move those assets into a dedicated runtime-owned directory instead of weakening the boundary.
