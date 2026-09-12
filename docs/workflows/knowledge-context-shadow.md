# Knowledge Context Shadow Preflight

The locator is observe-only and never replaces direct repository authority.

```powershell
py -3 scripts/python/prepare_knowledge_context.py --consumer chapter4 --query "<intent>" --output logs/ci/knowledge-context/chapter4.json
py -3 scripts/python/prepare_knowledge_context.py --consumer chapter5 --task-id <id> --query "<task acceptance>" --output logs/ci/knowledge-context/chapter5-<id>.json
py -3 scripts/python/prepare_knowledge_context.py --consumer chapter6 --task-id <id> --query "<implementation intent>" --output logs/ci/knowledge-context/chapter6-<id>.json
```

Ranking is only candidate evidence. Re-read candidate source files directly before deciding acceptance.
