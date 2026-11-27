"""Exercise normalized consumer view and reject corrupt source bindings."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"
sys.path.insert(0, str(ROOT))
from normalize_coverage import normalize, load


class SediNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.register = load("requirement-coverage.json")
        self.index = load("requirement-index.json")
        self.manifest = load("archive-manifest.json")

    def test_view(self):
        result = normalize(self.register, self.index, self.manifest)
        self.assertEqual(result["summary"]["requirements"], 142)
        self.assertEqual(result["summary"]["examined"], 141)
        self.assertEqual(result["summary"]["numbered_objectives"], 703)
        self.assertEqual(result["overall_assurance"], "review-required")
        self.assertFalse(result["source_interpretations_independently_verified"])
        gap, = [r for r in result["records"] if r["status"] == "indexed"]
        self.assertEqual(gap["id"], "SEDI-IDP-08")
        self.assertTrue(gap["source_gap"])
        self.assertNotIn("objectives", gap)

    def test_mutations(self):
        name = "technical-architecture-examination.json"
        for mutation in ("digest", "page", "coverage", "applicability"):
            with self.subTest(mutation=mutation):
                doc = copy.deepcopy(load(name))
                r = doc["requirements"][0]
                if mutation == "digest":
                    r["source"]["sha256"] = "0" * 64
                elif mutation == "page":
                    r["source"]["pages"] = [999]
                elif mutation == "coverage":
                    for v in r["verification"].values():
                        v["objectives"] = []
                else:
                    r["verification"]["AUTO"]["applicability"] = "N/A"
                with self.assertRaises(ValueError):
                    normalize(self.register, self.index, self.manifest,
                              lambda path: doc if path == name else load(path))
