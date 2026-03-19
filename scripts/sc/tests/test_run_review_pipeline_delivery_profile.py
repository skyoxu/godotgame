#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'scripts' / 'sc' / 'run_review_pipeline.py'
SC_DIR = REPO_ROOT / 'scripts' / 'sc'
sys.path.insert(0, str(SC_DIR))

import run_review_pipeline as run_review_pipeline_module  # noqa: E402


def _extract_out_dir(output: str) -> Path:
    match = re.search(r'\bout=([^\r\n]+)', output or '')
    if not match:
        raise AssertionError(f'missing out=... in output:\n{output}')
    return Path(match.group(1).strip())


class RunReviewPipelineDeliveryProfileTests(unittest.TestCase):
    def test_agent_review_needs_fix_should_not_change_producer_summary_status(self) -> None:
        run_id = uuid.uuid4().hex
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            out_dir = tmp_root / f'sc-review-pipeline-task-1-{run_id}'
            latest_path = tmp_root / 'sc-review-pipeline-task-1' / 'latest.json'
            payload = {
                'schema_version': '1.0.0',
                'cmd': 'sc-agent-review',
                'date': '2026-03-19',
                'reviewer': 'artifact-reviewer',
                'task_id': '1',
                'run_id': run_id,
                'pipeline_out_dir': str(out_dir),
                'pipeline_status': 'ok',
                'failed_step': '',
                'review_verdict': 'needs-fix',
                'findings': [
                    {
                        'finding_id': 'llm-code-reviewer-needs-fix',
                        'severity': 'medium',
                        'category': 'llm-review',
                        'owner_step': 'sc-llm-review',
                        'evidence_path': 'logs/ci/fake/review.md',
                        'message': 'code-reviewer reported needs fix',
                        'suggested_fix': 'rerun llm review after addressing findings',
                        'commands': [],
                    }
                ],
            }
            argv = [
                str(SCRIPT),
                '--task-id',
                '1',
                '--run-id',
                run_id,
                '--skip-test',
                '--skip-acceptance',
                '--skip-llm-review',
            ]
            with mock.patch.object(sys, 'argv', argv), \
                mock.patch.object(run_review_pipeline_module, '_pipeline_run_dir', return_value=out_dir), \
                mock.patch.object(run_review_pipeline_module, '_pipeline_latest_index_path', return_value=latest_path), \
                mock.patch.object(run_review_pipeline_module, 'write_agent_review', return_value=(payload, [], [])):
                rc = run_review_pipeline_module.main()

            self.assertEqual(0, rc)
            summary = json.loads((out_dir / 'summary.json').read_text(encoding='utf-8'))
            latest = json.loads(latest_path.read_text(encoding='utf-8'))
            hook_log = (out_dir / 'sc-agent-review.log').read_text(encoding='utf-8')

            self.assertEqual('ok', summary['status'])
            self.assertNotIn('agent_review_json_path', latest)
            self.assertNotIn('agent_review_md_path', latest)
            self.assertIn('SC_AGENT_REVIEW status=needs-fix', hook_log)

    def test_skip_all_steps_should_generate_agent_review_sidecar(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), '--task-id', '1', '--skip-test', '--skip-acceptance', '--skip-llm-review'],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
        )
        self.assertEqual(0, proc.returncode, proc.stdout)
        out_dir = _extract_out_dir(proc.stdout or '')
        summary = json.loads((out_dir / 'summary.json').read_text(encoding='utf-8'))
        agent_review = json.loads((out_dir / 'agent-review.json').read_text(encoding='utf-8'))
        latest = json.loads((REPO_ROOT / 'logs' / 'ci' / out_dir.parent.name / 'sc-review-pipeline-task-1' / 'latest.json').read_text(encoding='utf-8'))

        self.assertEqual('ok', summary['status'])
        self.assertEqual('pass', agent_review['review_verdict'])
        self.assertEqual(str(out_dir / 'agent-review.json'), latest['agent_review_json_path'])
        self.assertEqual(str(out_dir / 'agent-review.md'), latest['agent_review_md_path'])

    def test_skip_agent_review_should_not_generate_sidecar_outputs(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), '--task-id', '1', '--skip-test', '--skip-acceptance', '--skip-llm-review', '--skip-agent-review'],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
        )
        self.assertEqual(0, proc.returncode, proc.stdout)
        out_dir = _extract_out_dir(proc.stdout or '')
        latest = json.loads((REPO_ROOT / 'logs' / 'ci' / out_dir.parent.name / 'sc-review-pipeline-task-1' / 'latest.json').read_text(encoding='utf-8'))

        self.assertFalse((out_dir / 'agent-review.json').exists())
        self.assertFalse((out_dir / 'agent-review.md').exists())
        self.assertNotIn('agent_review_json_path', latest)
        self.assertNotIn('agent_review_md_path', latest)

    def test_dry_run_playable_ea_should_relax_acceptance_and_llm_defaults(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), '--task-id', '1', '--delivery-profile', 'playable-ea', '--dry-run', '--skip-test'],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
        )
        self.assertEqual(0, proc.returncode, proc.stdout)
        out_dir = _extract_out_dir(proc.stdout or '')
        summary = json.loads((out_dir / 'summary.json').read_text(encoding='utf-8'))
        execution_context = json.loads((out_dir / 'execution-context.json').read_text(encoding='utf-8'))
        repair_guide = json.loads((out_dir / 'repair-guide.json').read_text(encoding='utf-8'))
        steps = {str(item.get('name')): item for item in (summary.get('steps') or [])}
        acceptance_cmd = steps['sc-acceptance-check']['cmd']
        llm_cmd = steps['sc-llm-review']['cmd']

        self.assertEqual('playable-ea', execution_context['delivery_profile'])
        self.assertEqual('host-safe', execution_context['security_profile'])
        self.assertEqual('not-needed', repair_guide['status'])
        self.assertIn('--security-profile', acceptance_cmd)
        self.assertIn('host-safe', acceptance_cmd)
        self.assertNotIn('--require-executed-refs', acceptance_cmd)
        self.assertNotIn('--require-headless-e2e', acceptance_cmd)
        self.assertIn('--semantic-gate', llm_cmd)
        gate_idx = llm_cmd.index('--semantic-gate') + 1
        self.assertEqual('skip', llm_cmd[gate_idx])

    def test_dry_run_standard_should_keep_strict_acceptance_and_llm_defaults(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), '--task-id', '1', '--delivery-profile', 'standard', '--dry-run', '--skip-test'],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
        )
        self.assertEqual(0, proc.returncode, proc.stdout)
        out_dir = _extract_out_dir(proc.stdout or '')
        summary = json.loads((out_dir / 'summary.json').read_text(encoding='utf-8'))
        execution_context = json.loads((out_dir / 'execution-context.json').read_text(encoding='utf-8'))
        repair_guide = json.loads((out_dir / 'repair-guide.json').read_text(encoding='utf-8'))
        steps = {str(item.get('name')): item for item in (summary.get('steps') or [])}
        acceptance_cmd = steps['sc-acceptance-check']['cmd']
        llm_cmd = steps['sc-llm-review']['cmd']

        self.assertEqual('standard', execution_context['delivery_profile'])
        self.assertEqual('strict', execution_context['security_profile'])
        self.assertEqual('not-needed', repair_guide['status'])
        self.assertIn('--require-executed-refs', acceptance_cmd)
        self.assertIn('--require-headless-e2e', acceptance_cmd)
        self.assertIn('--security-profile', acceptance_cmd)
        self.assertIn('strict', acceptance_cmd)
        gate_idx = llm_cmd.index('--semantic-gate') + 1
        self.assertEqual('require', llm_cmd[gate_idx])


if __name__ == '__main__':
    unittest.main()
