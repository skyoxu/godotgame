"""Regression cases for ADR-0005/ADR-0018 CI success criteria."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts/python'))
import ci_change_scope
import godot_selfcheck
import run_gdunit


class ScopeTests(unittest.TestCase):
    def test_import_boundary_change_requires_export(self):
        self.assertTrue(ci_change_scope.needs_export(['Game.Godot/.gdignore']))

    def test_runtime_resources_are_not_ignored(self):
        self.assertFalse((ROOT / 'Game.Godot/.gdignore').exists())
        self.assertTrue((ROOT / 'docs/.gdignore').exists())
        self.assertTrue((ROOT / 'logs/.gdignore').exists())

    def test_documentation_only_can_skip_runtime(self):
        self.assertFalse(ci_change_scope.needs_runtime(['README.md', 'docs/adr/example.md']))

    def test_code_configuration_and_unknown_files_run_runtime(self):
        for path in ['Game.Core/Game.cs', 'Game.Godot/help.md', 'project.godot', '.github/actions/setup/action.yml', 'assets/a.png', 'scripts/tool.py']:
            with self.subTest(path=path):
                self.assertTrue(ci_change_scope.needs_runtime(['README.md', path]))


class SelfCheckTests(unittest.TestCase):
    def check_payload(self, payload, exit_code=0):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            project = root / 'project.godot'
            project.touch()
            evidence = root / 'evidence.json'
            evidence.write_text(json.dumps(payload), encoding='utf-8')
            with patch.object(godot_selfcheck, 'run_cmd', return_value=(exit_code, f'SELF_CHECK_OUT:{evidence}\n', '')):
                return godot_selfcheck.run_selfcheck('godot', str(project), False)

    def test_all_required_ports_pass(self):
        ports = {k: True for k in ['time', 'input', 'resourceLoader', 'dataStore', 'logger', 'eventBus']}
        self.assertEqual('ok', self.check_payload({'ports': ports})['status'])

    def test_missing_false_or_malformed_ports_fail(self):
        for ports in [{}, {'time': True}, {'time': False}, [], None]:
            with self.subTest(ports=ports):
                self.assertEqual('fail', self.check_payload({'ports': ports})['status'])

    def test_process_failure_rejects_valid_json(self):
        ports = {k: True for k in ['time', 'input', 'resourceLoader', 'dataStore', 'logger', 'eventBus']}
        self.assertEqual('fail', self.check_payload({'ports': ports}, 1)['status'])

    def test_build_failure_stops_before_selfcheck(self):
        with tempfile.TemporaryDirectory() as td, patch.object(godot_selfcheck, 'run_cmd', return_value=(1, '', 'build failed')) as run:
            result = godot_selfcheck.run_selfcheck('godot', str(Path(td) / 'project.godot'), True)
            self.assertEqual('fail', result['status'])
            self.assertEqual(1, run.call_count)


class GdUnitProcessTests(unittest.TestCase):
    def test_prewarm_imports_before_build_and_records_each_stage(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / 'Tests.Godot.csproj').touch()
            with patch.object(run_gdunit, 'run_cmd_failfast', side_effect=[(0, 'imported'), (0, 'built')]) as run:
                self.assertEqual(0, run_gdunit.prewarm_project('godot', td, td))
            self.assertIn('--import', run.call_args_list[0].args[0])
            self.assertEqual(['dotnet', 'build'], run.call_args_list[1].args[0][:2])
            report = json.loads((Path(td) / 'prewarm-summary.json').read_text(encoding='utf-8'))
            self.assertEqual(['import', 'build'], [s['stage'] for s in report['steps']])
            self.assertEqual('imported', (Path(td) / 'prewarm-import.txt').read_text(encoding='utf-8'))

    def test_prewarm_failure_does_not_retry_or_run_later_stages(self):
        for results in [[(124, 'timeout')], [(1, 'parse error')], [(0, 'imported'), (7, 'build failed')]]:
            with self.subTest(results=results), tempfile.TemporaryDirectory() as td:
                (Path(td) / 'Tests.Godot.csproj').touch()
                with patch.object(run_gdunit, 'run_cmd_failfast', side_effect=results) as run:
                    self.assertEqual(results[-1][0], run_gdunit.prewarm_project('godot', td, td))
                self.assertEqual(len(results), run.call_count)
                report = json.loads((Path(td) / 'prewarm-summary.json').read_text(encoding='utf-8'))
                self.assertEqual(results[-1][0], report['rc'])

    def test_prewarm_gdscript_project_needs_no_dotnet(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(run_gdunit, 'run_cmd_failfast', return_value=(0, 'imported')) as run:
                self.assertEqual(0, run_gdunit.prewarm_project('godot', td, td))
                self.assertEqual(1, run.call_count)

    def test_prewarm_rejects_ambiguous_build_target(self):
        with tempfile.TemporaryDirectory() as td:
            for name in ['One.csproj', 'Two.csproj']:
                (Path(td) / name).touch()
            with patch.object(run_gdunit, 'run_cmd_failfast') as run:
                self.assertEqual(2, run_gdunit.prewarm_project('godot', td, td))
                run.assert_not_called()

    def test_silent_process_obeys_deadline(self):
        start = time.monotonic()
        rc, _ = run_gdunit.run_cmd_failfast([sys.executable, '-c', 'import time; time.sleep(20)'], timeout=200)
        self.assertEqual(124, rc)
        self.assertLess(time.monotonic() - start, 5)

    def test_nonzero_exit_is_preserved(self):
        rc, _ = run_gdunit.run_cmd_failfast([sys.executable, '-c', 'raise SystemExit(7)'])
        self.assertEqual(7, rc)

    def test_parser_error_fails_early(self):
        rc, output = run_gdunit.run_cmd_failfast([sys.executable, '-u', '-c', 'import time; print("SCRIPT ERROR: broken"); time.sleep(20)'])
        self.assertEqual(1, rc)
        self.assertIn('SCRIPT ERROR', output)


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell runtime is verified on Windows CI')
class PowerShellTests(unittest.TestCase):
    def test_changed_scripts_parse(self):
        script = r'''
$ErrorActionPreference = 'Stop'
foreach ($path in @('smoke_process.ps1', 'smoke_exe.ps1', 'smoke_headless.ps1', 'export_windows.ps1', 'install_export_templates.ps1')) {
  $tokens = $null; $errors = $null
  $null = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $env:TEST_ROOT "scripts/ci/$path"), [ref]$tokens, [ref]$errors)
  if ($errors.Count) { throw ($errors | Out-String) }
}
'''
        result = self.run_ps(script, ROOT)
        self.assertEqual(0, result.returncode, result.stdout)

    def run_ps(self, source, directory, extra=None):
        path = Path(directory) / 'driver.ps1'
        path.write_text(source, encoding='utf-8')
        try:
            env = dict(os.environ, TEST_ROOT=str(ROOT), PYTHON_EXE=sys.executable, **(extra or {}))
            return subprocess.run(['pwsh', '-NoProfile', '-File', str(path)], cwd=directory, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', timeout=30)
        finally:
            path.unlink(missing_ok=True)

    def test_smoke_rejects_errors_empty_logs_and_failed_exit(self):
        cases = [
            ('print("[TEMPLATE_SMOKE_READY]")', True),
            ('print("[TEMPLATE_SMOKE_READY]"); raise SystemExit(1)', False),
            ('print("[TEMPLATE_SMOKE_READY]\\nERROR: broken")', False),
            ('print("[DB] opened")', False),
            ('pass', False),
            ('import time; print("[TEMPLATE_SMOKE_READY]", flush=True); time.sleep(20)', True),
        ]
        for code, passed in cases:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                Path(td, 'fake.py').write_text(code, encoding='utf-8')
                result = self.run_ps('''
$ErrorActionPreference = 'Stop'
. "$env:TEST_ROOT/scripts/ci/smoke_process.ps1"
Invoke-SmokeProcess -Executable $env:PYTHON_EXE -Arguments @('fake.py') -WorkingDirectory (Get-Location).Path -TimeoutSec 1
''', td)
                self.assertEqual(passed, result.returncode == 0, result.stdout)

    def test_export_requires_fresh_release_executable_and_zero_exit(self):
        for scenario, passed in [('success', True), ('failure_with_file', False), ('stale', False), ('timeout', False)]:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / 'scripts/ci').mkdir(parents=True)
                shutil.copy2(ROOT / 'scripts/ci/export_windows.ps1', root / 'scripts/ci/export_windows.ps1')
                (root / 'Game.sln').touch()
                (root / 'godot.exe').touch()
                (root / 'build').mkdir()
                (root / 'build/Game.exe').write_bytes(b'stale')
                source = r'''
$ErrorActionPreference = 'Stop'
function Start-Process {
  param($FilePath, $ArgumentList, [switch]$PassThru, $WorkingDirectory, $RedirectStandardOutput, $RedirectStandardError, $WindowStyle)
  [System.IO.File]::WriteAllText($RedirectStandardOutput, 'export log')
  [System.IO.File]::WriteAllText($RedirectStandardError, '')
  if ($env:EXPORT_CASE -in @('success', 'failure_with_file')) {
    [System.IO.File]::WriteAllText((Join-Path $WorkingDirectory 'build/Game.exe'), 'fresh export')
  }
  $code = if ($env:EXPORT_CASE -eq 'failure_with_file') { 1 } else { 0 }
  $process = [pscustomobject]@{ ExitCode = $code; Id = 2147483647 }
  $process | Add-Member ScriptMethod WaitForExit { param($timeout) return ($env:EXPORT_CASE -ne 'timeout') }
  return $process
}
& './scripts/ci/export_windows.ps1' -GodotBin './godot.exe' -Output 'build/Game.exe'
exit $LASTEXITCODE
'''
                result = self.run_ps(source, td, {'EXPORT_CASE': scenario})
                self.assertEqual(passed, result.returncode == 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
