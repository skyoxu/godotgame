"""Content-aware freshness checks for published repository Knowledge.

A Knowledge publication is stale only when authoritative inputs changed after the
published commit. Generated publication outputs and unrelated implementation
changes are intentionally ignored so a derived-state PR does not invalidate
itself when merged.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from _knowledge_catalog_builder import _eligible_source, _excluded, normalize_path

# These files affect how a publication is built or formally consumed even when
# they are not ordinary catalog sources.
PUBLICATION_CONTROL_PLANE_INPUT_FILES = {
    "scripts/python/_knowledge_catalog_builder.py",
    "scripts/python/_knowledge_locator_core.py",
    "scripts/python/build_knowledge_catalog.py",
    "scripts/python/freeze_knowledge_context.py",
    "scripts/python/knowledge_locator.py",
    "scripts/python/knowledge_publication_freshness.py",
    "scripts/python/prepare_knowledge_context.py",
    "scripts/python/publish_knowledge_catalog.py",
}
PUBLICATION_CONTROL_PLANE_INPUT_PREFIXES = (
    "knowledge/policies/",
    "knowledge/evaluation/",
    "knowledge/contracts/",
)


def publication_relevant(path: str, exclusions: dict[str, Any]) -> bool:
    """Return whether a changed repository path can alter published Knowledge."""
    normalized = normalize_path(path)
    if normalized in PUBLICATION_CONTROL_PLANE_INPUT_FILES:
        return True
    if normalized.startswith(PUBLICATION_CONTROL_PLANE_INPUT_PREFIXES):
        return True
    return _eligible_source(normalized) and not _excluded(normalized, exclusions)


def publication_freshness_reason(
    root: Path,
    published_commit: str,
    authority_ref: str,
    exclusions: dict[str, Any],
) -> str | None:
    """Return a stable stale reason, or ``None`` when authority inputs are equivalent."""
    if not published_commit or not authority_ref:
        return "authority_binding_invalid"

    current = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", authority_ref],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if current.returncode:
        return "authority_ref_unavailable"
    current_commit = current.stdout.strip()

    published = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{published_commit}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    if published.returncode:
        return "published_commit_unavailable"

    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", published_commit, current_commit],
        capture_output=True,
        check=False,
    )
    if ancestor.returncode != 0:
        return "authority_ref_diverged"

    changed = subprocess.run(
        [
            "git", "-C", str(root), "diff", "--no-renames", "--name-only", "-z",
            published_commit, current_commit,
        ],
        capture_output=True,
        check=False,
    )
    if changed.returncode:
        return "authority_diff_failed"

    for raw in changed.stdout.split(b"\0"):
        if not raw:
            continue
        try:
            path = raw.decode("utf-8")
        except UnicodeDecodeError:
            return "authority_path_encoding_invalid"
        try:
            if publication_relevant(path, exclusions):
                return "authority_inputs_changed"
        except ValueError:
            return "authority_path_invalid"
    return None
