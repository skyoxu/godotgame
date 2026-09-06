from __future__ import annotations

import os
from pathlib import Path

_TRIPLET_FILES = ("tasks.json", "tasks_back.json", "tasks_gameplay.json")
_TRIPLET_ENV_KEYS = (
    "SC_TASKMASTER_TASKS_JSON_PATH",
    "SC_TASKMASTER_TASKS_BACK_PATH",
    "SC_TASKMASTER_TASKS_GAMEPLAY_PATH",
)


def _complete_triplet_dir(base_dir: Path) -> Path | None:
    if all((base_dir / name).exists() for name in _TRIPLET_FILES):
        return base_dir
    return None


def _resolve_override_path(root: Path, env_key: str) -> Path | None:
    raw = str(os.environ.get(env_key) or "").strip()
    if not raw:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    return candidate


def resolve_default_task_triplet_paths(root: Path) -> tuple[Path, Path, Path]:
    overrides = tuple(_resolve_override_path(root, key) for key in _TRIPLET_ENV_KEYS)
    if any(path is not None for path in overrides):
        default_base_dir = _complete_triplet_dir(root / ".taskmaster" / "tasks")
        if default_base_dir is None:
            default_base_dir = _complete_triplet_dir(root / "examples" / "taskmaster")
        if default_base_dir is None:
            default_base_dir = root / ".taskmaster" / "tasks"
        default_paths = tuple(default_base_dir / name for name in _TRIPLET_FILES)
        return tuple(path or default_paths[idx] for idx, path in enumerate(overrides))

    base_dir = _complete_triplet_dir(root / ".taskmaster" / "tasks")
    if base_dir is None:
        base_dir = _complete_triplet_dir(root / "examples" / "taskmaster")
    if base_dir is None:
        base_dir = root / ".taskmaster" / "tasks"
    return tuple(base_dir / name for name in _TRIPLET_FILES)
