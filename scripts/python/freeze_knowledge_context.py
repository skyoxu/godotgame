#!/usr/bin/env python3
"""Freeze an explicit candidate decision set into bounded context."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def sha(obj): return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
def freeze(bundle: dict, decisions: dict) -> dict:
    if bundle.get("schema")!="godot-project-knowledge.context-candidates.v1": raise ValueError("unsupported candidate bundle")
    by_path={c["path"]:c for c in bundle.get("candidates",[])}
    rows=[]
    for item in decisions.get("decisions",[]):
        path=str(item.get("path") or ""); accepted=bool(item.get("accepted")); reason=str(item.get("reason") or "").strip(); satisfies=str(item.get("satisfies") or "").strip()
        if path not in by_path: raise ValueError(f"decision path is not a candidate: {path}")
        if not reason: raise ValueError(f"decision reason required: {path}")
        rows.append({"path":path,"accepted":accepted,"reason":reason,"satisfies":satisfies,"source":by_path[path]})
    if not rows: raise ValueError("at least one explicit candidate decision is required")
    out={"schema":"godot-project-knowledge.frozen-context.v1","consumer":bundle.get("consumer"),"task_id":bundle.get("task_id"),"revision":bundle.get("revision"),"candidate_bundle_sha256":bundle.get("bundle_sha256") or sha(bundle),"decisions":rows,"accepted_paths":[r["path"] for r in rows if r["accepted"]]}
    out["frozen_sha256"]=sha(out); return out

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--bundle",required=True); p.add_argument("--decisions",required=True); p.add_argument("--output",required=True); a=p.parse_args(argv)
    bundle=json.loads(Path(a.bundle).read_text(encoding="utf-8")); decisions=json.loads(Path(a.decisions).read_text(encoding="utf-8")); out=freeze(bundle,decisions); Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"ok","output":a.output,"frozen_sha256":out["frozen_sha256"]})); return 0
if __name__=="__main__": raise SystemExit(main())
