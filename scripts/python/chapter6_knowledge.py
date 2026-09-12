#!/usr/bin/env python3
"""Capture reviewed Chapter 6 resource associations without inventing business facts."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def capture(root: Path, task_id: str, paths: list[str]) -> dict:
    normalized=[]
    for raw in paths:
        candidate=(root/raw).resolve()
        if root != candidate and root not in candidate.parents: raise ValueError(f"path escapes repository: {raw}")
        if not candidate.exists(): raise ValueError(f"resource path does not exist: {raw}")
        normalized.append(candidate.relative_to(root).as_posix())
    if not normalized:
        return {"status":"skipped","reason":"no reviewed resource paths supplied","task_id":task_id}
    out={"schema":"godot-project-knowledge.task-resource-links.v1","task_id":str(task_id),"resources":sorted(set(normalized)),"provenance":"explicit-reviewed-input"}
    path=root/"docs/knowledge/generated"/f"task-{task_id}-resources.json"; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"status":"ok","output":path.relative_to(root).as_posix(),"count":len(out["resources"])}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repo-root",default="."); p.add_argument("--task-id",required=True); p.add_argument("--path",action="append",default=[]); a=p.parse_args(argv); print(json.dumps(capture(Path(a.repo_root).resolve(),a.task_id,a.path),ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
