#!/usr/bin/env python3
"""Run template-safe Project Health browser regression against a local loopback server."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/python"))

from _project_health_server import ensure_project_health_server


def _stop(pid: int) -> None:
    if pid <= 0:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, check=False)
    else:
        try:
            os.kill(pid, 15)
        except ProcessLookupError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--playwright-root", required=True)
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    pwroot = Path(args.playwright_root).resolve()
    cli = pwroot / "node_modules/@playwright/test/cli.js"
    if not cli.is_file():
        raise SystemExit("Playwright CLI is missing: " + str(cli))
    server = ensure_project_health_server(root=root)
    env = dict(os.environ)
    env["NODE_PATH"] = str(pwroot / "node_modules")
    env["PROJECT_HEALTH_URL"] = f"http://127.0.0.1:{server['port']}"
    try:
        result = subprocess.run(
            ["node", str(cli), "test", "scripts/browser/project_health.spec.js", "--reporter=line", "--workers=1"],
            cwd=root,
            env=env,
            check=False,
        )
        return result.returncode
    finally:
        if not server.get("reused"):
            _stop(int(server.get("pid") or 0))


if __name__ == "__main__":
    raise SystemExit(main())
