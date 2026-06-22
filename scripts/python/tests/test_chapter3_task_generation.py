#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import contextlib
import io
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


class Chapter3TaskGenerationTests(unittest.TestCase):
    def test_requirement_extraction_should_skip_reference_only_blocks(self) -> None:
        mod = _load_module("extract_requirement_anchors_for_noise_test", "scripts/python/extract_requirement_anchors.py")

        self.assertFalse(mod.is_requirement_like("- docs/gdd/ui-gdd-flow.md ADR-Refs:"))
        self.assertFalse(mod.is_requirement_like("- Game.Core.Tests/Tasks/Task1WindowsPlatformGateTests.cs"))
        self.assertFalse(mod.is_requirement_like("- T42 `Independent performance gates workflow`"))
        self.assertTrue(mod.is_requirement_like("- Startup smoke must verify all required autoloads load without startup errors."))

    def test_task_intents_should_split_large_source_groups_by_topic_and_size(self) -> None:
        mod = _load_module("normalize_task_intents_for_split_test", "scripts/python/normalize_task_intents.py")
        anchors = []
        for idx in range(1, 13):
            anchors.append(
                {
                    "requirement_id": f"REQ-COMBAT-{idx:04d}",
                    "source_path": "docs/gdd/ui-gdd-flow.md",
                    "line": idx,
                    "kind": "gdd",
                    "priority": "P1",
                    "text": f"Combat enemy attack damage targeting requirement {idx} must be implemented.",
                    "refs": [],
                }
            )
        for idx in range(1, 5):
            anchors.append(
                {
                    "requirement_id": f"REQ-UI-{idx:04d}",
                    "source_path": "docs/gdd/ui-gdd-flow.md",
                    "line": 100 + idx,
                    "kind": "gdd",
                    "priority": "P2",
                    "text": f"UI HUD surface display requirement {idx} should be implemented.",
                    "refs": [],
                }
            )

        result = mod.build_intents(
            {
                "schema": "task-generation.requirements-index.v1",
                "anchors": anchors,
            },
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=5,
            split_profile="compact",
        )

        self.assertEqual("task-generation.task-intents.v1", result["schema"])
        self.assertEqual(16, result["source_anchor_count"])
        self.assertEqual(4, result["intent_count"])
        self.assertEqual(
            sorted(anchor["requirement_id"] for anchor in anchors),
            sorted(rid for intent in result["intents"] for rid in intent["requirement_ids"]),
        )
        self.assertLessEqual(max(intent["covered_anchor_count"] for intent in result["intents"]), 5)
        self.assertIn("combat-loop", {intent["topic"] for intent in result["intents"]})
        self.assertIn("ui-hud", {intent["topic"] for intent in result["intents"]})
        self.assertTrue(any(intent["title"].startswith("Implement ") for intent in result["intents"]))
        self.assertTrue(any(intent["title"].startswith("Create ") for intent in result["intents"]))
        self.assertTrue(any("Red:" in " ".join(intent["test_strategy"]) for intent in result["intents"]))
        self.assertTrue(any(intent["depends_on"] for intent in result["intents"]))

    def test_task_intent_titles_should_deprioritize_traceability_noise(self) -> None:
        mod = _load_module("normalize_task_intents_for_title_noise_test", "scripts/python/normalize_task_intents.py")
        result = mod.build_intents(
            {
                "schema": "task-generation.requirements-index.v1",
                "anchors": [
                    {
                        "requirement_id": "REQ-NOISE-0001",
                        "source_path": "docs/gdd/a.md",
                        "line": 1,
                        "kind": "gdd",
                        "priority": "P2",
                        "text": "- ADR-0033 Test-Refs: Default save slot must gate Continue by valid metadata.",
                        "refs": [],
                    },
                    {
                        "requirement_id": "REQ-NOISE-0002",
                        "source_path": "docs/gdd/a.md",
                        "line": 2,
                        "kind": "gdd",
                        "priority": "P2",
                        "text": "- Default save slot must gate Continue by valid metadata.",
                        "refs": [],
                    },
                ],
            },
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
        )

        title = result["intents"][0]["title"].lower()
        self.assertIn("save", title)
        self.assertNotIn("test", title)
        self.assertNotIn("adr", title)

    def test_task_intent_titles_should_fallback_to_source_name_not_generic_topic(self) -> None:
        mod = _load_module("normalize_task_intents_for_source_fallback_test", "scripts/python/normalize_task_intents.py")
        result = mod.build_intents(
            {
                "schema": "task-generation.requirements-index.v1",
                "anchors": [
                    {
                        "requirement_id": "REQ-SOURCE-0001",
                        "source_path": "docs/gdd/m1-playable-setup.md",
                        "line": 1,
                        "kind": "acceptance",
                        "priority": "P2",
                        "text": "- ADR-0033 Test-Refs: tests must pass.",
                        "refs": [],
                    },
                ],
            },
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
        )

        title = result["intents"][0]["title"].lower()
        self.assertIn("playable", title)
        self.assertNotEqual("add test coverage for testing", title)

    def test_balanced_split_profile_should_split_gameplay_groups_more_finely_than_compact(self) -> None:
        mod = _load_module("normalize_task_intents_for_profile_test", "scripts/python/normalize_task_intents.py")
        anchors = [
            {
                "requirement_id": f"REQ-RUN-{idx:04d}",
                "source_path": "docs/gdd/run-loop.md",
                "line": idx,
                "kind": "gdd",
                "priority": "P2",
                "text": f"Run state turn cycle win lose terminal behavior requirement {idx} must be implemented.",
                "refs": [],
            }
            for idx in range(1, 9)
        ]

        compact = mod.build_intents(
            {"schema": "task-generation.requirements-index.v1", "anchors": anchors},
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
            split_profile="compact",
        )
        balanced = mod.build_intents(
            {"schema": "task-generation.requirements-index.v1", "anchors": anchors},
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
            split_profile="balanced",
        )

        self.assertEqual(1, compact["intent_count"])
        self.assertEqual(2, balanced["intent_count"])
        self.assertEqual(
            sorted(anchor["requirement_id"] for anchor in anchors),
            sorted(rid for intent in balanced["intents"] for rid in intent["requirement_ids"]),
        )

    def test_split_titles_should_put_part_number_before_shared_focus(self) -> None:
        mod = _load_module("normalize_task_intents_for_title_part_test", "scripts/python/normalize_task_intents.py")
        anchors = [
            {
                "requirement_id": f"REQ-GATE-{idx:04d}",
                "source_path": "docs/gdd/audit.md",
                "line": idx,
                "kind": "gdd",
                "priority": "P2",
                "text": f"Validation gate closure deterministic state requirement {idx} must be visible.",
                "refs": [],
            }
            for idx in range(1, 9)
        ]

        result = mod.build_intents(
            {"schema": "task-generation.requirements-index.v1", "anchors": anchors},
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
            split_profile="balanced",
        )

        titles = [intent["title"] for intent in result["intents"]]
        self.assertTrue(any("part 1 validation" in title.lower() for title in titles))
        self.assertTrue(any("part 2 validation" in title.lower() for title in titles))

    def test_duplicate_titles_should_be_disambiguated_with_source_focus(self) -> None:
        mod = _load_module("normalize_task_intents_for_title_disambiguation_test", "scripts/python/normalize_task_intents.py")
        anchors = [
            {
                "requirement_id": "REQ-COPY-0001",
                "source_path": "docs/prd/narrative-style-guide.md",
                "line": 10,
                "kind": "prd",
                "priority": "P2",
                "text": "Screen specs must define visible copy.",
                "refs": [],
            },
            {
                "requirement_id": "REQ-COPY-0002",
                "source_path": "docs/prd/playtest-script.md",
                "line": 10,
                "kind": "prd",
                "priority": "P2",
                "text": "Screen specs must define visible copy.",
                "refs": [],
            },
        ]

        result = mod.build_intents(
            {"schema": "task-generation.requirements-index.v1", "anchors": anchors},
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
            split_profile="balanced",
        )

        titles = [intent["title"] for intent in result["intents"]]
        self.assertEqual(len(titles), len(set(titles)))

    def test_duplicate_single_source_titles_should_get_line_qualifier(self) -> None:
        mod = _load_module("normalize_task_intents_for_line_disambiguation_test", "scripts/python/normalize_task_intents.py")
        anchors = [
            {
                "requirement_id": "REQ-LINE-0001",
                "source_path": "docs/prd/main-prd.md",
                "line": 13,
                "kind": "requirement",
                "priority": "P2",
                "text": "The product name must be visible.",
                "refs": [],
            },
            {
                "requirement_id": "REQ-LINE-0002",
                "source_path": "docs/prd/main-prd.md",
                "line": 147,
                "kind": "prd",
                "priority": "P2",
                "text": "The product name must be visible.",
                "refs": [],
            },
        ]

        result = mod.build_intents(
            {"schema": "task-generation.requirements-index.v1", "anchors": anchors},
            mode="init",
            id_prefix="TST",
            max_anchors_per_intent=8,
            split_profile="balanced",
        )

        titles = [intent["title"] for intent in result["intents"]]
        self.assertTrue(any("line 13" in title for title in titles))
        self.assertTrue(any("line 147" in title for title in titles))

    def test_intent_titles_should_collapse_repeated_adjacent_words(self) -> None:
        mod = _load_module("normalize_task_intents_for_repeated_word_test", "scripts/python/normalize_task_intents.py")

        self.assertEqual("Implement newrouge", mod.intent_title("newrouge-0001", "newrouge"))
        self.assertEqual("Document playable setup", mod.collapse_repeated_words("Document playable setup playable setup"))

    def test_candidate_generation_should_prefer_task_intents_when_present(self) -> None:
        mod = _load_module("generate_task_candidates_for_intent_test", "scripts/python/generate_task_candidates_from_sources.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_dir = root / "logs" / "ci" / "task-generation"
            out_dir.mkdir(parents=True)
            (out_dir / "requirements.index.json").write_text(
                json.dumps(
                    {
                        "schema": "task-generation.requirements-index.v1",
                        "anchors": [
                            {
                                "requirement_id": "REQ-OLD-0001",
                                "source_path": "docs/prd/a.md",
                                "line": 1,
                                "kind": "prd",
                                "priority": "P2",
                                "text": "Old source grouping should not be used.",
                                "refs": [],
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (out_dir / "task-intents.normalized.json").write_text(
                json.dumps(
                    {
                        "schema": "task-generation.task-intents.v1",
                        "intents": [
                            {
                                "id": "INT-0001",
                                "title": "Implement combat loop",
                                "description": "Combat loop intent.",
                                "details": ["Do combat work."],
                                "priority": "P1",
                                "layer": "core",
                                "owner": "gameplay",
                                "labels": ["combat-loop"],
                                "requirement_ids": ["REQ-NEW-0001", "REQ-NEW-0002"],
                                "source_refs": ["docs/gdd/a.md:10", "docs/gdd/a.md:11"],
                                "covered_anchor_count": 2,
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["--repo-root", str(root), "--mode", "init", "--id-prefix", "GEN"])
            payload = json.loads((out_dir / "task-candidates.normalized.json").read_text(encoding="utf-8"))

        self.assertEqual(0, rc)
        self.assertEqual("task-generation.task-intents.v1", payload["source_schema"])
        self.assertEqual(1, payload["candidate_count"])
        self.assertEqual("INT-0001", payload["candidates"][0]["id"])
        self.assertEqual(["REQ-NEW-0001", "REQ-NEW-0002"], payload["candidates"][0]["requirement_ids"])

    def test_chapter3_should_preserve_gdd_ui_ux_seed_through_candidates_and_triplet_patch(self) -> None:
        extract_mod = _load_module("extract_requirement_anchors_for_ui_ux_seed_test", "scripts/python/extract_requirement_anchors.py")
        intent_mod = _load_module("normalize_task_intents_for_ui_ux_seed_test", "scripts/python/normalize_task_intents.py")
        candidate_mod = _load_module("generate_task_candidates_for_ui_ux_seed_test", "scripts/python/generate_task_candidates_from_sources.py")
        compile_mod = _load_module("compile_task_triplet_for_ui_ux_seed_test", "scripts/python/compile_task_triplet.py")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gdd = root / "docs" / "gdd" / "new-game-gdd.md"
            out_dir = root / "logs" / "ci" / "task-generation"
            gdd.parent.mkdir(parents=True)
            out_dir.mkdir(parents=True)
            gdd.write_text(
                """# New Game GDD

## UI/UX Direction

- Visual mood: tactical roguelike, readable under pressure.
- Target platforms/resolutions: Windows desktop, 1280x720 and 1920x1080.

## Screen Inventory

| Screen | Purpose | Entry | Exit | Priority |
| --- | --- | --- | --- | --- |
| Gameplay HUD | Show health, deck, gold, and turn state | Run scene | Pause or result | P1 |

## HUD Priority

| Data | Priority | Always Visible | Contextual | Feedback Only |
| --- | --- | --- | --- | --- |
| Health | P1 | yes | no | no |

## Input Model

| Action | Keyboard/Mouse | Controller | UI Surface |
| --- | --- | --- | --- |
| Confirm reward | Enter / click | A | Reward screen |

## Localization Seed

| UI Text Area | Key Prefix | Notes |
| --- | --- | --- |
| Gameplay HUD | ui.hud | Avoid hardcoded player text |

## Accessibility Baseline

| Requirement | Applies To |
| --- | --- |
| Focus visible | menus, reward, settings |
""",
                encoding="utf-8",
            )

            requirements = extract_mod.extract(root, ["docs/gdd/new-game-gdd.md"], "init")
            (out_dir / "requirements.index.json").write_text(json.dumps(requirements, indent=2) + "\n", encoding="utf-8")
            intents = intent_mod.build_intents(
                requirements,
                mode="init",
                id_prefix="INT",
                max_anchors_per_intent=8,
                split_profile="balanced",
            )
            (out_dir / "task-intents.normalized.json").write_text(json.dumps(intents, indent=2) + "\n", encoding="utf-8")
            candidates = candidate_mod.build_candidates_from_intents(intents, "init", "GEN")
            candidate = next(item for item in candidates["candidates"] if item.get("ui_ux_seed"))
            triplet_task = compile_mod.normalize_task(candidate, "gameplay")

        seed = candidate["ui_ux_seed"]
        self.assertTrue(seed["required"])
        self.assertEqual("docs/workflows/ui-ux-implementation-policy.md", seed["policy_ref"])
        self.assertIn("screen_inventory_seed", seed["categories"])
        self.assertIn("hud_priority", seed["categories"])
        self.assertIn("input_model", seed["categories"])
        self.assertIn("localization_seed", seed["categories"])
        self.assertIn("accessibility_baseline", seed["categories"])
        self.assertIn("ui-ux-seed", candidate["labels"])
        self.assertIn("chapter7-input", candidate["labels"])
        self.assertIn("not-chapter6-runnable", candidate["labels"])
        self.assertEqual("deferred", candidate["status"])
        self.assertTrue(any("UI/UX seed" in item for item in candidate["acceptance"]))
        self.assertEqual(seed, triplet_task["ui_ux_seed"])
        self.assertIn("chapter7-input", triplet_task["labels"])
        self.assertIn("not-chapter6-runnable", triplet_task["labels"])
        self.assertEqual("deferred", triplet_task["status"])

    def test_chapter3_ui_ux_seed_should_not_be_dependency_for_runtime_tasks(self) -> None:
        intent_mod = _load_module("normalize_task_intents_for_ui_ux_seed_dependency_test", "scripts/python/normalize_task_intents.py")

        index = {
            "schema": "task-generation.requirements-index.v1",
            "anchors": [
                {
                    "requirement_id": "REQ-UI-0001",
                    "source_path": "docs/gdd/new-game-gdd.md",
                    "line": 10,
                    "kind": "gdd",
                    "priority": "P2",
                    "text": "## Screen Inventory Gameplay HUD shows run state.",
                    "refs": [],
                    "ui_ux_category": "screen_inventory_seed",
                },
                {
                    "requirement_id": "REQ-RUN-0001",
                    "source_path": "docs/gdd/new-game-gdd.md",
                    "line": 20,
                    "kind": "gdd",
                    "priority": "P1",
                    "text": "The player must see run state, health, and turn changes on the HUD.",
                    "refs": [],
                    "ui_ux_category": "",
                },
            ],
        }

        intents = intent_mod.build_intents(index, mode="init", id_prefix="INT", max_anchors_per_intent=8)
        seed = next(item for item in intents["intents"] if item.get("ui_ux_seed"))
        runtime = next(item for item in intents["intents"] if item["id"] != seed["id"])

        self.assertEqual("INT-0001", seed["id"])
        self.assertNotIn(seed["id"], runtime["depends_on"])

    def test_ui_ux_seed_excerpt_should_prefer_content_anchor_over_heading_anchor(self) -> None:
        seed_mod = _load_module("ui_ux_seed_support_excerpt_quality_test", "scripts/python/_ui_ux_seed_support.py")

        seed = seed_mod.build_ui_ux_seed(
            [
                {
                    "source_path": "docs/gdd/new-game-gdd.md",
                    "line": 10,
                    "ui_ux_category": "screen_inventory_seed",
                    "text": "## Screen Inventory",
                },
                {
                    "source_path": "docs/gdd/new-game-gdd.md",
                    "line": 12,
                    "ui_ux_category": "screen_inventory_seed",
                    "text": "| Gameplay HUD | Show health, deck, gold, and turn state | Run scene | Pause or result | P1 |",
                },
            ]
        )

        self.assertEqual(
            "| Gameplay HUD | Show health, deck, gold, and turn state | Run scene | Pause or result | P1 |",
            seed["excerpts"]["screen_inventory_seed"],
        )

    def test_ui_ux_seed_excerpt_should_treat_any_single_markdown_heading_as_heading_only(self) -> None:
        seed_mod = _load_module("ui_ux_seed_support_heading_level_test", "scripts/python/_ui_ux_seed_support.py")

        seed = seed_mod.build_ui_ux_seed(
            [
                {
                    "source_path": "docs/gdd/new-game-gdd.md",
                    "line": 10,
                    "ui_ux_category": "screen_inventory_seed",
                    "text": "### 用户界面和所有主要屏幕清单必须在 Chapter 7 前保留",
                },
                {
                    "source_path": "docs/gdd/new-game-gdd.md",
                    "line": 12,
                    "ui_ux_category": "screen_inventory_seed",
                    "text": "Main menu commands.",
                },
            ]
        )

        self.assertEqual(
            "Main menu commands.",
            seed["excerpts"]["screen_inventory_seed"],
        )

    def test_requirement_extraction_should_capture_bmad_gds_ui_ux_heading_aliases(self) -> None:
        mod = _load_module("extract_requirement_anchors_for_ui_ux_alias_test", "scripts/python/extract_requirement_anchors.py")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gdd = root / "docs" / "gdd" / "alias-gdd.md"
            gdd.parent.mkdir(parents=True)
            gdd.write_text(
                """# Alias GDD

## User Interface

- Main menu should expose Continue, New Run, Settings, and Quit.

## Controls

- Confirm uses Enter or gamepad A.

## Accessibility Controls

- Important feedback must not rely on color only.

## Localization

- UI copy should use the ui.main key prefix.
""",
                encoding="utf-8",
            )

            result = mod.extract(root, ["docs/gdd/alias-gdd.md"], "init")

        categories = {anchor["ui_ux_category"] for anchor in result["anchors"] if anchor.get("ui_ux_category")}
        self.assertIn("screen_inventory_seed", categories)
        self.assertIn("input_model", categories)
        self.assertIn("accessibility_baseline", categories)
        self.assertIn("localization_seed", categories)

    def test_requirement_extraction_should_capture_chinese_ui_ux_heading_aliases(self) -> None:
        mod = _load_module("extract_requirement_anchors_for_ui_ux_chinese_alias_test", "scripts/python/extract_requirement_anchors.py")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gdd = root / "docs" / "gdd" / "zh-gdd.md"
            gdd.parent.mkdir(parents=True)
            gdd.write_text(
                "\n".join(
                    [
                        "# \u4e2d\u6587 GDD",
                        "",
                        "## \u754c\u9762\u8bbe\u8ba1",
                        "",
                        "- \u4e3b\u83dc\u5355\u5fc5\u987b\u63d0\u4f9b\u7ee7\u7eed\u3001\u65b0\u6e38\u620f\u3001\u8bbe\u7f6e\u548c\u9000\u51fa\u5165\u53e3\u3002",
                        "",
                        "## \u8f93\u5165\u63a7\u5236",
                        "",
                        "- \u786e\u8ba4\u64cd\u4f5c\u4f7f\u7528 Enter \u6216\u624b\u67c4 A\u3002",
                        "",
                        "## \u65e0\u969c\u788d",
                        "",
                        "- \u91cd\u8981\u53cd\u9988\u4e0d\u5f97\u53ea\u4f9d\u8d56\u989c\u8272\u3002",
                        "",
                        "## \u672c\u5730\u5316",
                        "",
                        "- UI \u6587\u6848\u5fc5\u987b\u4f7f\u7528 ui.main key prefix\u3002",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = mod.extract(root, ["docs/gdd/zh-gdd.md"], "init")

        categories = {anchor["ui_ux_category"] for anchor in result["anchors"] if anchor.get("ui_ux_category")}
        self.assertIn("screen_inventory_seed", categories)
        self.assertIn("input_model", categories)
        self.assertIn("accessibility_baseline", categories)
        self.assertIn("localization_seed", categories)

    def test_candidate_generation_add_should_continue_after_existing_max_task_id(self) -> None:
        mod = _load_module("generate_task_candidates_for_add_id_test", "scripts/python/generate_task_candidates_from_sources.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_dir = root / "logs" / "ci" / "task-generation"
            task_dir = root / ".taskmaster" / "tasks"
            out_dir.mkdir(parents=True)
            task_dir.mkdir(parents=True)
            (task_dir / "tasks_back.json").write_text(
                json.dumps([{"id": "SG-0007", "title": "Existing back task"}]) + "\n",
                encoding="utf-8",
            )
            (task_dir / "tasks_gameplay.json").write_text(
                json.dumps([{"id": "SG-0010", "title": "Existing gameplay task"}]) + "\n",
                encoding="utf-8",
            )
            (out_dir / "requirements.index.json").write_text(
                json.dumps(
                    {
                        "schema": "task-generation.requirements-index.v1",
                        "anchors": [
                            {
                                "requirement_id": "REQ-ADD-0001",
                                "source_path": "docs/gdd/a.md",
                                "line": 1,
                                "kind": "gdd",
                                "priority": "P1",
                                "text": "New combat loop must be implemented.",
                                "refs": [],
                            },
                            {
                                "requirement_id": "REQ-ADD-0002",
                                "source_path": "docs/prd/b.md",
                                "line": 2,
                                "kind": "prd",
                                "priority": "P2",
                                "text": "New onboarding must be implemented.",
                                "refs": [],
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["--repo-root", str(root), "--mode", "add", "--id-prefix", "SG"])
            payload = json.loads((out_dir / "task-candidates.normalized.json").read_text(encoding="utf-8"))

        self.assertEqual(0, rc)
        self.assertEqual(["SG-0011", "SG-0012"], [candidate["id"] for candidate in payload["candidates"]])

    def test_compile_triplet_add_should_renumber_before_write_and_preserve_existing_tasks(self) -> None:
        mod = _load_module("compile_task_triplet_for_add_id_test", "scripts/python/compile_task_triplet.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_dir = root / "logs" / "ci" / "task-generation"
            task_dir = root / ".taskmaster" / "tasks"
            out_dir.mkdir(parents=True)
            task_dir.mkdir(parents=True)
            (task_dir / "tasks_back.json").write_text(
                json.dumps([{"id": "SG-0001", "title": "Keep existing back"}]) + "\n",
                encoding="utf-8",
            )
            (task_dir / "tasks_gameplay.json").write_text(
                json.dumps([{"id": "SG-0003", "title": "Keep existing gameplay"}]) + "\n",
                encoding="utf-8",
            )
            (out_dir / "coverage-report.json").write_text(json.dumps({"status": "ok"}) + "\n", encoding="utf-8")
            (out_dir / "task-candidates.enriched.json").write_text(
                json.dumps(
                    {
                        "candidates": [
                            {
                                "id": "SG-0001",
                                "title": "Added architecture task",
                                "owner": "architecture",
                                "labels": [],
                                "depends_on": [],
                            },
                            {
                                "id": "SG-0002",
                                "title": "Added gameplay task",
                                "owner": "gameplay",
                                "labels": ["gdd"],
                                "depends_on": ["SG-0001"],
                            },
                        ]
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["--repo-root", str(root), "--mode", "add", "--write"])
            back = json.loads((task_dir / "tasks_back.json").read_text(encoding="utf-8"))
            gameplay = json.loads((task_dir / "tasks_gameplay.json").read_text(encoding="utf-8"))

        self.assertEqual(0, rc)
        self.assertEqual(["SG-0001", "SG-0004"], [task["id"] for task in back])
        self.assertEqual(["SG-0003", "SG-0005"], [task["id"] for task in gameplay])
        self.assertEqual(["SG-0004"], gameplay[-1]["depends_on"])
        self.assertEqual("Keep existing back", back[0]["title"])
        self.assertEqual("Keep existing gameplay", gameplay[0]["title"])

    def test_compile_triplet_should_block_duplicate_candidate_ids(self) -> None:
        mod = _load_module("compile_task_triplet_for_duplicate_id_test", "scripts/python/compile_task_triplet.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_dir = root / "logs" / "ci" / "task-generation"
            out_dir.mkdir(parents=True)
            (out_dir / "coverage-report.json").write_text(json.dumps({"status": "ok"}) + "\n", encoding="utf-8")
            (out_dir / "task-candidates.enriched.json").write_text(
                json.dumps(
                    {
                        "candidates": [
                            {"id": "SG-0001", "title": "First", "owner": "architecture"},
                            {"id": "SG-0001", "title": "Second", "owner": "architecture"},
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as raised:
                mod.main(["--repo-root", str(root), "--mode", "init"])

        self.assertIn("duplicate_candidate_ids", str(raised.exception))

    def test_enrichment_should_append_technical_preflight_spike_candidate(self) -> None:
        mod = _load_module("enrich_task_candidates_with_technical_preflight_test", "scripts/python/enrich_task_candidates.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_dir = root / "logs" / "ci" / "task-generation"
            out_dir.mkdir(parents=True)
            candidates = {
                "schema": "task-generation.candidates.v1",
                "candidates": [
                    {
                        "id": "SG-0001",
                        "title": "Implement physics sandbox loop",
                        "description": "Gameplay task after preflight.",
                        "labels": ["gameplay"],
                        "owner": "gameplay",
                        "layer": "feature",
                    }
                ],
            }
            technical_preflight = {
                "schema": "technical-preflight.v1",
                "technical_preflight": {
                    "engine_route": {
                        "recommended_action": "engine_spike_required",
                        "candidate_backend": "rapier_2d",
                        "adr_required": True,
                        "reason_codes": ["physics_core_loop", "web_wasm_target"],
                        "chapter3_task_hints": ["Create a physics backend spike for rapier_2d before implementation tasks."],
                        "chapter4_overlay_hints": ["Chapter 4 must record the backend decision."],
                        "chapter6_acceptance_gates": ["Chapter 6 must not install plugins until spike evidence exists."],
                    }
                },
            }
            (out_dir / "task-candidates.normalized.json").write_text(
                json.dumps(candidates, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (out_dir / "technical-preflight.json").write_text(
                json.dumps(technical_preflight, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(
                    [
                        "--repo-root",
                        str(root),
                        "--candidates",
                        "logs/ci/task-generation/task-candidates.normalized.json",
                        "--technical-preflight",
                        "logs/ci/task-generation/technical-preflight.json",
                    ]
                )
            payload = json.loads((out_dir / "task-candidates.enriched.json").read_text(encoding="utf-8"))

        self.assertEqual(0, rc)
        titles = [candidate["title"] for candidate in payload["candidates"]]
        self.assertIn("Run technical preflight spike for rapier_2d", titles)
        spike = next(candidate for candidate in payload["candidates"] if candidate["title"] == "Run technical preflight spike for rapier_2d")
        self.assertEqual("architecture", spike["owner"])
        self.assertIn("technical-preflight", spike["labels"])
        self.assertTrue(spike["technical_preflight"]["adr_required"])
        implementation = next(candidate for candidate in payload["candidates"] if candidate["id"] == "SG-0001")
        self.assertIn(spike["id"], implementation["depends_on"])
        self.assertEqual(
            {
                "available": True,
                "recommended_action": "engine_spike_required",
                "candidate_backend": "rapier_2d",
                "spike_count": 1,
            },
            payload["inventory"]["technical_preflight"],
        )

    def test_chapter3_regression_should_pass_explicit_technical_preflight_summary_to_enrichment(self) -> None:
        mod = _load_module("run_chapter3_regression_check_preflight_test", "scripts/python/run_chapter3_regression_check.py")
        commands: list[list[str]] = []

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            template = root / "template"
            repo = root / "business"
            out_dir = template / "logs" / "analysis" / "chapter3-regression" / "business"
            template.mkdir(parents=True)
            repo.mkdir()
            (template / "workflow.md").write_text("workflow", encoding="utf-8")
            (template / "logs" / "ci" / "technical-preflight").mkdir(parents=True)
            (template / "logs" / "ci" / "technical-preflight" / "summary.json").write_text(
                json.dumps(
                    {
                        "schema": "technical-preflight.v1",
                        "source": {"path": str(repo / "docs" / "prototypes" / "current.md")},
                    },
                    ensure_ascii=True,
                )
                + "\n",
                encoding="utf-8",
            )

            def fake_run(_template_root: Path, command: list[str]) -> None:
                commands.append(command)
                out_dir.mkdir(parents=True, exist_ok=True)
                if any(item.endswith("audit_task_intents_quality.py") for item in command):
                    (out_dir / "task-intents.quality.json").write_text(json.dumps({"status": "ok", "issue_count": 0}) + "\n", encoding="utf-8")
                elif any(item.endswith("enrich_task_candidates.py") for item in command):
                    (out_dir / "task-candidates.enriched.json").write_text(json.dumps({"candidates": []}) + "\n", encoding="utf-8")
                elif any(item.endswith("audit_task_candidate_coverage.py") for item in command):
                    (out_dir / "coverage-report.json").write_text(json.dumps({"status": "ok", "missing_blocking_count": 0}) + "\n", encoding="utf-8")

            original_run = mod.run
            mod.run = fake_run
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = mod.main(
                        [
                            str(repo),
                            "--template-root",
                            str(template),
                            "--technical-preflight",
                            str(template / "logs" / "ci" / "technical-preflight" / "summary.json"),
                        ]
                    )
            finally:
                mod.run = original_run

        self.assertEqual(0, rc)
        enrich_cmd = next(command for command in commands if "scripts/python/enrich_task_candidates.py" in command)
        self.assertIn("--technical-preflight", enrich_cmd)
        self.assertIn(str(template / "logs" / "ci" / "technical-preflight" / "summary.json"), enrich_cmd)

    def test_chapter3_regression_should_not_consume_technical_preflight_without_explicit_argument(self) -> None:
        mod = _load_module("run_chapter3_regression_check_stale_preflight_test", "scripts/python/run_chapter3_regression_check.py")
        commands: list[list[str]] = []

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            template = root / "template"
            repo = root / "current-business"
            out_dir = template / "logs" / "analysis" / "chapter3-regression" / "current-business"
            template.mkdir(parents=True)
            repo.mkdir()
            (template / "workflow.md").write_text("workflow", encoding="utf-8")
            summary = {
                "schema": "technical-preflight.v1",
                "source": {
                    "path": str(repo / "docs" / "prototypes" / "old.md"),
                },
            }
            (template / "logs" / "ci" / "technical-preflight").mkdir(parents=True)
            (template / "logs" / "ci" / "technical-preflight" / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=True) + "\n",
                encoding="utf-8",
            )

            def fake_run(_template_root: Path, command: list[str]) -> None:
                commands.append(command)
                out_dir.mkdir(parents=True, exist_ok=True)
                if any(item.endswith("audit_task_intents_quality.py") for item in command):
                    (out_dir / "task-intents.quality.json").write_text(json.dumps({"status": "ok", "issue_count": 0}) + "\n", encoding="utf-8")
                elif any(item.endswith("enrich_task_candidates.py") for item in command):
                    (out_dir / "task-candidates.enriched.json").write_text(json.dumps({"candidates": []}) + "\n", encoding="utf-8")
                elif any(item.endswith("audit_task_candidate_coverage.py") for item in command):
                    (out_dir / "coverage-report.json").write_text(json.dumps({"status": "ok", "missing_blocking_count": 0}) + "\n", encoding="utf-8")

            original_run = mod.run
            mod.run = fake_run
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = mod.main([str(repo), "--template-root", str(template)])
            finally:
                mod.run = original_run

        self.assertEqual(0, rc)
        enrich_cmd = next(command for command in commands if "scripts/python/enrich_task_candidates.py" in command)
        self.assertNotIn("--technical-preflight", enrich_cmd)

    def test_task_intent_quality_audit_should_report_generic_and_noisy_titles(self) -> None:
        mod = _load_module("audit_task_intents_quality_test", "scripts/python/audit_task_intents_quality.py")
        result = mod.audit(
            {
                "schema": "task-generation.task-intents.v1",
                "intents": [
                    {
                        "id": "INT-0001",
                        "title": "Add test coverage for testing",
                        "covered_anchor_count": 2,
                        "requirement_ids": ["REQ-1"],
                        "source_refs": ["docs/gdd/a.md:1"],
                    },
                    {
                        "id": "INT-0002",
                        "title": "Implement tasks.json refs",
                        "covered_anchor_count": 9,
                        "requirement_ids": [],
                        "source_refs": [],
                    },
                ],
            },
            max_anchors_per_intent=8,
        )

        self.assertEqual("review", result["status"])
        self.assertEqual(2, result["issue_count"])
        self.assertIn("generic_title", result["issue_counts"])
        self.assertIn("metadata_noise_in_title", result["issue_counts"])
        self.assertIn("too_many_anchors", result["issue_counts"])
        self.assertIn("missing_traceability", result["issue_counts"])

    def test_task_intent_quality_audit_should_not_flag_planning_metadata_seed_size(self) -> None:
        mod = _load_module("audit_task_intents_quality_planning_seed_test", "scripts/python/audit_task_intents_quality.py")
        result = mod.audit(
            {
                "schema": "task-generation.task-intents.v1",
                "intents": [
                    {
                        "id": "INT-0001",
                        "title": "Create screen inventory hud input localization accessibility",
                        "covered_anchor_count": 12,
                        "requirement_ids": ["REQ-UI-1"],
                        "source_refs": ["docs/gdd/a.md:1"],
                        "labels": ["planning-metadata", "ui-ux-seed", "chapter7-input"],
                    },
                ],
            },
            max_anchors_per_intent=8,
        )

        self.assertEqual("ok", result["status"])
        self.assertNotIn("too_many_anchors", result["issue_counts"])

    def test_task_intent_quality_audit_should_treat_part_numbers_as_disambiguators(self) -> None:
        mod = _load_module("audit_task_intents_quality_part_key_test", "scripts/python/audit_task_intents_quality.py")
        result = mod.audit(
            {
                "schema": "task-generation.task-intents.v1",
                "intents": [
                    {
                        "id": "INT-0001",
                        "title": "Validate gdd part 1 closure deterministic draft state missing",
                        "covered_anchor_count": 4,
                        "requirement_ids": ["REQ-1"],
                        "source_refs": ["docs/gdd/a.md:1"],
                    },
                    {
                        "id": "INT-0002",
                        "title": "Validate gdd part 4 closure deterministic draft state missing",
                        "covered_anchor_count": 4,
                        "requirement_ids": ["REQ-2"],
                        "source_refs": ["docs/gdd/a.md:4"],
                    },
                ],
            },
            max_anchors_per_intent=8,
        )

        self.assertEqual("ok", result["status"])

    def test_regression_check_should_filter_back_only_and_post_ch3_tasks(self) -> None:
        mod = _load_module("run_chapter3_regression_check_test", "scripts/python/run_chapter3_regression_check.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task_dir = root / ".taskmaster" / "tasks"
            task_dir.mkdir(parents=True)
            (task_dir / "tasks.json").write_text(
                json.dumps(
                    {
                        "master": {
                            "tasks": [
                                {"id": 1, "title": "Shared gameplay task", "labels": []},
                                {"id": 2, "title": "Back only task", "labels": []},
                                {"id": 3, "title": "Wire UI: Chapter 7 task", "labels": ["chapter7-ui"]},
                            ]
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (task_dir / "tasks_back.json").write_text(
                json.dumps(
                    [
                        {"id": "B-1", "taskmaster_id": 1, "title": "Shared gameplay task"},
                        {"id": "B-2", "taskmaster_id": 2, "title": "Back only task"},
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (task_dir / "tasks_gameplay.json").write_text(
                json.dumps([{"id": "G-1", "taskmaster_id": 1, "title": "Shared gameplay task"}]) + "\n",
                encoding="utf-8",
            )

            filtered = mod.filtered_tasks_json(root)

        self.assertEqual([1], [task["id"] for task in filtered])


if __name__ == "__main__":
    unittest.main()
