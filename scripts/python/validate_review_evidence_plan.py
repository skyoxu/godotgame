#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _review_evidence_plan_contract import (
    PHASE_PREDECESSORS,
    adversarial_contract_errors,
    compatibility_contract_errors,
    core_policy_errors,
    ledger_status_errors,
    phase_contract_errors,
    profile_contract_errors,
    schema_contract_errors,
)
from _review_evidence_source_audit import check_source_audit

PLAN_NAME = "2026-07-12-phase-review-evidence-gate-hardening-execution-plan"
REQUIRED_BOOKS = {
    "00-index.md", "01-authority-scope-and-invariants.md", "02-review-evidence-contracts-and-severity.md",
    "03-chapter3-5-evidence-profiles.md", "04-chapter6-review-ingestion-and-residual-closure.md", "05-chapter7-ui-review-evidence.md",
    "06-pipeline-integration-recovery-and-compatibility.md", "07-observability-replay-and-performance.md", "08-implementation-phases.md",
    "09-risks-dod-and-glossary.md", "96-global-review-and-split-validation.md", "97-post-split-requirements-ledger.md", "98-research-to-split-audit.md", "99-source-coverage.md",
}
REQUIRED_HEADINGS = {
    "00-index.md": {"Authority", "Reading Order", "Required Schemas"},
    "01-authority-scope-and-invariants.md": {"Global Invariants", "Trust Model", "Acceptance"},
    "02-review-evidence-contracts-and-severity.md": {"Severity Normalization", "Verdict Derivation", "Acceptance"},
    "03-chapter3-5-evidence-profiles.md": {"Chapter 3: Task Triplet Planning", "Chapter 5: Semantics Stabilization", "Acceptance"},
    "04-chapter6-review-ingestion-and-residual-closure.md": {"Parser And Validator", "Residual Closure Correctness", "Acceptance"},
    "05-chapter7-ui-review-evidence.md": {"Visual Findings", "False-Positive Exclusions", "Acceptance"},
    "06-pipeline-integration-recovery-and-compatibility.md": {"Backward Compatibility", "Rollback", "Acceptance"},
    "07-observability-replay-and-performance.md": {"Replay Corpus", "Retention", "Acceptance"},
    "08-implementation-phases.md": {"Mandatory Sequential Dependency Matrix", "Phase RG-0: Policy, ADR, Schema, And Ownership Freeze"},
    "09-risks-dod-and-glossary.md": {"Global Definition Of Done", "Review Stop Conditions"},
    "96-global-review-and-split-validation.md": {"Required RG-0 Validator", "Historical Whole-Directory Finding Ledger", "Acceptance"}, "97-post-split-requirements-ledger.md": {"Requirements", "Requirement Status Registry", "Acceptance"},
    "98-research-to-split-audit.md": {"Source Range Registry", "Audit Result"}, "99-source-coverage.md": {"Explicit Requirement Coverage", "Research Source Range Coverage", "Completion"},
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.rule_id} {self.path}: {self.message}"

def _add(findings: list[Finding], rule_id: str, path: Path | str, message: str) -> None:
    findings.append(Finding(rule_id, str(path).replace("\\", "/"), message))

def _read_utf8(path: Path, findings: list[Finding], rule_id: str) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        _add(findings, rule_id, path, f"file is not readable UTF-8: {exc}")
        return None

def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]

def _slug(value: str) -> str:
    value = re.sub(r"[`*_]", "", value.strip().lower())
    value = re.sub(r"[^\w\-\s]", "", value, flags=re.UNICODE)
    return re.sub(r"[\s]+", "-", value).strip("-")

def _headings(text: str) -> dict[str, int]:
    return {_slug(match.group(2)): index for index, match in enumerate(HEADING_RE.finditer(text), start=1)}

def _check_books(plan_dir: Path, findings: list[Finding]) -> None:
    actual = {path.name for path in plan_dir.glob("*.md")}
    for name in sorted(REQUIRED_BOOKS - actual):
        _add(findings, "RGE-PLAN-001", plan_dir / name, "required book is missing")
    for name in sorted(actual - REQUIRED_BOOKS):
        _add(findings, "RGE-PLAN-001", plan_dir / name, "unexpected Markdown book")

