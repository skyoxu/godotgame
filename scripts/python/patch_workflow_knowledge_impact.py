#!/usr/bin/env python3
"""Idempotently install the Knowledge/Impact cross-chapter contract in workflow.md."""
from __future__ import annotations

import argparse
from pathlib import Path

BEGIN = "<!-- KNOWLEDGE_IMPACT_WORKFLOW_CONTRACT_BEGIN -->"
END = "<!-- KNOWLEDGE_IMPACT_WORKFLOW_CONTRACT_END -->"

BLOCK = r'''<!-- KNOWLEDGE_IMPACT_WORKFLOW_CONTRACT_BEGIN -->
## 1.5 Knowledge / Impact cross-chapter contract

This contract is normative for Chapters 2, 4, 5, and 6. It augments the existing workflow; it does not replace newer Chapter 2.5, Chapter 3, Chapter 6 recovery/stop-loss behavior, or Chapter 7.

General authority rules:

- Knowledge retrieval is evidence discovery, not a second source of truth. Taskmaster, PRD/GDD, ADR/Base/Overlay, Contracts, source, and executable tests remain authoritative in their governed scopes.
- Locator ranking never means semantic acceptance. Candidate files must be re-read directly before use.
- A fresh template with no business task data is valid. Never copy sibling-repository task ids, gameplay entities, asset mappings, hashes, generated publications, or runtime evidence into this template.
- Consumer policies are separate for `repository-session`, `chapter4`, `chapter5`, `chapter6`, and `review`; do not relabel one consumer's frozen context as another's.
- Browser investigation may use an ephemeral policy-aware catalog, but formal Chapter 6 and Review freezes require `publication_state = published-current`.

Chapter 2 bootstrap additions:

```powershell
py -3 scripts/python/init_knowledge_catalog.py --repo-root .
```

- Read `docs/knowledge/README.md`, `docs/workflows/project-health-knowledge.md`, and the policies under `knowledge/policies/`.
- Empty Knowledge directories/policies and an empty evaluation suite are allowed; bootstrap must not seed business records or product query expectations.
- After bootstrap/control-plane changes are committed on local `main`, publish and validate the hash-bound Knowledge generation:

```powershell
py -3 scripts/python/publish_knowledge_catalog.py --repository-root . --publish
py -3 scripts/python/publish_knowledge_catalog.py --repository-root . --check
```

- Publication is blocked if Knowledge policies/evaluation/control-plane scripts are dirty. `knowledge/indexes/current.json` and `last-known-good.json` bind generations under `knowledge/indexes/generations/<generation-id>/` to hashes and the authority ref.
- `serve-project-health` must expose both `/latest.html` and the same-origin `/knowledge/` investigation surface on `127.0.0.1`.

Chapter 4 additions, before overlay / contract authoring:

```powershell
py -3 scripts/python/prepare_knowledge_context.py --consumer chapter4 --query "<architecture/product intent>"
```

- Chapter 4 candidates are observe-only. Re-read the candidate sources; do not freeze or auto-accept them.
- Direct PRD/GDD/ADR/Overlay/Contract/source evidence remains stronger than locator rank.

Chapter 5 additions, before semantic stabilization:

```powershell
py -3 scripts/python/prepare_knowledge_context.py --consumer chapter5 --task-id <id> --query "<task acceptance>"
```

- Chapter 5 candidates are task-scoped and observe-only.
- Knowledge retrieval must never hide an acceptance extraction, refs, coverage, or semantic-gate defect.

Chapter 6 additions, before RED:

1. Ensure the Knowledge publication is current. If local `main`, policies, exclusions, evaluation, or control-plane code changed, republish before preparing a formal context.
2. Prepare `consumer=chapter6` candidates for the current task and intent. Formal preparation rejects ephemeral Knowledge.
3. Re-read candidate files directly.
4. Record an explicit accept/reject decision for every candidate with non-empty `reason` and `satisfies` fields.
5. Freeze the accepted context with `freeze_knowledge_context.py`; a Chapter 6 or Review freeze must be bound to `published-current` Knowledge.
6. Read the frozen context revision and build/reuse an immutable Impact Index for that exact revision: `py -3 scripts/python/build_impact_index.py --revision <frozen-revision> --trusted-ref refs/heads/main`.
7. Run strict Impact analysis with `py -3 scripts/python/analyze_impact.py --target <path-or-symbol-or-config-pointer> --strict --frozen-context <frozen.json> --output <impact.json>`, then validate frozen-context / impact revision / index lineage with `impact_analysis_handoff.py` before consuming the report.
8. If semantic scope genuinely changes during RED/GREEN/REFACTOR, create a new candidate/decision/freeze revision and a matching revision-bound Impact Index; never silently expand a frozen context.
9. Review must prepare and freeze a separate `consumer=review` context. Never reuse a Chapter 6 freeze as Review context.
10. After implementation evidence is stable, run `chapter6_knowledge.py --task-id <id> --path <reviewed-resource>` only for resources actually reviewed in this task. With no reviewed resource path, the explicit-reviewed record must skip instead of inventing associations.
11. `chapter6_knowledge.py` must deterministically rebuild `task-resource-links.json` from the current Project Health snapshot before any semantic explanation is consumed. When explanation materially helps, `--semantic --llm-backend <codex-cli|openai-api>` is an explicit opt-in; every returned resource path, JSON pointer, scene node, and asset binding must resolve to reconstructed snapshot evidence, and generated prose remains non-authoritative.
12. Project Health runtime evidence is task-scoped evidence only. `workspace` verification must not be promoted to `main` runtime acceptance; formal main evidence requires the guarded main-mode verifier and a non-empty passing GdUnit report.

Regeneration invariant:

- `.agents/skills/workflow-chapter2-*`, `workflow-chapter4-*`, `workflow-chapter5-*`, and `workflow-chapter6-*` are regenerated through `scripts/python/update_workflow_chapter_skills.py`; its Knowledge/Impact overlay is idempotent and must remain aligned with this root contract.
<!-- KNOWLEDGE_IMPACT_WORKFLOW_CONTRACT_END -->
'''


def patch_text(text: str) -> str:
    while BEGIN in text and END in text:
        start = text.index(BEGIN)
        finish = text.index(END, start) + len(END)
        text = text[:start].rstrip() + "\n\n" + text[finish:].lstrip("\n")
    anchor = "\n## 2. Phase 0"
    index = text.find(anchor)
    if index < 0:
        raise ValueError("Chapter 2 anchor not found in workflow.md")
    return text[:index].rstrip() + "\n\n" + BLOCK.rstrip() + "\n\n" + text[index + 1:]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    path = args.repo_root.resolve() / "workflow.md"
    original = path.read_text(encoding="utf-8")
    updated = patch_text(original)
    if args.check:
        if original != updated:
            print("workflow.md Knowledge/Impact contract is not current")
            return 1
        print("workflow.md Knowledge/Impact contract is current")
        return 0
    if original == updated:
        print("workflow.md already current")
        return 0
    path.write_text(updated, encoding="utf-8", newline="\n")
    print("workflow.md updated")
    return 0


if __name__ == "__main__": raise SystemExit(main())
