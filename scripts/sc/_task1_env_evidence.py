#!/usr/bin/env python3
"""
Backward-compatible Task 1 environment evidence wrapper.

The canonical implementation lives in `_env_evidence_preflight.py`.
"""

from __future__ import annotations

from pathlib import Path

from _env_evidence_preflight import step_env_evidence_preflight
from _step_result import StepResult


def step_task1_env_evidence(out_dir: Path, *, godot_bin: str | None) -> StepResult:
    return step_env_evidence_preflight(out_dir, godot_bin=godot_bin, task_id='1')