def _check_links(root: Path, markdown_files: list[Path], findings: list[Finding]) -> None:
    for path in markdown_files:
        text = _read_utf8(path, findings, "RGE-PLAN-002")
        if text is None:
            continue
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            file_part, _, anchor = target.partition("#")
            resolved = path if not file_part else (path.parent / file_part).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                _add(findings, "RGE-PLAN-002", path, f"link escapes repository: {target}")
                continue
            if not resolved.exists():
                _add(findings, "RGE-PLAN-002", path, f"link target does not exist: {target}")
                continue
            if anchor and resolved.suffix.lower() == ".md":
                target_text = _read_utf8(resolved, findings, "RGE-PLAN-002")
                if target_text is None:
                    continue
                target_headings = _headings(target_text)
                if anchor.lower() not in target_headings:
                    _add(findings, "RGE-PLAN-002", path, f"link anchor does not exist: {target}")


def _check_headings(plan_dir: Path, findings: list[Finding]) -> None:
    for name, required in REQUIRED_HEADINGS.items():
        path = plan_dir / name
        if not path.exists():
            continue
        text = _read_utf8(path, findings, "RGE-PLAN-003")
        if text is None:
            continue
        present = {match.group(2).strip() for match in HEADING_RE.finditer(text)}
        for heading in sorted(required - present):
            _add(findings, "RGE-PLAN-003", path, f"required heading is missing: {heading}")


def _parse_active_requirements(path: Path, findings: list[Finding]) -> dict[str, str]:
    active: dict[str, str] = {}
    seen: set[str] = set()
    if not path.exists():
        return active
    in_requirements = False
    text = _read_utf8(path, findings, "RGE-PLAN-004")
    if text is None:
        return active
    for line in text.splitlines():
        if line == "## Requirements":
            in_requirements = True
            continue
        if in_requirements and line.startswith("## "):
            break
        if not in_requirements:
            continue
        if not line.startswith("| RGR-"):
            continue
        cells = _table_cells(line)
        if len(cells) != 7:
            _add(findings, "RGE-PLAN-004", path, f"ledger row must have seven fields: {line}")
            continue
        req_id, status, owner, phase, _, acceptance, test_intent = cells
        if req_id in seen:
            _add(findings, "RGE-PLAN-004", path, f"duplicate requirement ID: {req_id}")
        seen.add(req_id)
        if status not in {"Active", "Closed", "Superseded"}:
            _add(findings, "RGE-PLAN-004", path, f"{req_id} has invalid status: {status}")
        if status in {"Active", "Closed"}:
            active[req_id] = owner
            if owner not in {name[:2] for name in REQUIRED_BOOKS}:
                _add(findings, "RGE-PLAN-004", path, f"{req_id} has invalid owner book: {owner}")
            if phase not in PHASE_PREDECESSORS:
                _add(findings, "RGE-PLAN-004", path, f"{req_id} has invalid phase: {phase}")
            if not LINK_RE.search(acceptance) or "#" not in acceptance:
                _add(findings, "RGE-PLAN-004", path, f"{req_id} lacks an acceptance reference")
            if not test_intent or test_intent.lower() in {"n/a", "none"}:
                _add(findings, "RGE-PLAN-004", path, f"{req_id} lacks test/evidence intent")
    for message in ledger_status_errors(text):
        _add(findings, "RGE-PLAN-004", path, message)
    return active


