# Template Customization

Use this document when you need the old AGENTS content for Base/Overlay rules, ADR entry points, PR expectations, or post-clone template customization.

## Primary Sources
- [../../README.md](../../README.md): human-facing template overview and quick start.
- [../PROJECT_DOCUMENTATION_INDEX.md](../PROJECT_DOCUMENTATION_INDEX.md): full document map.
- `docs/architecture/base/00-README.md`: base chapter navigation and maintenance rules.
- [../architecture/ADR_INDEX_GODOT.md](../architecture/ADR_INDEX_GODOT.md): accepted ADR list.
- `docs/adr/guide.md`: ADR writing guidance.
- `.github/PULL_REQUEST_TEMPLATE.md`: PR checklist and release/Sentry expectations.
- `docs/workflows/overlays-authoring-guide.md`: overlay authoring guidance.
- `docs/workflows/contracts-template-v1.md`: contract template entry point.

## After Cloning This Template
1. Update project identity in `project.godot`, `README.md`, and user-facing docs.
2. Choose the default `DELIVERY_PROFILE` in `scripts/sc/config/delivery_profiles.json`.
3. Review workflow names, secrets, and release behavior in `.github/workflows/`.
4. If the new project has real Taskmaster data, replace template fallback assumptions with `.taskmaster/tasks/*.json`.
5. Keep contract SSoT in `Game.Core/Contracts/**` and align new project decisions through ADRs.

## Base, Overlay, And ADR Routing
- Base chapters live in `docs/architecture/base/`.
- PRD-specific feature slices live in `docs/architecture/overlays/<PRD-ID>/08/`.
- Accepted ADRs in `docs/adr/` decide current architecture and guardrails.
- Contract placement rules point back to `Game.Core/Contracts/**`.

## PR And Violation Handling Routing
- Need PR checklist expectations:
  - Read `.github/PULL_REQUEST_TEMPLATE.md`.
- Need ADR or contract validation behavior:
  - Read `scripts/python/task_links_validate.py`, `scripts/python/validate_contracts.py`, and related workflow docs.
- Need to understand why a rule should move out of `AGENTS.md`:
  - Read [11-agents-construction-principles.md](11-agents-construction-principles.md).

## Old AGENTS Coverage Map
- `Base / Overlay 目录约定` -> `docs/architecture/base/00-README.md` + `docs/workflows/overlays-authoring-guide.md`
- `默认 ADR 映射` -> `docs/architecture/ADR_INDEX_GODOT.md`
- `PR 模板要求 / 违例处理` -> `.github/PULL_REQUEST_TEMPLATE.md` + validation scripts and workflow docs
- `Customizing This Template` -> `README.md` + this document
