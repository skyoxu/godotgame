#!/usr/bin/env python3
"""
Run GdUnit4 tests headless and archive reports to logs/e2e/<date>/.

Usage:
  py -3 scripts/python/run_gdunit.py \
    --godot-bin "C:\\Godot\\Godot_v4.5.1-stable_mono_win64_console.exe" \
    --project Tests.Godot \
    --add tests/Adapters --add tests/OtherSuite \
    --timeout-sec 300
"""
import argparse
import datetime as dt
import os
import shutil
import subprocess
import json
import sys
import time
import queue
import threading
import xml.etree.ElementTree as ET


def _find_latest_results_xml(reports_dir: str):
    try:
        if not os.path.isdir(reports_dir):
            return None
        best_path = None
        best_mtime = -1.0
        for name in os.listdir(reports_dir):
            if not name.startswith("report_"):
                continue
            cand = os.path.join(reports_dir, name, "results.xml")
            if not os.path.isfile(cand):
                continue
            mtime = os.path.getmtime(cand)
            if mtime > best_mtime:
                best_mtime = mtime
                best_path = cand
        return best_path
    except Exception:
        return None


def _parse_results_xml(path: str):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        failures = int(root.attrib.get("failures", "0"))
        tests = int(root.attrib.get("tests", "0"))
        errors = int(root.attrib.get("errors", "0"))
        for ts in root.findall("testsuite"):
            errors += int(ts.attrib.get("errors", "0"))
        return {"path": path, "tests": tests, "failures": failures, "errors": errors}
    except Exception as ex:
        return {"path": path, "error": f"parse_failed:{type(ex).__name__}"}


def run_cmd(args, cwd=None, timeout=600_000):
    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding='utf-8', errors='ignore')
    try:
        out, _ = p.communicate(timeout=timeout/1000.0)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        return 124, out
    return p.returncode, out


def run_cmd_failfast(args, cwd=None, timeout=600_000, break_markers=None):
    """Run a process and stream stdout; if any line contains a break marker, kill early and return rc=1.
    This avoids long timeouts when Godot enters Debugger Break state.
    """
    break_markers = break_markers or [
        'Debugger Break',
        'Parser Error',
        'SCRIPT ERROR',
    ]
    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding='utf-8', errors='ignore')
    lines = queue.Queue()

    def read_output():
        try:
            for line in p.stdout:
                lines.put(line)
        finally:
            lines.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    output = []
    deadline = time.monotonic() + timeout / 1000.0
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                p.kill()
                p.wait()
                return 124, ''.join(output)
            try:
                line = lines.get(timeout=remaining)
            except queue.Empty:
                p.kill()
                p.wait()
                return 124, ''.join(output)
            if line is None:
                return p.wait(timeout=max(0.01, deadline - time.monotonic())), ''.join(output)
            output.append(line)
            if any(marker.lower() in line.lower() for marker in break_markers):
                p.kill()
                p.wait()
                return 1, ''.join(output)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
        return 124, ''.join(output)
    finally:
        if p.poll() is None:
            p.kill()
            p.wait()
        reader.join(timeout=1)
        p.stdout.close()


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def prewarm_project(godot_bin: str, project: str, out_dir: str) -> int:
    """ADR-0018: finish cold resource import before building C# solutions."""
    steps = []
    for stage, flags in [('import', ['--editor', '--import']),
                         ('build', ['--build-solutions', '--quit'])]:
        started = time.monotonic()
        rc, output = run_cmd_failfast(
            [godot_bin, '--headless', '--path', project, *flags],
            cwd=project, timeout=300_000,
            break_markers=['Debugger Break', 'Parser Error', 'Parse Error', 'SCRIPT ERROR'])
        write_text(os.path.join(out_dir, f'prewarm-{stage}.txt'), output)
        steps.append({'stage': stage, 'rc': rc,
                      'elapsed_sec': round(time.monotonic() - started, 3)})
        write_text(os.path.join(out_dir, 'prewarm-summary.json'),
                   json.dumps({'steps': steps, 'rc': rc}, indent=2))
        print(f'GDUNIT_PREWARM stage={stage} rc={rc} elapsed_sec={steps[-1]["elapsed_sec"]}')
        if rc != 0:
            return rc
    return 0


