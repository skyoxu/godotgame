from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from project_health_knowledge import scan, query, safe_file
from impact_analyzer import ImpactAnalyzer
from prepare_knowledge_context import prepare
from freeze_knowledge_context import freeze
from chapter6_knowledge import capture
from project_health_runtime import eligibility
from workflow_chapter_knowledge_overlay import BEGIN, END, apply_overlay

class TemplateKnowledgeImpactTests(unittest.TestCase):
    def test_empty_template_and_deterministic_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"docs").mkdir(); (root/"docs/spec.md").write_text("PlayerService emits ReadyEvent\n",encoding="utf-8")
            cfg={"schema":"godot-project-knowledge.config.v1","source_paths":["docs"],"include_extensions":[".md"],"max_file_bytes":512000,"max_results":50}
            state=scan(root,cfg); self.assertEqual(1,state["counts"]["files"])
            self.assertEqual("docs/spec.md",query(root,"PlayerService")["results"][0]["path"])
    def test_impact_text_reference_is_not_confirmed_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"docs").mkdir(); (root/"docs/spec.md").write_text("PlayerService\n",encoding="utf-8")
            scan(root,{"source_paths":["docs"],"include_extensions":[".md"],"max_file_bytes":512000,"max_results":50})
            report=ImpactAnalyzer(root).analyze("PlayerService")
            self.assertFalse(report["evidence"][0]["confirmed"])
    def test_freeze_requires_explicit_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"docs").mkdir(); (root/"docs/a.md").write_text("intent",encoding="utf-8")
            scan(root,{"source_paths":["docs"],"include_extensions":[".md"],"max_file_bytes":512000,"max_results":50})
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
            self.assertEqual(once,twice)
            self.assertEqual(1,twice.count(BEGIN))

if __name__=="__main__": unittest.main()