def _check_requirement_coverage(path: Path, active: dict[str, str], findings: list[Finding]) -> None:
    if not path.exists():
        return
    coverage: dict[str, str] = {}
    in_section = False
    text = _read_utf8(path, findings, "RGE-PLAN-005")
    if text is None:
        return
    for line in text.splitlines():
        if line == "## Explicit Requirement Coverage":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not re.match(r"^\| \d{2} \|", line):
            continue
        cells = _table_cells(line)
        if len(cells) != 2:
            _add(findings, "RGE-PLAN-005", path, f"coverage row must have two fields: {line}")
            continue
        owner, ids = cells
        for req_id in re.findall(r"RGR-\d{3}", ids):
            if req_id in coverage:
                _add(findings, "RGE-PLAN-005", path, f"requirement covered more than once: {req_id}")
            coverage[req_id] = owner
    for req_id in sorted(set(active) ^ set(coverage)):
        _add(findings, "RGE-PLAN-005", path, f"active/coverage mismatch: {req_id}")
    for req_id in sorted(set(active) & set(coverage)):
        if active[req_id] != coverage[req_id]:
            _add(findings, "RGE-PLAN-005", path, f"owner mismatch for {req_id}: {active[req_id]} != {coverage[req_id]}")


def _check_source_audit(root: Path, plan_dir: Path, findings: list[Finding]) -> None:
    check_source_audit(root, plan_dir, lambda path, message: _add(findings, "RGE-PLAN-006", path, message))


def _check_schema(root: Path, plan_dir: Path, findings: list[Finding]) -> None:
    schema_path = root / "scripts/sc/schemas/review-evidence.v1.schema.json"
    example_path = plan_dir / "schemas/review-evidence.v1.example.json"
    pointer_path = plan_dir / "schemas/review-evidence.v1.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        example = json.loads(example_path.read_text(encoding="utf-8"))
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _add(findings, "RGE-PLAN-007", schema_path, f"schema/example is not parseable: {exc}")
        return
    if not isinstance(schema, dict) or not isinstance(example, dict) or not isinstance(pointer, dict):
        _add(findings, "RGE-PLAN-007", schema_path, "schema, pointer, and example must be JSON objects")
        return
    for target, message in schema_contract_errors(schema, pointer):
        _add(findings, "RGE-PLAN-008" if target == "pointer" else "RGE-PLAN-007", pointer_path if target == "pointer" else schema_path, message)
    sc_dir = root / "scripts" / "sc"
    if str(sc_dir) not in sys.path:
        sys.path.insert(0, str(sc_dir))
    from _review_evidence_schema_fallback import validate_review_evidence_without_jsonschema
    errors = validate_review_evidence_without_jsonschema(example)
    if errors:
        _add(findings, "RGE-PLAN-007", example_path, errors[0])
    try:
        import jsonschema  # type: ignore
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
        except jsonschema.SchemaError as exc:
            _add(findings, "RGE-PLAN-007", schema_path, f"canonical schema is invalid: {exc.message}")
            return
        primary_errors = list(jsonschema.Draft202012Validator(schema).iter_errors(example))
        if primary_errors:
            _add(findings, "RGE-PLAN-007", example_path, primary_errors[0].message)
    except ImportError:
        pass


def _check_compatibility(root: Path, path: Path, findings: list[Finding]) -> None:
    adr_path = root / "docs/adr/ADR-0032-review-evidence-gate.md"
    if not path.exists():
        return
    adr_text = adr_path.read_text(encoding="utf-8") if adr_path.exists() else ""
    for message in compatibility_contract_errors(adr_text=adr_text, compatibility_text=path.read_text(encoding="utf-8")):
        _add(findings, "RGE-PLAN-009", adr_path if message.startswith("ADR") else path, message)


def _check_history(path: Path, findings: list[Finding]) -> None:
    if not path.exists():
        return
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| RG-WDR-"):
            continue
        cells = _table_cells(line)
        if len(cells) != 7:
            _add(findings, "RGE-PLAN-010", path, "historical finding row must have seven fields")
            continue
        finding_id, severity, status, owner, expiry, recheck, closure = cells
        if finding_id in seen or severity not in {"P0", "P1", "P2"} or status not in {"Open", "Closed", "Superseded"}:
            _add(findings, "RGE-PLAN-010", path, f"invalid historical finding identity/state: {finding_id}")
        seen.add(finding_id)
        if status == "Open" and (not owner or expiry.lower() == "n/a" or not recheck):
            _add(findings, "RGE-PLAN-010", path, f"Open finding lacks owner, expiry, or recheck: {finding_id}")
        if status == "Closed" and (not closure or closure.lower() == "n/a"):
            _add(findings, "RGE-PLAN-010", path, f"Closed finding lacks closure evidence: {finding_id}")


