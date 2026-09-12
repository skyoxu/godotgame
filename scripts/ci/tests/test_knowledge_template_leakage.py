from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class TemplateBusinessLeakageTests(unittest.TestCase):
    def test_knowledge_impact_template_scope_has_no_sibling_business_identifiers(self):
        forbidden = [
            "new" + "rouge",
            "PRD-" + "NEWROUGE",
            "Reward" + ".tscn",
            "Reward" + "Service",
            "reward" + ".basic",
        ]
        roots = [
            ROOT / "scripts/python",
            ROOT / "scripts/ci/tests",
            ROOT / "knowledge",
            ROOT / "docs/knowledge",
            ROOT / ".agents/skills",
        ]
        explicit_files = [
            ROOT / "workflow.md",
            ROOT / ".github/workflows/publish-knowledge-catalog.yml",
        ]
        paths: list[Path] = []
        for base in roots:
            if base.exists():
                paths.extend(path for path in base.rglob("*") if path.is_file())
        paths.extend(path for path in explicit_files if path.is_file())

        violations: list[str] = []
        self_path = Path(__file__).resolve()
        for path in sorted(set(paths)):
            if path.resolve() == self_path:
                continue
            if path.suffix.casefold() in {".png", ".jpg", ".jpeg", ".webp", ".zip", ".dll", ".exe"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            folded = text.casefold()
            for token in forbidden:
                if token.casefold() in folded:
                    violations.append(f"{path.relative_to(ROOT).as_posix()}: {token}")
        self.assertFalse(violations, "business-specific identifiers leaked into template scope:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
