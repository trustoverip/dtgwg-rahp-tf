"""Coverage register consistency and incomplete-coverage gate."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("sedi_coverage", ROOT / "check_coverage.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SediCoverageTests(unittest.TestCase):
    def setUp(self):
        self.register = MODULE.load("requirement-coverage.json")
        self.index = MODULE.load("requirement-index.json")
        self.manifest = MODULE.load("archive-manifest.json")

    def check(self, register, complete=False):
        return MODULE.check(register, self.index, self.manifest, require_complete=complete)

    def test_coverage(self):
        result = self.check(self.register)
        self.assertEqual(result["indexed_universe"], 142)
        self.assertEqual(sum(result["counts"].values()), 142)
        self.assertEqual(result["overall_assurance"], "review-required")
        if result["counts"]["indexed"]:
            with self.assertRaises(ValueError):
                self.check(self.register, True)
        else:
            self.assertTrue(self.check(self.register, True)["documentary_coverage_complete"])

    def test_invalid_records(self):
        for mutation in ("missing", "duplicate", "wrong-id", "wrong-objectives", "review-claim", "archive"):
            with self.subTest(mutation=mutation):
                register = copy.deepcopy(self.register)
                examined = next(r for r in register["records"] if r["status"] != "indexed")
                if mutation == "missing":
                    register["records"].pop()
                elif mutation == "duplicate":
                    register["records"][-1] = register["records"][0]
                elif mutation == "wrong-id":
                    examined["id"] = "SEDI-INVALID-99"
                elif mutation == "wrong-objectives":
                    examined["examination"]["objectives"] = [999]
                elif mutation == "review-claim":
                    examined["review_state"] = "reviewed"
                else:
                    register["archive_sha256"] = "0" * 64
                with self.assertRaises(ValueError):
                    self.check(register)
