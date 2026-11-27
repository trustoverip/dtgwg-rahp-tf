"""Exercise integrated SEDI documentary consumer using synthetic integrity boundary."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"
sys.path.insert(0, str(ROOT))
import consolidate

class SediConsolidationTests(unittest.TestCase):
    def test_composition(self):
        with patch.object(consolidate, "verify_archive", return_value={"source_integrity": "fixture"}):
            r = consolidate.compose("fixture")
            self.assertEqual(len(r["risks"]), 31)
            self.assertEqual(len(r["candidate_propositions"]), 47)
            self.assertEqual(r["coverage"]["examined"], 141)
            self.assertFalse(r["documentary_coverage_complete"])
            self.assertEqual(r["overall_assurance"], "review-required")

    def test_false_success(self):
        for mutation in ("missing-case", "unknown-risk", "terminal", "baseline"):
            with self.subTest(mutation=mutation):
                def loader(name):
                    d = copy.deepcopy(consolidate.load(name))
                    if name == "consolidation-index.json":
                        if mutation == "missing-case":
                            d["findings"].pop()
                        elif mutation == "terminal":
                            d["findings"][0]["status"] = "resolved"
                        elif mutation == "baseline":
                            d["archive_sha256"] = "0" * 64
                    if name == "privacy-examination.json" and mutation == "unknown-risk":
                        d["cases"][0]["risk"] = "EX-RK-UNKNOWN"
                    return d
                with patch.object(consolidate, "verify_archive", return_value={}):
                    with self.assertRaises(ValueError):
                        consolidate.compose("fixture", loader)
