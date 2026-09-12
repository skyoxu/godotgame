#!/usr/bin/env python3
"""CLI for deterministic impact exploration / strict target analysis."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from impact_analyzer import ImpactAnalyzer

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--repo-root",default="."); p.add_argument("--target",required=True); p.add_argument("--strict",action="store_true"); p.add_argument("--output"); a=p.parse_args(argv)
    out=ImpactAnalyzer(a.repo_root).analyze(a.target,strict=a.strict); text=json.dumps(out,ensure_ascii=False,indent=2)+"\n"
    if a.output: Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 0
if __name__=="__main__": raise SystemExit(main())
