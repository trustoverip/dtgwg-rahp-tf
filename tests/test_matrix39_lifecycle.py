"""Reference experiment and RAHP review contract checks for #39."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "research" / "matrix-interoperability"
SPEC = importlib.util.spec_from_file_location("matrix39_lifecycle", EXAMPLE / "lifecycle.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.run_record = M.campaign("reassessed")
        self.ctx = self.run_record["context"]
        self.obs = self.run_record["observations"]

    def test_fresh_replay_preserves_both_contexts(self):
        r = M.reproduce()
        self.assertEqual(r["baseline"]["protocol_result"], "PASS")
        self.assertEqual(r["reassessed"]["protocol_result"], "PASS")
        self.assertIsNone(r["baseline"]["context"]["revocation"])
        self.assertEqual(r["reassessed"]["context"]["revocation"]["deadline_tick"], 12)
        self.assertEqual(r["baseline"]["context"]["subject_sha256"], self.ctx["subject_sha256"])
        self.assertEqual(r["overall_assurance"], "review-required")
        self.assertEqual(r["matrix_campaign"], "not-executed")

    def test_known_bypasses_fail_including_deny_with_effect(self):
        for variant, trial_id in (("cached-mutant", "R3"), ("fallback-mutant", "R4"), ("recombine-mutant", "R5")):
            with self.subTest(variant=variant):
                r = M.campaign("reassessed", variant)
                self.assertEqual(r["protocol_result"], "FAIL")
                self.assertEqual(r["trial_results"][trial_id], "FAIL")
                trace = next(o for o in r["observations"] if o["id"] == trial_id)
                self.assertTrue(trace["effects"])
                if variant == "fallback-mutant":
                    self.assertFalse(trace["gate_allow"])

    def test_missing_duplicate_unknown_and_malformed_observations(self):
        for records in (self.obs[:-1], self.obs + [self.obs[0]], self.obs + [{"id": "unknown"}], self.obs + [{"id": []}]):
            self.assertEqual(M.aggregate("reassessed", records, self.ctx), "INDETERMINATE")

    def test_missing_or_wrong_context_evidence(self):
        for key in ("effects", "gate_allow", "authority", "context"):
            records = copy.deepcopy(self.obs)
            del records[0][key]
            self.assertEqual(M.aggregate("reassessed", records, self.ctx), "INDETERMINATE", key)
        records = copy.deepcopy(self.obs)
        records[0]["context"] = M.digest(M.context("baseline"))
        self.assertEqual(M.aggregate("reassessed", records, self.ctx), "INDETERMINATE")

    def test_counterexample_not_hidden_by_missing_coverage(self):
        r = M.campaign("reassessed", "fallback-mutant")
        trace = next(o for o in r["observations"] if o["id"] == "R4")
        self.assertEqual(M.aggregate("reassessed", [trace], r["context"]), "FAIL")

    def test_duplicate_effect_is_a_failure(self):
        records = copy.deepcopy(self.obs)
        records[-1]["effects"] *= 2
        self.assertEqual(M.aggregate("reassessed", records, self.ctx), "FAIL")

    def test_unchanged_read_grant_and_revoked_descendant(self):
        self.assertTrue(M.eligible("grandchild", "book", set()))
        self.assertFalse(M.eligible("grandchild", "book", {"root"}))
        self.assertTrue(M.eligible("read", "read", {"root"}))

    def test_existing_review_contract(self):
        for name in ("matrix-source-review.yaml", "baseline-review.json", "reassessed-review.json"):
            with self.subTest(record=name):
                result = subprocess.run([sys.executable, str(ROOT / "review" / "validate_spec_review.py"),
                                         str(EXAMPLE / name), "--risks", str(EXAMPLE / "risks.yaml")],
                                        text=True, capture_output=True, cwd=ROOT)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
