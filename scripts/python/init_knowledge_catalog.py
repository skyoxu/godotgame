#!/usr/bin/env python3
"""Initialize template-safe Knowledge directories without business data."""
from __future__ import annotations
import argparse, json
from pathlib import Path

FILES = {
    "docs/knowledge/README.md": "# Project Resource Knowledge\n\nThis directory is human-reviewable project resource knowledge. It starts empty in the template. Repository sources remain authoritative.\n",
    "knowledge/policies/consumer-policies.v1.json": json.dumps({"schema":"godot-project-knowledge.consumer-policies.v1","revision":"godot-project-knowledge-v1","consumers":{"repository-session":{"task_id_required":False,"observe_only":True},"chapter4":{"task_id_required":False,"observe_only":True},"chapter5":{"task_id_required":True,"observe_only":True},"chapter6":{"task_id_required":True,"freeze_before_red":True},"review":{"task_id_required":True,"separate_from_chapter6":True}}},indent=2)+"\n",
    "knowledge/policies/source-exclusions.v1.json": json.dumps({"schema":"godot-project-knowledge.source-exclusions.v1","rules":[{"prefix":".git/","reason":"repository internals"},{"prefix":".godot/","reason":"generated engine state"},{"prefix":"logs/","reason":"run evidence is not repository authority"}]},indent=2)+"\n",
}

def initialize(root: Path) -> dict:
    created=[]
    for rel, content in FILES.items():
        path=root/rel; path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists(): path.write_text(content,encoding="utf-8"); created.append(rel)
    for rel in ("docs/knowledge/generated", "knowledge/indexes/generations", "knowledge/catalogs", "knowledge/snapshots"):
        (root/rel).mkdir(parents=True,exist_ok=True)
    return {"status":"ok","created":created,"business_data_seeded":False}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repo-root",default="."); a=p.parse_args(argv); print(json.dumps(initialize(Path(a.repo_root).resolve()),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
