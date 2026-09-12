#!/usr/bin/env python3
"""CLI for deterministic Impact exploration or formal strict analysis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from impact_analyzer import ImpactAnalyzer


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target", required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--frozen-context")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    frozen_hash = None
    if args.strict:
        if not args.frozen_context:
            parser.error("--strict formal analysis requires --frozen-context")
        frozen = json.loads(Path(args.frozen_context).read_text(encoding="utf-8"))
        frozen_hash = str(frozen.get("frozen_sha256") or "").strip()
        if not frozen_hash:
            raise ValueError("frozen context hash is missing")
    out = ImpactAnalyzer(args.repo_root).analyze(args.target, strict=args.strict, frozen_context_sha256=frozen_hash)
    if args.strict:
        frozen = json.loads(Path(args.frozen_context).read_text(encoding="utf-8"))
        if frozen.get("revision") != out.get("revision"):
            raise ValueError("frozen context revision does not match Impact index/report revision")
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__": raise SystemExit(main())
