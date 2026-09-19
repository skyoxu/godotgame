# Knowledge Context Decision And Freeze Contract

Before Chapter 6 RED, make explicit accept/reject decisions for candidate sources and freeze them.

Decision file example:
```json
{"decisions":[{"path":"docs/example.md","accepted":true,"reason":"authoritative requirement","satisfies":"task intent"}]}
```

```powershell
py -3 scripts/python/freeze_knowledge_context.py --bundle logs/ci/knowledge-context/chapter6-<id>.json --decisions logs/ci/knowledge-context/chapter6-<id>.decisions.json --output logs/ci/knowledge-context/chapter6-<id>.frozen.json
py -3 scripts/python/analyze_impact.py --target <path-or-symbol> --strict --frozen-context logs/ci/knowledge-context/chapter6-<id>.frozen.json --output logs/ci/impact/<id>.json
py -3 scripts/python/impact_analysis_handoff.py --repo-root . --consumer chapter6 --task-id <id> --frozen-context logs/ci/knowledge-context/chapter6-<id>.frozen.json --impact-report logs/ci/impact/<id>.json
```

The strict analyzer publishes a sibling `run-manifest.v1.json` beside the Impact report. Formal Chapter 6 / Review handoff consumes both artifacts and revalidates the actual report bytes SHA, repository-relative path, revision, and status. Missing, moved, copied-without-manifest, or tampered reports fail closed.

Review uses `consumer=review` and a separate freeze. Never relabel a Chapter 6 context as Review.
