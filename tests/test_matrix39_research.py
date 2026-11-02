"""Exercise issue #39 research fixture from normal upstream unittest discovery."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "research" / "matrix-interoperability"
SPEC = importlib.util.spec_from_file_location("matrix39_evaluate", EXAMPLE / "evaluate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MatrixResearchTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((EXAMPLE / "cases.json").read_text(encoding="utf-8"))

    def test_retained_expected_results(self):
        expected = json.loads((EXAMPLE / "expected.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.evaluate(self.data), expected)
        self.assertEqual(expected["target_assurance"], "not-assessed")

    def test_revocation_never_grants_execution(self):
        for case in self.data["scenarios"]:
            if case["permission"] == "revoked" and case["booking_executed"]:
                result = next(x for x in MODULE.evaluate(self.data)["results"] if x["id"] == case["id"])
                self.assertEqual(result["outcome"], "FAIL")

    def test_missing_authority_is_indeterminate(self):
        result = next(x for x in MODULE.evaluate(self.data)["results"] if x["id"] == "unknown-authority")
        self.assertEqual(result["outcome"], "INDETERMINATE")


if __name__ == "__main__":
    unittest.main()
