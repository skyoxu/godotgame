from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from project_health_knowledge import scan, query, safe_file, save_config, task_details
from impact_analyzer import ImpactAnalyzer
from prepare_knowledge_context import prepare
from freeze_knowledge_context import freeze
from chapter6_knowledge import capture
from project_health_runtime import eligibility
from project_health_godot import inspect_scene, task_navigation
from workflow_chapter_knowledge_overlay import BEGIN, END, apply_overlay

class TemplateKnowledgeImpactTests(unittest.TestCase):
    def test_empty_template_and_deterministic_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"docs").mkdir(); (root/"docs/spec.md").write_text("PlayerService emits ReadyEvent\n",encoding="utf-8")
            cfg={"source_path_bindings":{"docs":"docs"},"source_paths":["docs"],"gdd_paths":[],"task_scene_bindings":[],"query_aliases":{},"include_extensions":[".md"],"max_file_bytes":512000,"max_results":50}
            state=scan(root,cfg); self.assertEqual(1,state["counts"]["files"])
            self.assertEqual("docs/spec.md",query(root,"PlayerService")["results"][0]["path"])
    def test_aliases_and_actionable_categories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"Game.Core").mkdir(); (root/"Tests.Godot").mkdir(); (root/"docs/gdd").mkdir(parents=True)
            (root/"Game.Core/Reward.cs").write_text("class RewardService {}\n",encoding="utf-8")
            (root/"Tests.Godot/test_reward.gd").write_text("RewardService\n",encoding="utf-8")
            (root/"docs/gdd/reward.md").write_text("奖励 RewardService\n",encoding="utf-8")
            cfg={"source_path_bindings":{"domain_code":"Game.Core","engine_tests":"Tests.Godot"},"source_paths":["Game.Core","Tests.Godot"],"gdd_paths":["docs/gdd"],"task_scene_bindings":[],"query_aliases":{"奖励":["RewardService"]},"include_extensions":[".md",".cs",".gd"],"max_file_bytes":512000,"max_results":50}
            save_config(root,cfg); scan(root)
            result=query(root,"奖励")
            self.assertIn("RewardService",result["queries"])
            self.assertTrue(result["actionable"]["code"])
            self.assertTrue(result["actionable"]["tests"])
            self.assertTrue(result["gdd_supplements"])
    def test_impact_text_reference_is_not_confirmed_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"docs").mkdir(); (root/"docs/spec.md").write_text("PlayerService\n",encoding="utf-8")
            scan(root,{"source_path_bindings":{"docs":"docs"},"source_paths":["docs"],"gdd_paths":[],"task_scene_bindings":[],"query_aliases":{},"include_extensions":[".md"],"max_file_bytes":512000,"max_results":50})
            report=ImpactAnalyzer(root).analyze("PlayerService")
            self.assertFalse(report["evidence"][0]["confirmed"])
    def test_freeze_requires_explicit_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"docs").mkdir(); (root/"docs/a.md").write_text("intent",encoding="utf-8")
            scan(root,{"source_path_bindings":{"docs":"docs"},"source_paths":["docs"],"gdd_paths":[],"task_scene_bindings":[],"query_aliases":{},"include_extensions":[".md"],"max_file_bytes":512000,"max_results":50})
            bundle=prepare(root,"chapter6","intent","1")
            with self.assertRaises(ValueError): freeze(bundle,{"decisions":[{"path":"docs/a.md","accepted":True,"reason":""}]})
    def test_resource_capture_never_invents_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.assertEqual("skipped",capture(root,"1",[])["status"])
            with self.assertRaises(ValueError): capture(root,"1",["missing.tscn"])
    def test_safe_file_rejects_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): safe_file(Path(tmp).resolve(),"../outside")
    def test_runtime_eligibility_uses_only_existing_task_scoped_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            task_dir=root/".taskmaster/tasks"; task_dir.mkdir(parents=True)
            test_dir=root/"Tests.Godot/tests/Gameplay"; test_dir.mkdir(parents=True)
            (test_dir/"test_reward.gd").write_text("extends GdUnitTestSuite\n",encoding="utf-8")
            (task_dir/"tasks_gameplay.json").write_text(json.dumps({"tasks":[{"id":"7","title":"Reward","test_refs":["Tests.Godot/tests/Gameplay/test_reward.gd","Tests.Godot/tests/Gameplay/missing.gd"]}]}),encoding="utf-8")
            result=eligibility(root)
            self.assertEqual(1,result["eligible_count"])
            self.assertEqual(["Tests.Godot/tests/Gameplay/test_reward.gd"],result["tasks"][0]["test_refs"])
    def test_static_godot_navigation_uses_real_scene_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); scene_dir=root/"Game.Godot/Scenes"; script_dir=root/"Game.Godot/Scripts"; scene_dir.mkdir(parents=True); script_dir.mkdir(parents=True)
            (script_dir/"RewardPanel.gd").write_text("extends Control\n",encoding="utf-8")
            (scene_dir/"Reward.tscn").write_text('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://Game.Godot/Scripts/RewardPanel.gd" id="1"]\n\n[node name="Reward" type="Control"]\nscript = ExtResource("1")\n\n[node name="Confirm" type="Button" parent="."]\n',encoding="utf-8")
            inspected=inspect_scene(root,"Game.Godot/Scenes/Reward.tscn")
            self.assertTrue(inspected["exists"]); self.assertIn("Game.Godot/Scripts/RewardPanel.gd",inspected["scripts"])
            nav=task_navigation(root,"7",[{"task_id":"7","scene":"Game.Godot/Scenes/Reward.tscn","nodes":["Confirm"]}])
            self.assertEqual("configured",next(row for row in nav["nodes"] if row["name"]=="Confirm")["evidence_kind"])
    def test_workflow_overlay_is_single_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"SKILL.md"
            path.write_text("# Skill\n\n## Idempotent Procedure\n\n1. Original\n",encoding="utf-8")
            body="## Knowledge / Impact Contract\n\n- Rule"
            self.assertTrue(apply_overlay(path,body))
            once=path.read_text(encoding="utf-8")
            self.assertIn(BEGIN,once); self.assertIn(END,once)
            self.assertFalse(apply_overlay(path,body))
            twice=path.read_text(encoding="utf-8")
            self.assertEqual(once,twice); self.assertEqual(1,twice.count(BEGIN))

if __name__=="__main__": unittest.main()
