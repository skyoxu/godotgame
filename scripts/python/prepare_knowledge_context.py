#!/usr/bin/env python3
"""Prepare observe-only Knowledge context candidates."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from knowledge_locator import locate

def canonical(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
def prepare(root, consumer, text, task_id=None):
    located=locate(root,consumer=consumer,text=text,task_id=task_id)
    payload={"schema":"godot-project-knowledge.context-candidates.v1","consumer":consumer,"task_id":task_id,"revision":located["revision"],"query":text,"candidates":located["candidates"],"observe_only":True}
    payload["bundle_sha256"]=hashlib.sha256(canonical(payload)).hexdigest(); return payload

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repository-root",default="."); p.add_argument("--consumer",required=True); p.add_argument("--query",required=True); p.add_argument("--task-id"); p.add_argument("--output")
    a=p.parse_args(argv); data=prepare(a.repository_root,a.consumer,a.query,a.task_id); text=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    if a.output: Path(a.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 0
if __name__=="__main__": raise SystemExit(main())
