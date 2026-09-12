# Project Resource Knowledge

This directory is the human-reviewable project resource knowledge layer for repositories created from this template.

- It may describe configuration, assets, scenes, code and tests discovered during project work.
- It is **not** a second source of truth. Taskmaster, PRD/GDD, ADR/Base/Overlay, Contracts and source code remain authoritative.
- A fresh template intentionally contains no business task records. `generated/` remains empty until a real project captures task-scoped knowledge.
- Machine publication state belongs under `knowledge/**`; local run evidence belongs under `logs/**`.
- Do not copy sibling-repository task IDs, product IDs, asset paths, hashes or gameplay fixtures into this template.

## Knowledge Control Plane

The reusable control plane has four deterministic layers:

1. `knowledge/snapshots/repository-source-snapshot.v1.json` binds repository sources to a trusted Git ref and commit.
2. `knowledge/catalogs/repository-knowledge-catalog.v1.json` classifies bounded repository authority into modules with source hashes and anchors.
3. `knowledge/projections/consumer-projections.v1.json` applies `knowledge/policies/consumer-policies.v1.json` to `repository-session`, Chapter 4, Chapter 5, Chapter 6 and Review.
4. `knowledge/indexes/current.json` points at a hash-bound published generation under `knowledge/indexes/generations/<generation-id>/`; `last-known-good.json` supports controlled recovery.

Build without publishing:

```powershell
py -3 scripts/python/build_knowledge_catalog.py --repository-root . --write
```

Publish the current local `main` generation only after the Knowledge control-plane scripts, policies and evaluation suite are committed and clean:

```powershell
py -3 scripts/python/publish_knowledge_catalog.py --repository-root . --publish
py -3 scripts/python/publish_knowledge_catalog.py --repository-root . --check
```

Restore the last hash-validated generation when the current pointer is damaged or a newly attempted generation is not usable:

```powershell
py -3 scripts/python/publish_knowledge_catalog.py --repository-root . --restore-lkg
```

The template ships an empty deterministic query evaluation suite at `knowledge/evaluation/queries.v1.json`. This means the control plane itself can be published without inventing product expectations. A business repository should add its own query cases before treating evaluation coverage as evidence about that product.

Browser investigation may fall back to an ephemeral policy-aware catalog so `/knowledge/` stays useful before publication. Formal Chapter 6 and Review context preparation does **not** accept that fallback: it requires `publication_state = published-current` before a candidate bundle may be frozen.
