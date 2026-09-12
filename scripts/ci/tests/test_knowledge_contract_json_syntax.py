from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_DIR = ROOT / "knowledge" / "contracts"


class KnowledgeContractJsonSyntaxTests(unittest.TestCase):
    def test_all_contract_json_files_parse(self) -> None:
        paths = sorted(CONTRACT_DIR.glob("*.json"))
        self.assertTrue(paths, "knowledge/contracts must contain JSON contracts")
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                json.loads(path.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