def _check_phases(path: Path, top_path: Path, history_path: Path, findings: list[Finding]) -> None:
    if not path.exists() or not top_path.exists() or not history_path.exists():
        return
    text = path.read_text(encoding="utf-8")
    actual: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\| (RG-(?:HANDOFF|\d)) \| (.+) \|$", line)
        if match:
            actual[match.group(1)] = match.group(2).strip()
    for message in phase_contract_errors(
        phase_text=text,
        top_text=top_path.read_text(encoding="utf-8"),
        history_text=history_path.read_text(encoding="utf-8"),
        actual_predecessors=actual,
    ):
        _add(findings, "RGE-PLAN-011", path, message)


def _check_profile_config(root: Path, findings: list[Finding]) -> None:
    path = root / "scripts/sc/config/delivery_profiles.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _add(findings, "RGE-PLAN-013", path, f"delivery profile config is not parseable: {exc}")
        return
    for message in profile_contract_errors(payload):
        _add(findings, "RGE-PLAN-013", path, message)


def _check_text_contracts(top_path: Path, plan_dir: Path, findings: list[Finding]) -> None:
    names = ["01-authority-scope-and-invariants.md", "02-review-evidence-contracts-and-severity.md",
             "03-chapter3-5-evidence-profiles.md", "04-chapter6-review-ingestion-and-residual-closure.md",
             "96-global-review-and-split-validation.md"]
    paths = [plan_dir / name for name in names]
    if not top_path.exists() or any(not path.exists() for path in paths):
        return
    texts = [path.read_text(encoding="utf-8") for path in paths]
    for target, message in core_policy_errors(authority=texts[0], chapter6=texts[3]):
        _add(findings, "RGE-PLAN-014", paths[0] if target == "authority" else paths[3], message)
    for message in adversarial_contract_errors(
        top=top_path.read_text(encoding="utf-8"),
        book02=texts[1], book03=texts[2], book04=texts[3], book96=texts[4],
    ):
        _add(findings, "RGE-PLAN-015", top_path, message)


def validate_plan(root: Path) -> list[Finding]:
    root = root.resolve()
    plan_dir = root / "execution-plans" / PLAN_NAME
    top_path = root / "execution-plans" / f"{PLAN_NAME}.md"
    findings: list[Finding] = []
    if not plan_dir.is_dir() or not top_path.exists():
        _add(findings, "RGE-PLAN-001", plan_dir, "plan directory or top-level recovery file is missing")
        return findings
    try:
        _check_books(plan_dir, findings)
        markdown_files = [top_path, *sorted(plan_dir.glob("*.md"))]
        _check_links(root, markdown_files, findings)
        _check_headings(plan_dir, findings)
        active = _parse_active_requirements(plan_dir / "97-post-split-requirements-ledger.md", findings)
        _check_requirement_coverage(plan_dir / "99-source-coverage.md", active, findings)
        _check_source_audit(root, plan_dir, findings)
        _check_schema(root, plan_dir, findings)
        _check_compatibility(root, plan_dir / "06-pipeline-integration-recovery-and-compatibility.md", findings)
        _check_history(plan_dir / "96-global-review-and-split-validation.md", findings)
        _check_phases(plan_dir / "08-implementation-phases.md", top_path, plan_dir / "96-global-review-and-split-validation.md", findings)
        _check_profile_config(root, findings)
        _check_text_contracts(top_path, plan_dir, findings)
        if "- Status: active" not in top_path.read_text(encoding="utf-8"):
            _add(findings, "RGE-PLAN-012", top_path, "implementation plan must be active during RG-0")
    except (OSError, UnicodeError) as exc:
        _add(findings, "RGE-PLAN-001", getattr(exc, "filename", plan_dir) or plan_dir, f"control input is unreadable: {exc}")
    return sorted(findings, key=lambda item: (item.rule_id, item.path, item.message))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Review Evidence Gate split execution plan.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    findings = validate_plan(args.root)
    if findings:
        for finding in findings:
            print(finding.render())
        return 1
    print("OK: review evidence plan validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
