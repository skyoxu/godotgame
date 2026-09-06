#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_DIR = REPO_ROOT / "examples" / "taskmaster"
_TRIPLET_ENV = {
    "SC_TASKMASTER_TASKS_JSON_PATH": "tasks.json",
    "SC_TASKMASTER_TASKS_BACK_PATH": "tasks_back.json",
    "SC_TASKMASTER_TASKS_GAMEPLAY_PATH": "tasks_gameplay.json",
}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _example_triplet() -> tuple[dict, list, list]:
    return (
        _read_json(EXAMPLES_DIR / "tasks.json"),
        _read_json(EXAMPLES_DIR / "tasks_back.json"),
        _read_json(EXAMPLES_DIR / "tasks_gameplay.json"),
    )


def _inject_task1(tasks_json: dict, tasks_back: list, tasks_gameplay: list) -> None:
    master = (tasks_json.get("master") or {}).get("tasks") or []
    if not any(str(t.get("id")) == "1" for t in master if isinstance(t, dict)):
        master.insert(0, {
            "id": 1,
            "title": "Template Task1 evidence gate demo",
            "status": "in-progress",
            "adrRefs": ["ADR-0031", "ADR-0011"],
            "archRefs": ["CH07"],
            "overlay": "docs/architecture/overlays/PRD-Guild-Manager/08/ACCEPTANCE_CHECKLIST.md",
        })
    if not any(isinstance(t, dict) and t.get("taskmaster_id") == 1 for t in tasks_back):
        tasks_back.insert(0, {
            "id": "T1-back",
            "taskmaster_id": 1,
            "acceptance": [
                "ACC:T1.1 template headless evidence. Refs: Tests.Godot/tests/Adapters/Config/test_settings_config_utf8.gd"
            ],
            "test_refs": [
                "Game.Core.Tests/Tasks/Task1EnvironmentEvidencePersistenceTests.cs",
                "Game.Core.Tests/Tasks/Task1WindowsPlatformGateTests.cs",
                "Game.Core.Tests/Tasks/Task1ToolchainVersionChecksTests.cs",
                "Tests.Godot/tests/Adapters/Config/test_settings_config_utf8.gd",
            ],
        })
    if not any(isinstance(t, dict) and t.get("taskmaster_id") == 1 for t in tasks_gameplay):
        tasks_gameplay.insert(0, {
            "id": "T1-gameplay",
            "taskmaster_id": 1,
            "acceptance": [
                "ACC:T1.2 template gd ref. Refs: Tests.Godot/tests/Adapters/Config/test_settings_config_utf8.gd"
            ],
            "test_refs": ["Tests.Godot/tests/Adapters/Config/test_settings_config_utf8.gd"],
        })
@contextmanager
def staged_taskmaster_triplet(*, include_task1: bool = False) -> Iterator[Path]:
    previous_env = {key: os.environ.get(key) for key in _TRIPLET_ENV}
    with tempfile.TemporaryDirectory(prefix="sc-taskmaster-fixture-") as td:
        taskmaster_dir = Path(td).resolve()
        try:
            tasks_json, tasks_back, tasks_gameplay = _example_triplet()
            if include_task1:
                _inject_task1(tasks_json, tasks_back, tasks_gameplay)
            _write_json(taskmaster_dir / "tasks.json", tasks_json)
            _write_json(taskmaster_dir / "tasks_back.json", tasks_back)
            _write_json(taskmaster_dir / "tasks_gameplay.json", tasks_gameplay)
            for key, filename in _TRIPLET_ENV.items():
                os.environ[key] = str(taskmaster_dir / filename)
            yield taskmaster_dir
        finally:
            for key, value in previous_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
