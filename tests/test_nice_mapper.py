"""Unit tests for the NIST NICE Framework Mapping Engine."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import nice_mapper  # noqa: E402


class TestNiceMapper(unittest.TestCase):
    """Deterministic unit tests for tokenization, mapping, and CLI behavior."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tks_rows = json.loads(nice_mapper.DEFAULT_DATA_PATH.read_text(encoding="utf-8"))
        cls.mapper = nice_mapper.NiceTksMapper(cls.tks_rows)

    def test_tks_dictionary_size(self) -> None:
        self.assertEqual(len(self.tks_rows), 2211)

    def test_tokenize_hyphenated_and_stopwords(self) -> None:
        tokens = nice_mapper.tokenize("How to identify C2-beacon traffic using SIEM")
        self.assertIn("c2-beacon", tokens)
        self.assertIn("beacon", tokens)
        self.assertIn("siem", tokens)
        self.assertNotIn("how", tokens)
        self.assertNotIn("using", tokens)

    def test_reuse_cap_enforced(self) -> None:
        items = [f"Investigate SIEM lateral movement alert #{i}" for i in range(6)]
        results = self.mapper.map_items(items, per_item=3, max_reuse=2)
        counts: dict[str, int] = {}
        for item in results:
            self.assertGreaterEqual(len(item["matches"]), 2)
            self.assertLessEqual(len(item["matches"]), 3)
            for match in item["matches"]:
                counts[match["tks_id"]] = counts.get(match["tks_id"], 0) + 1
        self.assertTrue(all(count <= 2 for count in counts.values()))

    def test_load_sample_inputs_and_export_csv(self) -> None:
        label_json, items_json = nice_mapper.load_inputs(ROOT / "samples" / "soc_triage_04.json")
        self.assertEqual(label_json, "soc-triage-04")
        self.assertEqual(len(items_json), 1)

        label_csv, items_csv = nice_mapper.load_inputs(ROOT / "samples" / "sample_questions.csv")
        self.assertEqual(label_csv, "sample_questions")
        self.assertGreater(len(items_csv), 0)

        results = self.mapper.map_items(items_csv[:2], per_item=2)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_csv = Path(tmpdir) / "out.csv"
            nice_mapper.export_csv(results, out_csv)
            lines = out_csv.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 5)

    def test_cli_selftest(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "nice_mapper.py"), "--selftest"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("[PASS]", proc.stdout)


if __name__ == "__main__":
    unittest.main()
