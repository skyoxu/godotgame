# Project Health: Knowledge + Impact

`serve-project-health` serves the existing health dashboard and the loopback-only `/knowledge/` investigation page from the same `127.0.0.1` process.

A fresh template intentionally has no business task records. Empty task, mapping, runtime, and generated Knowledge state is valid; do not seed it with sibling-repository examples.

## Snapshot model

In a Git-backed repository, **Scan local main** reads `refs/heads/main` without checking it out. Search results, task/task-view joins, source viewing, image preview, Impact exploration, static Godot navigation, and main-mode runtime eligibility all bind to that scanned revision.

The page surfaces the scanned revision and warns when local main moves after the scan. Re-scan before relying on stale investigation evidence.

Non-Git temporary fixtures fall back to a directory snapshot so deterministic tests can remain self-contained. That fallback is not a substitute for local-main evidence in a real repository.

The bounded scan manifest includes UTF-8 text sources plus supported assets. Images can be previewed only when their bytes still match the scanned manifest. Large assets remain outside the preview budget.

## Knowledge and Impact

The page provides:

- consumer-aware Knowledge lookup for `repository-session`, `chapter4`, `chapter5`, `chapter6`, and `review`;
- deterministic query aliases;
- actionable result groups for Tasks, Configuration, Code, and Tests, plus lower-confidence evidence;
- configured GDD supplements;
- exploratory and strict Impact probes;
- source viewing bound to the scan revision.

Locator rank and text-reference Impact edges are evidence only. They do not become semantic acceptance or confirmed dependencies automatically.

Formal Chapter 6 and Review handoffs still require candidate preparation, direct source re-reading, explicit accept/reject decisions, a frozen context, strict Impact output, and lineage validation. The browser page is an investigation surface, not a replacement for those contracts.

## Task and Godot navigation

When task data exists, `tasks.json` is treated as the task SSOT and enrichment views are joined by task id. The task table supports pagination, status/Godot filtering, page selection, selected runtime verification, eligible runtime verification, and all-gameplay runtime auditing.

Task detail can expose:

- reviewed task-to-scene mappings;
- scene nodes and properties;
- real scene script attachments;
- configured code witnesses;
- code/config/resource reference chains;
- exact JSON fields and configured JSON pointers;
- assets and image previews;
- task-scoped test references and suggested test commands;
- unresolved references and explicit navigation limitations.

A configured mapping is not enough to claim `static_attached`. The scene must actually attach the declared script to the declared node and the configured witness must exist in that production script. Test references to a scene are only candidates.

## Resource reconstruction and semantic explanation

`generate_knowledge_links.py` deterministically reconstructs task-to-config/asset/scene/code associations from the current Project Health snapshot. It never seeds product identities or upgrades filename similarity into authority.

For an implemented task, the normal capture entry is:

```powershell
py -3 scripts/python/chapter6_knowledge.py --task-id <id> --path <reviewed-resource>
```

The `--path` values are explicit reviewed workspace resources. If no reviewed resource path is supplied, that explicit-reviewed record is skipped rather than invented. The command still rebuilds snapshot-derived `docs/knowledge/generated/task-resource-links.json` for the selected task.

When developer-facing semantic explanation is useful, opt in explicitly:

```powershell
py -3 scripts/python/chapter6_knowledge.py --task-id <id> --path <reviewed-resource> --semantic --llm-backend codex-cli
```

`openai-api` is also supported when that backend is explicitly configured. Semantic output is written to `docs/knowledge/generated/task-<id>-semantic.json` only after validation. The model may explain only evidence already reconstructed for the task:

- configuration parameters must use exact JSON pointers that exist in the scanned file;
- asset bindings must use exact source/line pairs from static evidence;
- scene bindings must use exact node-path/line pairs from parsed scene evidence;
- unknown paths, pointers, nodes, or bindings reject the semantic output;
- generated prose never proves runtime observation or business authority.

The 127 page renders exact reviewed/confirmed configuration pointers separately from generated semantic suggestions. Generated semantic evidence may provide blue suggested-field highlighting only when the JSON pointer exists. Yellow confirmed highlighting remains reserved for reviewed/static-confirmed evidence.

## Runtime verification

Runtime eligibility means only that the scanned task evidence contains a real, existing task-scoped `Tests.Godot/**` reference. It is not acceptance.

Main-mode verification:

1. confirms the scan still represents local main;
2. creates an immutable `git archive` snapshot of that revision;
3. executes only the selected task-scoped GdUnit refs inside the isolated snapshot;
4. requires a non-empty clean GdUnit report;
5. verifies input hashes after execution;
6. records `runtime_verified` only when the scan/main/input lineage remains stable.

Workspace-mode verification uses a separate bounded workspace snapshot and can produce `workspace_verified`, but it must never be promoted to main acceptance.

**Audit all gameplay tasks** includes gameplay-view tasks even when they have no executable task-scoped GdUnit reference. Those tasks are recorded as `runtime_unverified`; the verifier never falls back to an unrelated full test suite to manufacture a green result.

## Local security boundaries

- bind only `127.0.0.1`;
- reject unexpected `Host` headers;
- write operations require exact same-origin `Origin` plus an in-memory session token;
- JSON request bodies are bounded;
- scan/config/runtime writes share a non-blocking operation lock and the page visibly locks while a write operation is active;
- source and image reads are restricted to the scanned manifest;
- image preview has an explicit size/type boundary;
- no arbitrary command execution endpoint exists;
- the only runtime command path is the repository-owned, task-scoped GdUnit verifier.

## Configuration

The structured editor writes `scripts/python/project_health_knowledge_config.json` when the operator chooses to save it. The reusable schema supports:

- `source_path_bindings` and the derived `source_paths`;
- `gdd_paths`;
- reviewed `task_scene_bindings`;
- deterministic `query_aliases`;
- bounded text/asset limits and result limits.

Saving configuration does not silently alter business data. Re-scan local main to apply the configuration to investigation results.
