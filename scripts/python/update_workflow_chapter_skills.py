#!/usr/bin/env python3
"""Stable workflow chapter-skill generator entrypoint.

The legacy generator remains byte-for-byte preserved in
`_update_workflow_chapter_skills_legacy.py`.  This wrapper runs it first and then
applies the reusable Knowledge/Impact contract so future evidence refreshes cannot
silently erase Chapter 2/4/5/6 integration.
"""
from __future__ import annotations

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


def main() -> int:
    template_root = _template_root(sys.argv[1:])
    rc = legacy.main()
    if rc == 0:
        apply_knowledge_overlays(template_root)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
