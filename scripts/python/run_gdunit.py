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

    # Optional prewarm
    if args.prewarm:
        _rcp, _outp = run_cmd([args.godot_bin, '--headless', '--path', proj, '--build-solutions', '--quit'], cwd=proj, timeout=300_000)

    # Run tests
    # Build command with optional -a filters
    cmd = [args.godot_bin, '--headless', '--path', proj, '-s', '-d', 'res://addons/gdUnit4/bin/GdUnitCmdTool.gd', '--ignoreHeadlessMode']
    for a in args.add:
        apath = a
        if not apath.startswith('res://'):
            # normalize relative tests path to res://
            apath = 'res://' + apath.replace('\\', '/').lstrip('/')
        cmd += ['-a', apath]
    rc, out = run_cmd(cmd, cwd=proj, timeout=args.timeout_sec*1000)
    with open(os.path.join(out_dir, 'gdunit-console.txt'), 'w', encoding='utf-8') as f:
        f.write(out)

    # Generate HTML log frame (optional)
    _rc2, _out2 = run_cmd([args.godot_bin, '--headless', '--path', proj, '--quiet', '-s', 'res://addons/gdUnit4/bin/GdUnitCopyLog.gd'], cwd=proj)

    # Archive reports
    reports_dir = os.path.join(proj, 'reports')
    if os.path.isdir(reports_dir):
        dest = args.report_dir if args.report_dir else os.path.join(out_dir, 'gdunit-reports')
        if os.path.isdir(dest):
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(reports_dir, dest)
    print(f'GDUNIT_DONE rc={rc} out={out_dir}')
    return 0 if rc == 0 else rc


if __name__ == '__main__':
    raise SystemExit(main())
