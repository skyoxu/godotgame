#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PYTHON_DIR = REPO_ROOT / "scripts" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


def _load_module(name: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PrototypeWorkflowRouterTests(unittest.TestCase):
    def test_template_defaults_should_fill_optional_fields(self) -> None:
        module = _load_module("prototype_workflow_router_defaults", "scripts/python/run_prototype_workflow.py")
        content = """# 原型：combat-loop

- 假设
- <验证战斗循环是否值得继续>

## 核心玩家幻想
- <第一分钟内感受到战斗节奏>

## 最小可玩循环
- <进入战斗，攻击一次，看到受击反馈>

## 成功标准
- <玩家能完成一次最小循环>
"""
        parsed = module.parse_template_content(content)
        normalized = module.normalize_prototype_payload(parsed, today="2026-04-21")

        self.assertEqual("combat-loop", normalized["slug"])
        self.assertEqual("active", normalized["status"])
        self.assertEqual("operator", normalized["owner"])
        self.assertEqual("2026-04-21", normalized["date"])
        self.assertEqual(["none yet"], normalized["related_formal_task_ids"])
        self.assertEqual(["TBD"], normalized["scope_in"])
        self.assertEqual(["TBD"], normalized["scope_out"])
        self.assertEqual("pending", normalized["decision"])

    def test_template_missing_required_fields_should_block_progress(self) -> None:
        module = _load_module("prototype_workflow_router_required", "scripts/python/run_prototype_workflow.py")
        content = """# 原型：combat-loop

## 假设
- <验证战斗循环是否值得继续>
"""
        parsed = module.parse_template_content(content)
        normalized = module.normalize_prototype_payload(parsed, today="2026-04-21")
        missing = module.required_field_names(normalized)

        self.assertIn("core_player_fantasy", missing)
        self.assertIn("minimum_playable_loop", missing)
        self.assertIn("success_criteria", missing)

    def test_collecting_answers_without_file_should_require_required_fields(self) -> None:
        module = _load_module("prototype_workflow_router_questions", "scripts/python/run_prototype_workflow.py")
        questions = module.required_questions_for_missing_payload({})
        ids = [item["id"] for item in questions]

        self.assertIn("slug", ids)
        self.assertIn("hypothesis", ids)
        self.assertIn("core_player_fantasy", ids)
        self.assertIn("minimum_playable_loop", ids)
        self.assertIn("success_criteria", ids)

    def test_active_state_should_round_trip(self) -> None:
        module = _load_module("prototype_workflow_router_state", "scripts/python/run_prototype_workflow.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = {
                "status": "needs-confirmation",
                "prototype": {"slug": "combat-loop", "day": 1},
                "missing_required_fields": [],
            }
            path = module.write_active_state(repo_root=root, slug="combat-loop", payload=state)
            loaded = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(state["status"], loaded["status"])
        self.assertEqual("combat-loop", loaded["prototype"]["slug"])

    def test_record_render_should_include_template_fields(self) -> None:
        module = _load_module("prototype_workflow_router_record", "scripts/python/run_prototype_tdd.py")
        rendered = module._render_record(
            slug="combat-loop",
            owner="operator",
            related_task_ids=["none yet"],
            hypothesis="验证战斗循环是否值得继续",
            core_player_fantasy="第一分钟内感受到战斗节奏",
            minimum_playable_loop="进入战斗，攻击一次，看到受击反馈",
            scope_in=["移动", "攻击"],
            scope_out=["正式任务"],
            success_criteria=["玩家能完成一次最小循环"],
            promote_signals=["试玩后仍值得继续"],
            archive_signals=["方向有价值但不够强"],
            discard_signals=["循环无趣且不清晰"],
            evidence=["Game.Godot/Prototypes/combat-loop/CombatLoopPrototype.tscn"],
            decision="pending",
            next_step="进入 Day 2 场景脚手架",
        )

        self.assertIn("## Core Player Fantasy", rendered)
        self.assertIn("## Minimum Playable Loop", rendered)
        self.assertIn("## Promote Signals", rendered)
        self.assertIn("## Archive Signals", rendered)
        self.assertIn("## Discard Signals", rendered)

    def test_dev_cli_should_expose_prototype_workflow_entry(self) -> None:
        builders = _load_module("dev_cli_builders_module_for_proto_workflow", "scripts/python/dev_cli_builders.py")
        dev_cli = _load_module("dev_cli_module_for_proto_workflow", "scripts/python/dev_cli.py")
        parser = dev_cli.build_parser()
        args = parser.parse_args(["run-prototype-workflow", "--prototype-file", "docs/prototypes/sample.md"])
        cmd = builders.build_run_prototype_workflow_cmd(args)

        self.assertEqual("run-prototype-workflow", args.cmd)
        self.assertIn("scripts/python/run_prototype_workflow.py", cmd)
        self.assertIn("docs/prototypes/sample.md", cmd)


if __name__ == "__main__":
    unittest.main()
