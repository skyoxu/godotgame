#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_module(name: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class WorkflowChapterSkillTests(unittest.TestCase):
    def test_chapter3_to_7_skills_should_reference_formal_component_routing_preferences(self) -> None:
        updater = _load_module("update_workflow_chapter_skills_for_component_routing", "scripts/python/update_workflow_chapter_skills.py")

        for name, cfg in updater.SKILLS.items():
            if cfg["chapter"] not in {"3", "4", "5", "6", "7"}:
                continue
            with self.subTest(skill=name):
                text = updater.skill_markdown(name, cfg)
                self.assertIn("docs/workflows/chapter3-7-component-routing.md", text)
                self.assertIn("Godot Node/Scene Component", text)
                self.assertIn("not an ECS component", text)
                self.assertIn("Game.Core", text)

    def test_chapter3_skill_should_preserve_chinese_interaction_prompt_guidance(self) -> None:
        updater = _load_module("update_workflow_chapter_skills_for_extra_sections", "scripts/python/update_workflow_chapter_skills.py")

        cfg = updater.SKILLS["workflow-chapter3-task-triplet-baseline"]
        text = updater.skill_markdown("workflow-chapter3-task-triplet-baseline", cfg)

        self.assertIn("## \u7528\u6237\u4ea4\u4e92\u6587\u6848\u8981\u6c42", text)
        self.assertIn("\u9762\u5411\u7528\u6237\u7684\u63d0\u95ee\u5fc5\u987b\u4f7f\u7528\u4e2d\u6587", text)
        self.assertIn("\u6280\u672f\u547d\u4ee4\u3001\u6587\u4ef6\u8def\u5f84\u3001\u811a\u672c\u540d\u4fdd\u6301\u82f1\u6587\u539f\u6587", text)

    def test_chapter2_skill_should_preserve_bootstrap_extensions_when_regenerated(self) -> None:
        updater = _load_module("update_workflow_chapter_skills_for_chapter2_extensions", "scripts/python/update_workflow_chapter_skills.py")

        cfg = updater.SKILLS["workflow-chapter2-repository-bootstrap"]
        text = updater.skill_markdown("workflow-chapter2-repository-bootstrap", cfg)

        self.assertIn("## Highest Encoding Rule", text)
        self.assertIn("\u6240\u6709\u4e2d\u6587\u6587\u6863\u8bfb\u5199\u5fc5\u987b\u901a\u8fc7 Python", text)
        self.assertIn("## Game Type Classification Prompt", text)
        self.assertIn("codex exec", text)
        self.assertIn("## \u7528\u6237\u4ea4\u4e92\u6587\u6848\u8981\u6c42", text)
        self.assertIn("project-health", text)

    def test_chapter2_workflow_source_should_preserve_repository_specific_extension(self) -> None:
        updater = _load_module("update_workflow_chapter_skills_for_chapter2_source_extension", "scripts/python/update_workflow_chapter_skills.py")

        text = updater.workflow_chapter_summary(REPO_ROOT, "2")

        self.assertIn("## Repository-Specific Extension", text)
        self.assertIn("After Chapter 2 initialization, create `docs/prd`, `docs/gdd`, and `docs/prototypes`.", text)
        self.assertIn("Classify the second answer with `codex exec`", text)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
