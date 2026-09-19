#!/usr/bin/env python3
"""Stable workflow chapter-skill generator entrypoint.

The legacy generator remains byte-for-byte preserved in
`_update_workflow_chapter_skills_legacy.py`.  This wrapper runs it first and then
applies the reusable Knowledge/Impact contract so future evidence refreshes cannot
silently erase Chapter 2/4/5/6 integration.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import _update_workflow_chapter_skills_legacy as legacy
from workflow_chapter_knowledge_overlay import apply_knowledge_overlays


def _template_root(argv: list[str]) -> Path:
    for index, value in enumerate(argv):
        if value == "--template-root" and index + 1 < len(argv):
            return Path(argv[index + 1]).resolve()
        if value.startswith("--template-root="):
            return Path(value.split("=", 1)[1]).resolve()
    return Path(".").resolve()


def _remove_shipped_business_evidence(template_root: Path) -> None:
    evidence_root = template_root / "logs/ci/workflow-business-evidence"
    for skill_root in (template_root / ".agents/skills").glob("workflow-chapter*"):
        references = skill_root / "references/business-repos"
        if references.is_dir():
            evidence_root.mkdir(parents=True, exist_ok=True)
            for source in references.glob("*.md"):
                destination = evidence_root / source.name
                if not destination.exists():
                    destination.write_bytes(source.read_bytes())
            shutil.rmtree(references)
        skill = skill_root / "SKILL.md"
        if skill.is_file():
            text = skill.read_text(encoding="utf-8")
            text = text.replace(
                "Generated evidence may live under `references/business-repos/<repo>.md`. These files are optional regression evidence from known business repositories; they must not define production generation rules.",
                "Sibling-repository evidence is never shipped inside the skill tree. When explicitly needed, refresh it locally under `logs/ci/workflow-business-evidence/`; it is empirical evidence only and never a production rule.",
            )
            text = text.replace(
                "Optionally read `references/business-repos/<repo>.md` only as empirical validation evidence when the target business repo has a generated reference.",
                "Do not load sibling-repository evidence from the shipped skill tree; use locally generated evidence only when explicitly needed.",
            )
            text = text.replace(
                "If that optional evidence file is missing or stale, run `py -3 scripts/python/update_workflow_chapter_skills.py <repo>` from the template repo.",
                "If local empirical evidence is needed, run `py -3 scripts/python/update_workflow_chapter_skills.py <repo>`; generated evidence stays under `logs/ci/workflow-business-evidence/`.",
            )
            skill.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    template_root = _template_root(sys.argv[1:])
    rc = legacy.main()
    if rc == 0:
        _remove_shipped_business_evidence(template_root)
        apply_knowledge_overlays(template_root)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
