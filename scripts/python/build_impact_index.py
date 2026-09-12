#!/usr/bin/env python3
"""Build or validate a revision-bound template Impact Index."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from impact_analysis_index import ImpactIndexError, build_index, load_current_index, publish_index


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--revision", required=True)
    parser.add_argument("--trusted-ref")
    parser.add_argument("--output-root", type=Path, default=Path("logs/ci"))
    parser.add_argument("--reuse-only", action="store_true")
    args = parser.parse_args(argv)
    root = args.repository_root.resolve()
    try:
        if args.reuse_only:
            index = load_current_index(root, args.revision)
            result = {"status": "reused", "index_id": index["index_id"], "repository_revision": index["repository_revision"]}
        else:
            output = (root / args.output_root).resolve()
            if root != output and root not in output.parents:
                raise ImpactIndexError("path_outside_repository", "output root must remain inside repository")
            index = build_index(root, args.revision, trusted_ref=args.trusted_ref)
            result = publish_index(root, index, output)
            result["repository_revision"] = index["repository_revision"]
    except ImpactIndexError as exc:
        print(json.dumps({"schema":"godot-project-impact.index-build-result.v1","status":"failed","code":exc.code,"reason":exc.reason}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"schema":"godot-project-impact.index-build-result.v1", **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__": raise SystemExit(main())
