#!/usr/bin/env python3
"""Bridge generate2dsprite image requests to the repo-local dev_cli image wrapper."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "scripts" / "python" / "dev_cli.py").is_file():
            return candidate
    raise FileNotFoundError(
        "Could not find repo root containing scripts/python/dev_cli.py. Pass --repo-root explicitly."
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Project root containing scripts/python/dev_cli.py.")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--prompt-file", default="")
    parser.add_argument("--out", required=True)
    parser.add_argument("--manifest-out", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--group", default="")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--output-format", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--response-format", default="b64_json", choices=["b64_json", "url"])
    parser.add_argument("--background", default="", choices=["", "transparent", "opaque", "auto"])
    parser.add_argument("--api-key-env", default="AIARTMIRROR_API_KEY")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    repo_root = _find_repo_root(Path(args.repo_root))
    cmd = [
        "py",
        "-3",
        "scripts/python/dev_cli.py",
        "generate-image",
        "--out",
        args.out,
        "--size",
        args.size,
        "--quality",
        args.quality,
        "--output-format",
        args.output_format,
        "--response-format",
        args.response_format,
        "--api-key-env",
        args.api_key_env,
        "--timeout",
        str(args.timeout),
    ]
    if args.prompt:
        cmd += ["--prompt", args.prompt]
    if args.prompt_file:
        cmd += ["--prompt-file", args.prompt_file]
    if args.manifest_out:
        cmd += ["--manifest-out", args.manifest_out]
    if args.model:
        cmd += ["--model", args.model]
    if args.group:
        cmd += ["--group", args.group]
    if args.background:
        cmd += ["--background", args.background]
    if args.base_url:
        cmd += ["--base-url", args.base_url]
    if args.dry_run:
        cmd.append("--dry-run")

    proc = subprocess.run(cmd, cwd=repo_root)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
