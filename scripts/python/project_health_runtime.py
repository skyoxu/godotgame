#!/usr/bin/env python3
"""Template-safe runtime eligibility reporter for Project Health.

It never treats engine startup as task acceptance. A task is eligible only when its
Taskmaster record declares concrete test references already present in the repo.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def _walk_tasks(value):
    if isinstance(value,dict):
        if "id" in value and ("title" in value or "status" in value): yield value
        for child in value.values(): yield from _walk_tasks(child)
    elif isinstance(value,list):
        for child in value: yield from _walk_tasks(child)

def eligibility(root: Path) -> dict:
    task_dir=root/".taskmaster/tasks"; tasks=[]
    if task_dir.exists():
        for file in sorted(task_dir.glob("*.json")):
            try: data=json.loads(file.read_text(encoding="utf-8-sig"))
            except Exception: continue
            for task in _walk_tasks(data):
                refs=task.get("test_refs") or []
                if isinstance(refs,str): refs=[refs]
                existing=[str(ref).replace("\\","/") for ref in refs if isinstance(ref,str) and (root/ref).exists()]
                tasks.append({"id":str(task.get("id")),"title":str(task.get("title") or ""),"eligible":bool(existing),"test_refs":existing})
    return {"schema":"godot-project-health.runtime-eligibility.v1","status":"ok","tasks":tasks,"eligible_count":sum(1 for t in tasks if t["eligible"]),"note":"Eligibility is not runtime acceptance. Execute task-specific assertions through the normal test workflow."}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repo-root",default="."); a=p.parse_args(argv); print(json.dumps(eligibility(Path(a.repo_root).resolve()),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
