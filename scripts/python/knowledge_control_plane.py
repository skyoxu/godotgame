#!/usr/bin/env python3
"""Deterministic Knowledge Control Plane and formal file-level Impact primitives.

This template implementation is intentionally repository-generic. It never
creates gameplay facts; it indexes reviewed repository files and binds frozen
contexts/reports to Git revisions and content hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONSUMERS = {"repository-session", "chapter4", "chapter5", "chapter6", "review"}
SOURCE_ROOTS = ("AGENTS.md", "workflow.md", "docs", ".taskmaster/tasks", "scripts", "Game.Core", "Game.Godot", "Game.Core.Tests", "Game.Godot.Tests")
TEXT_SUFFIXES = {".md", ".json", ".cs", ".gd", ".tscn", ".tres", ".py", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".xml", ".csproj", ".sln", ".js", ".ts", ".html", ".css", ".txt"}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    return proc.stdout.strip()


def repo_root(path: Path) -> Path:
    return Path(git(path.resolve(), "rev-parse", "--show-toplevel")).resolve()


def revision(root: Path, ref: str = "HEAD") -> str:
    return git(root, "rev-parse", "--verify", ref)


def tracked_files(root: Path, rev: str) -> list[str]:
    output = git(root, "ls-tree", "-r", "--name-only", rev, "--", *SOURCE_ROOTS)
    return sorted({line.strip().replace("\\", "/") for line in output.splitlines() if line.strip() and Path(line.strip()).suffix.lower() in TEXT_SUFFIXES})


def read_at(root: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=root, capture_output=True, check=False)
    if proc.returncode or len(proc.stdout) > 1024 * 1024:
        return None
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def classify(path: str) -> str:
    low = path.lower()
    if low.startswith(".taskmaster/tasks/"):
        return "task"
    if "/gdd/" in low or "/prd/" in low:
        return "requirements"
    if "/adr/" in low or "architecture" in low:
        return "architecture"
    if "contract" in low or "schema" in low:
        return "contracts"
    if "/test" in low or ".tests/" in low:
        return "tests"
    if low.startswith("docs/knowledge/"):
        return "resource-knowledge"
    if low.endswith((".cs", ".gd", ".tscn", ".tres", ".json")):
        return "implementation"
    return "repository-entrypoints"


def build_catalog(root: Path, rev: str | None = None) -> dict[str, Any]:
    root = repo_root(root); rev = rev or revision(root)
    entries=[]
    for path in tracked_files(root, rev):
        text=read_at(root, rev, path)
        if text is None: continue
        entries.append({"path":path,"context_class":classify(path),"sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),"bytes":len(text.encode("utf-8"))})
    payload={"schema_version":"godot-project-knowledge.catalog.v1","revision":rev,"generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"entries":entries}
    out=root/"knowledge"/"catalogs"/"candidate.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(canonical(payload)); return payload


def locate(root: Path, query: str, consumer: str, rev: str | None = None) -> dict[str, Any]:
    if consumer not in CONSUMERS: raise ValueError(f"unsupported consumer: {consumer}")
    root=repo_root(root); catalog=build_catalog(root, rev); tokens=[x.lower() for x in re.findall(r"[A-Za-z0-9_.:/-]+|[\u4e00-\u9fff]+",query) if len(x)>=2]
    results=[]
    for entry in catalog["entries"]:
        text=read_at(root,catalog["revision"],entry["path"]) or ""; low=(entry["path"]+"\n"+text).lower(); score=sum(12 if t in entry["path"].lower() else min(low.count(t),5)*2 for t in tokens)
        if score: results.append({**entry,"score":score})
    results.sort(key=lambda x:(-x["score"],x["path"]))
    return {"schema_version":"godot-project-knowledge.locator-result.v1","consumer":consumer,"query":query,"revision":catalog["revision"],"candidates":results[:50],"semantic_acceptance":False}


def prepare(root: Path, query: str, consumer: str, task_id: str | None = None) -> dict[str, Any]:
    located=locate(root,query,consumer); payload={"schema_version":"godot-project-knowledge.context-candidates.v1","consumer":consumer,"task_id":task_id,"revision":located["revision"],"query":query,"candidates":located["candidates"],"bundle_hash":""}; payload["bundle_hash"]=digest({k:v for k,v in payload.items() if k!="bundle_hash"}); return payload


def freeze(root: Path, bundle_path: Path, decisions_path: Path) -> dict[str, Any]:
    root=repo_root(root); bundle=json.loads(bundle_path.read_text(encoding="utf-8")); decisions=json.loads(decisions_path.read_text(encoding="utf-8")); expected=digest({k:v for k,v in bundle.items() if k!="bundle_hash"})
    if bundle.get("bundle_hash")!=expected: raise ValueError("candidate bundle hash mismatch")
    accepted=set(str(x) for x in decisions.get("accepted_paths",[])); known={x["path"] for x in bundle.get("candidates",[])}
    if not accepted.issubset(known): raise ValueError("decisions contain paths outside the candidate bundle")
    payload={"schema_version":"godot-project-knowledge.frozen-context.v1","consumer":bundle["consumer"],"task_id":bundle.get("task_id"),"revision":bundle["revision"],"candidate_bundle_hash":expected,"accepted_paths":sorted(accepted),"decision_reason":str(decisions.get("reason") or ""),"frozen_hash":""}; payload["frozen_hash"]=digest({k:v for k,v in payload.items() if k!="frozen_hash"}); return payload


def build_impact_index(root: Path, rev: str | None = None) -> dict[str, Any]:
    root=repo_root(root); rev=rev or revision(root); nodes=[]; refs=[]
    files=tracked_files(root,rev); names={Path(p).name.lower():p for p in files}
    for path in files:
        text=read_at(root,rev,path)
        if text is None: continue
        nodes.append({"path":path,"sha256":hashlib.sha256(text.encode()).hexdigest(),"kind":classify(path)})
        low=text.lower()
        for name,target in names.items():
            if target!=path and name in low: refs.append({"from":path,"to":target,"evidence":"filename-reference"})
    return {"schema_version":"godot-project-knowledge.impact-index.v1","revision":rev,"nodes":nodes,"references":refs,"index_hash":digest({"revision":rev,"nodes":nodes,"references":refs})}


def analyze_impact(root: Path, target: str, frozen: dict[str, Any] | None = None, rev: str | None = None) -> dict[str, Any]:
    index=build_impact_index(root,rev); paths={n["path"] for n in index["nodes"]}
    if target not in paths: raise ValueError("formal impact target must be an indexed repository file")
    incoming=[r for r in index["references"] if r["to"]==target]; outgoing=[r for r in index["references"] if r["from"]==target]
    if frozen is not None and frozen.get("revision")!=index["revision"]: raise ValueError("frozen context revision does not match impact revision")
    payload={"schema_version":"godot-project-knowledge.impact-report.v1","revision":index["revision"],"target":{"type":"file","id":target},"incoming":incoming,"outgoing":outgoing,"index_hash":index["index_hash"],"frozen_context_hash":frozen.get("frozen_hash") if frozen else None,"formal":True}; payload["report_hash"]=digest(payload); return payload


def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(); p.add_argument("action",choices=["build","locate","prepare","freeze","impact-index","impact-analyze"]); p.add_argument("--repo-root",type=Path,default=Path.cwd()); p.add_argument("--query",default=""); p.add_argument("--consumer",default="repository-session"); p.add_argument("--task-id"); p.add_argument("--bundle",type=Path); p.add_argument("--decisions",type=Path); p.add_argument("--target"); p.add_argument("--frozen",type=Path); p.add_argument("--out",type=Path); a=p.parse_args(argv)
    root=repo_root(a.repo_root)
    try:
        if a.action=="build": result=build_catalog(root)
        elif a.action=="locate": result=locate(root,a.query,a.consumer)
        elif a.action=="prepare": result=prepare(root,a.query,a.consumer,a.task_id)
        elif a.action=="freeze":
            if not a.bundle or not a.decisions: raise ValueError("--bundle and --decisions are required")
            result=freeze(root,a.bundle,a.decisions)
        elif a.action=="impact-index": result=build_impact_index(root)
        else:
            if not a.target: raise ValueError("--target is required")
            frozen=json.loads(a.frozen.read_text(encoding="utf-8")) if a.frozen else None; result=analyze_impact(root,a.target,frozen)
        text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
        if a.out: a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(text,encoding="utf-8")
        print(text,end=""); return 0
    except (OSError,ValueError,RuntimeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"error","error":str(exc)},ensure_ascii=False)); return 2

if __name__=="__main__": raise SystemExit(main())
