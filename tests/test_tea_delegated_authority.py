"""Regression coverage for the TEA delegated-authority worked example."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "review" / "examples" / "tea-delegated-authority"
SPEC = importlib.util.spec_from_file_location("tea_example_examine", EXAMPLE / "examine.py")
tea_examine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tea_examine)


class TeaDelegatedAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "example"
        shutil.copytree(EXAMPLE, self.root)

    def test_replay_preserves_bounded_authority_distinctions(self):
        result = tea_examine.replay(self.root)
        by_id = {case["id"]: case for case in result["cases"]}
        self.assertTrue(by_id["within-authority"]["authorized"])
        self.assertFalse(by_id["ability-not-delegated"]["authorized"])
        self.assertTrue(by_id["attenuated-redelegation"]["authorized"])
        self.assertFalse(by_id["attempted-broadening"]["restriction_conformant"])
        self.assertFalse(by_id["attempted-broadening"]["authorized"])
        self.assertFalse(by_id["authenticated-without-capability"]["authorized"])
        self.assertTrue(by_id["authorized-then-obligation-breach"]["authorized"])
        self.assertTrue(by_id["authorized-then-obligation-breach"]["post_gate_breach"])
        self.assertEqual("review-required", result["overall_assurance"])

    def test_composed_examination_is_validation_not_target_assurance(self):
        result = tea_examine.examine(self.root)
        self.assertEqual("complete", result["validation"])
        self.assertEqual("review-required", result["overall_assurance"])
        self.assertEqual(4, result["findings"])
        self.assertEqual(1, result["open_findings"])
        self.assertTrue(all(value == "not-assessed" for value in result["unassessed"].values()))

    def test_retained_source_tamper_fails_closed(self):
        path = self.root / "source" / "clauses.md.txt"
        path.write_text(path.read_text() + "\nchanged\n")
        with self.assertRaises(ValueError):
            tea_examine.examine(self.root)

    def test_fixture_expectation_drift_fails_closed(self):
        path = self.root / "cases.json"
        cases = json.loads(path.read_text())
        cases[0]["expected"]["authorized"] = False
        path.write_text(json.dumps(cases))
        with self.assertRaises(ValueError) as caught:
            tea_examine.examine(self.root)
        self.assertIn("Unexpected case result", str(caught.exception))

    def test_stale_evidence_observation_fails_closed(self):
        path = self.root / "evidence.json"
        evidence = json.loads(path.read_text())
        evidence["execution"]["observations"]["cases"][0]["authorized"] = False
        path.write_text(json.dumps(evidence))
        with self.assertRaises(ValueError) as caught:
            tea_examine.examine(self.root)
        self.assertIn("observations disagree", str(caught.exception))

    def test_unassessed_state_cannot_be_promoted_to_success(self):
        path = self.root / "evidence.json"
        evidence = json.loads(path.read_text())
        evidence["unassessed"]["live_service"] = "verified"
        path.write_text(json.dumps(evidence))
        with self.assertRaises(ValueError) as caught:
            tea_examine.examine(self.root)
        self.assertIn("evidence schema", str(caught.exception))

    def test_selected_bundle_code_is_not_executed(self):
        (self.root / "replay.py").write_text('raise RuntimeError("must not execute")')
        self.assertEqual("complete", tea_examine.examine(self.root)["validation"])

    def test_cli_success_and_failure_are_distinct(self):
        ok = subprocess.run(
            [sys.executable, str(EXAMPLE / "examine.py")],
            cwd=ROOT, capture_output=True, text=True
        )
        self.assertEqual(0, ok.returncode, ok.stderr)
        self.assertIn('"validation": "complete"', ok.stdout)
        self.assertIn('"overall_assurance": "review-required"', ok.stdout)

        (self.root / "evidence.json").unlink()
        bad = subprocess.run(
            [sys.executable, str(EXAMPLE / "examine.py"), "--example", str(self.root)],
            cwd=ROOT, capture_output=True, text=True
        )
        self.assertNotEqual(0, bad.returncode)
        self.assertEqual("", bad.stdout)
        self.assertIn("incomplete", bad.stderr)


if __name__ == "__main__":
    unittest.main()
