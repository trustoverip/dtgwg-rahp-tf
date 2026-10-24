"""Repeatability checker: stable positives, stable negatives and invalid inputs."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("review_replay_check", ROOT / "review/replay_check.py")
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
RISKS = ROOT / "data/risks.yaml"
EXAMPLE = ROOT / "review/examples/worked-adoption/baseline-review.yaml"


class RepeatabilityChecks(unittest.TestCase):
    def test_retained_review_is_stable_and_valid(self):
        result = m.run(EXAMPLE, RISKS)
        self.assertTrue(result["validation_accepted"])
        self.assertTrue(result["machine_results_identical"])
        self.assertEqual(result["repeat"], 2)

    def test_invalid_review_is_stably_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.yaml"
            path.write_text("schema: wrong\nassessment_id: BAD\n", encoding="utf-8")
            result = m.run(path, RISKS)
            self.assertFalse(result["validation_accepted"])
            self.assertTrue(result["machine_results_identical"])

    def test_missing_source_is_not_implicitly_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                m.run(EXAMPLE, RISKS, source=Path(temp) / "absent")

    def test_minimum_repetitions_enforced(self):
        with self.assertRaises(ValueError):
            m.run(EXAMPLE, RISKS, repeat=1)


if __name__ == "__main__":
    unittest.main()
