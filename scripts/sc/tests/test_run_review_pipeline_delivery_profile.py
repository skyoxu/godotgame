#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / 'scripts' / 'sc' / 'run_review_pipeline.py'


def _extract_out_dir(output: str) -> Path:
    match = re.search(r'\bout=([^\r\n]+)', output or '')
    if not match:
        raise AssertionError(f'missing out=... in output:\n{output}')
    return Path(match.group(1).strip())


class RunReviewPipelineDeliveryProfileTests(unittest.TestCase):
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