def ensure_tests_project_junction(repo_root: str, project_abs: str, out_dir: str) -> None:
    """
    Hard gate: ensure Tests.Godot/Game.Godot is a Junction to the real Game.Godot.

    This prevents drift between test resources and the actual game project.
    """
    try:
        proj_name = os.path.basename(os.path.normpath(project_abs))
        if proj_name != "Tests.Godot":
            return

        # Only enforce when the project is within repo root.
        try:
            common = os.path.commonpath([os.path.abspath(repo_root), os.path.abspath(project_abs)])
        except ValueError:
            return
        if os.path.abspath(common) != os.path.abspath(repo_root):
            return

        ensure_script = os.path.join(repo_root, "scripts", "python", "ensure_tests_godot_junction.py")
        if not os.path.isfile(ensure_script):
            raise RuntimeError("ensure_tests_godot_junction_script_missing")

        rel_project = os.path.relpath(project_abs, repo_root)
        cmd = [
            sys.executable,
            ensure_script,
            "--root",
            repo_root,
            "--tests-project",
            rel_project,
            "--link-name",
            "Game.Godot",
            "--target-rel",
            "Game.Godot",
            "--create-if-missing",
            "--fix-wrong-target",
        ]
        rc, out = run_cmd(cmd, cwd=repo_root, timeout=60_000)
        try:
            write_text(os.path.join(out_dir, "ensure-tests-godot-junction.txt"), out)
        except Exception:
            pass
        if rc != 0:
            raise RuntimeError("ensure_tests_godot_junction_failed")
    except Exception:
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--godot-bin', required=True)
    ap.add_argument('--project', default='Tests.Godot')
    ap.add_argument('--add', action='append', default=[], help='Add directory or suite path(s). E.g., tests/Adapters or res://tests/Adapters')
    ap.add_argument('--timeout-sec', type=int, default=600, help='Timeout seconds for test run (default 600)')
    ap.add_argument('--prewarm', action='store_true', help='Prewarm: build solutions before running tests')
    ap.add_argument('--rd', dest='report_dir', default=None, help='Custom destination to copy reports into (defaults to logs/e2e/<date>/gdunit-reports)')
    args = ap.parse_args()

    root = os.getcwd()
    proj = os.path.abspath(args.project)
    date = dt.date.today().strftime('%Y-%m-%d')
    out_dir = os.path.join(root, 'logs', 'e2e', date)
    os.makedirs(out_dir, exist_ok=True)

    # Hard gate before any Godot invocation.
    ensure_tests_project_junction(repo_root=root, project_abs=proj, out_dir=out_dir)

    # Import and build are separate bounded stages; failures stop before tests.
    prewarm_rc = None
    prewarm_note = None
    if args.prewarm:
        prewarm_rc = prewarm_project(args.godot_bin, proj, out_dir)
        prewarm_attempts = 1
        prewarm_note = 'import-then-build'
        if prewarm_rc != 0:
            return prewarm_rc

    # Discard stale reports before this invocation; only fresh evidence can pass.
    reports_dir = os.path.join(proj, 'reports')
    if os.path.isdir(reports_dir):
        shutil.rmtree(reports_dir)

    # Run tests (Debugger break, fail-fast).
    # Build command with optional -a filters
    cmd = [args.godot_bin, '--headless', '--path', proj, '--debug', '--script', 'res://addons/gdUnit4/bin/GdUnitCmdTool.gd', '--ignoreHeadlessMode']
    for a in args.add:
        apath = a
        if not apath.startswith('res://'):
            # normalize relative tests path to res://
            apath = 'res://' + apath.replace('\\', '/').lstrip('/')
        cmd += ['-a', apath]
    rc, out = run_cmd_failfast(cmd, cwd=proj, timeout=args.timeout_sec*1000)
    console_path = os.path.join(out_dir, 'gdunit-console.txt')
    with open(console_path, 'w', encoding='utf-8') as f:
        f.write(out)

    # Generate HTML log frame (optional)
    _rc2, _out2 = run_cmd([args.godot_bin, '--headless', '--path', proj, '--quiet', '-s', 'res://addons/gdUnit4/bin/GdUnitCopyLog.gd', '--quit'], cwd=proj, timeout=30_000)

    # Archive reports
    reports_dir = os.path.join(proj, 'reports')
    dest = args.report_dir if args.report_dir else os.path.join(out_dir, 'gdunit-reports')
    # Always create a destination folder with at least the console log and a summary
    if os.path.isdir(dest):
        shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest, exist_ok=True)
    # Copy console log for diagnosis
    try:
        shutil.copy2(console_path, os.path.join(dest, 'gdunit-console.txt'))
    except Exception:
        pass
    # Copy reports if they exist
    if os.path.isdir(reports_dir):
        for name in os.listdir(reports_dir):
            src = os.path.join(reports_dir, name)
            dst = os.path.join(dest, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    parsed = {}
    latest_results = _find_latest_results_xml(reports_dir)
    if latest_results:
        parsed = _parse_results_xml(latest_results)

    strict_exit = (os.environ.get("GDUNIT_STRICT_EXIT_CODE") or "0").strip() == "1"
    valid_results = bool(parsed and parsed.get("tests", 0) > 0 and
                         parsed.get("failures") == 0 and parsed.get("errors") == 0)
    normalized_rc = rc if rc != 0 else (0 if valid_results else 1)
    # A timeout or parser failure is never normalized into success.
    if not strict_exit and rc not in (0, 1, 124) and valid_results:
        normalized_rc = 0

    # Write a small summary json for CI
    summary = {
        'rc': rc,
        'normalized_rc': normalized_rc,
        'strict_exit_code': strict_exit,
        'project': proj,
        'added': args.add,
        'timeout_sec': args.timeout_sec,
        'results': parsed,
    }
    if prewarm_rc is not None:
        summary['prewarm_rc'] = prewarm_rc
        if prewarm_note:
            summary['prewarm_note'] = prewarm_note
        try:
            summary['prewarm_attempts'] = prewarm_attempts
        except NameError:
            pass
    try:
        with open(os.path.join(dest, 'run-summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False)
    except Exception:
        pass
    print(f'GDUNIT_DONE rc={rc} out={out_dir}')
    return 0 if normalized_rc == 0 else normalized_rc


if __name__ == '__main__':
    raise SystemExit(main())
