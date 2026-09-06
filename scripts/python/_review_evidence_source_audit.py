from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from pathlib import Path


def check_source_audit(root: Path, plan_dir: Path, add: Callable[[Path, str], None]) -> None:
    audit_path = plan_dir / "98-research-to-split-audit.md"
    coverage_path = plan_dir / "99-source-coverage.md"
    if not audit_path.exists() or not coverage_path.exists():
        return
    try:
        audit = audit_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        add(audit_path, f"source audit document is unreadable: {exc}")
        return
    source_match = re.search(r"Primary source:\s*\n\s*- `([^`]+)`\s*\n\s*- SHA-256: `([0-9a-f]{64})`\s*\n\s*- UTF-8 line count: `(\d+)`", audit)
    if not source_match:
        add(audit_path, "source metadata is missing or malformed")
        return
    source_rel, expected_hash, expected_count = source_match.groups()
    source_path = (root / source_rel).resolve()
    try:
        source_path.relative_to(root.resolve())
    except ValueError:
        add(source_path, "frozen research source escapes repository root")
        return
    if not source_path.is_file():
        add(source_path, "frozen research source is missing or not a file")
        return
    try:
        source_bytes = source_path.read_bytes()
        source_text = source_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        add(source_path, f"frozen research source is unreadable: {exc}")
        return
    line_count = len(source_text.splitlines())
    if hashlib.sha256(source_bytes).hexdigest() != expected_hash or line_count != int(expected_count):
        add(source_path, "hash or line count differs from book 98")

    ranges: list[tuple[str, int, int]] = []
    for line in audit.splitlines():
        match = re.match(r"^\| (SRC-\d{3}) \| (\d+)-(\d+) \|", line)
        if match:
            ranges.append((match.group(1), int(match.group(2)), int(match.group(3))))
    expected_start = 1
    for source_id, start, end in ranges:
        if start != expected_start or end < start:
            add(audit_path, f"non-contiguous source range: {source_id} {start}-{end}")
        expected_start = end + 1
    if not ranges or expected_start - 1 != line_count:
        add(audit_path, "source ranges do not cover the complete source")

    covered: list[str] = []
    in_section = False
    try:
        coverage_text = coverage_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        add(coverage_path, f"source coverage document is unreadable: {exc}")
        return
    for line in coverage_text.splitlines():
        if line == "## Research Source Range Coverage":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        match = re.match(r"^\| (SRC-\d{3}) \|", line) if in_section else None
        if match:
            covered.append(match.group(1))
    expected_ids = [item[0] for item in ranges]
    if sorted(covered) != sorted(expected_ids) or len(covered) != len(set(covered)):
        add(coverage_path, "source IDs must be covered exactly once")
    for line_number, line in enumerate(source_text.splitlines(), start=1):
        if re.match(r"^#{2,4}\s+", line):
            matches = sum(1 for _, start, end in ranges if start <= line_number <= end)
            if matches != 1:
                add(source_path, f"heading at line {line_number} belongs to {matches} ranges")
