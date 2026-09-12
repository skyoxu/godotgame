#!/usr/bin/env python3
"""Idempotently add Knowledge/Impact contracts to generated chapter skills."""
from __future__ import annotations

from pathlib import Path

BEGIN = "<!-- KNOWLEDGE_IMPACT_OVERLAY_BEGIN -->"
END = "<!-- KNOWLEDGE_IMPACT_OVERLAY_END -->"

OVERLAYS = {
    "workflow-chapter2-repository-bootstrap": """## Knowledge / Impact Contract

- Run `py -3 scripts/python/init_knowledge_catalog.py --repo-root .` during repository bootstrap. It may create empty directories, policies, and schemas only; it must not seed sibling-repository task/gameplay data.
- Read `docs/knowledge/README.md` and `docs/workflows/project-health-knowledge.md` before treating Knowledge output as repository authority.
- `serve-project-health` exposes `/latest.html` and the same-origin `/knowledge/` investigation page on `127.0.0.1`.
- A fresh template with no `.taskmaster/tasks/*.json` is a valid empty state.
""",
    "workflow-chapter4-overlays-contracts-baseline": """## Knowledge / Impact Contract

- Before writing overlays/contracts, run `prepare_knowledge_context.py --consumer chapter4 --query \"<architecture/product intent>\"`.
- Chapter 4 candidates are observe-only. Re-read candidate files directly; ranking is never acceptance and Chapter 4 does not freeze context.
- Direct PRD/GDD/ADR/Overlay/Contract/source authority remains stronger than locator output.
""",
    "workflow-chapter5-semantics-stabilization": """## Knowledge / Impact Contract

- Before semantic stabilization, run `prepare_knowledge_context.py --consumer chapter5 --task-id <id> --query \"<task acceptance>\"`.
- Chapter 5 candidates are observe-only. Re-read candidate files directly and do not turn ranking into acceptance.
- Acceptance extraction or triplet defects remain stop-and-fix signals; Knowledge retrieval must not hide them.
""",
    "workflow-chapter6-single-task-daily-loop": """## Knowledge / Impact Contract

- Before RED, prepare `consumer=chapter6` candidates, re-read sources directly, record explicit accept/reject decisions with reasons, and freeze them with `freeze_knowledge_context.py`.
- Run `analyze_impact.py --target <path-or-symbol> --strict` and validate revision/frozen-context lineage with `impact_analysis_handoff.py` before implementation consumes the report.
- Frozen semantic scope must not expand silently during RED/GREEN/REFACTOR. A genuine scope change requires a new candidate/decision/freeze revision.
- Review uses a separate `consumer=review` candidate set and freeze. Never relabel or reuse a Chapter 6 freeze as Review.
- After implementation evidence is stable, run `chapter6_knowledge.py --task-id <id> --path <reviewed-resource>` only for resources actually reviewed by the task. With no reviewed paths, the explicit-reviewed resource record must skip instead of inventing associations.
- When developer-facing semantic explanation would materially help, add `--semantic --llm-backend <codex-cli|openai-api>`. Semantic output is accepted only when every resource path, JSON pointer, scene node, and asset binding resolves to reconstructed snapshot evidence; generated explanations remain non-authoritative.
- `generate_knowledge_links.py` is the deterministic task-resource reconstruction layer used before semantic enrichment. Do not hand-author generated links to make a page look complete.
- Knowledge and Impact artifacts are bounded evidence; they never replace Taskmaster, PRD/GDD, ADR/Base/Overlay, Contracts, source, or test authority.
""",
}


def _strip_existing(text: str) -> str:
    while BEGIN in text and END in text:
        start = text.index(BEGIN)
        finish = text.index(END, start) + len(END)
        prefix = text[:start].rstrip()
        suffix = text[finish:].lstrip("\n")
        text = prefix + "\n\n" + suffix
    return text


def apply_overlay(path: Path, body: str) -> bool:
    if not path.exists():
        raise FileNotFoundError(path)
    original = path.read_text(encoding="utf-8")
    text = _strip_existing(original)
    anchor = "\n## Idempotent Procedure\n"
    if anchor not in text:
        raise ValueError(f"Idempotent Procedure heading not found: {path}")
    block = f"\n{BEGIN}\n{body.rstrip()}\n{END}\n"
    updated = text.replace(anchor, block + anchor, 1)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def apply_knowledge_overlays(template_root: Path) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for name, body in OVERLAYS.items():
        path = template_root / ".agents" / "skills" / name / "SKILL.md"
        results[name] = apply_overlay(path, body)
    return results
