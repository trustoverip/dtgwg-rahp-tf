"""Repeatability checker: stable positives, stable negatives and invalid inputs."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        self.assertIn("acceptances", result["inputs_sha256"])
        self.assertEqual(result["status"], "accepted-repeatable")

    def test_invalid_review_is_stably_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.yaml"
            path.write_text("schema: wrong\nassessment_id: BAD\n", encoding="utf-8")
            result = m.run(path, RISKS)
            self.assertFalse(result["validation_accepted"])
            self.assertTrue(result["machine_results_identical"])
            self.assertEqual(result["status"], "rejected-repeatable")

    def test_missing_source_is_not_implicitly_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                m.run(EXAMPLE, RISKS, source=Path(temp) / "absent")

    def test_minimum_repetitions_enforced(self):
        with self.assertRaises(ValueError):
            m.run(EXAMPLE, RISKS, repeat=1)


    def test_unstable_validator_results_are_not_accepted(self):
        replies = [
            subprocess.CompletedProcess([], 0, stdout="one", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="two", stderr=""),
        ]
        with mock.patch.object(m.subprocess, "run", side_effect=replies):
            result = m.run(EXAMPLE, RISKS)
        self.assertFalse(result["machine_results_identical"])
        self.assertEqual(result["status"], "unstable")

    def test_sanitization_cannot_hide_raw_instability(self):
        replies = [
            subprocess.CompletedProcess([], 0, stdout="PASS: /home/alpha/review.yaml\n", stderr=""),
            subprocess.CompletedProcess([], 0, stdout="PASS: /home/bravo/review.yaml\n", stderr=""),
        ]
        with mock.patch.object(m.subprocess, "run", side_effect=replies):
            result = m.run(EXAMPLE, RISKS)
        self.assertFalse(result["machine_results_identical"])
        self.assertEqual(result["status"], "unstable")
        report = json.dumps(result)
        self.assertNotIn("/home/alpha", report)
        self.assertNotIn("/home/bravo", report)

    def test_input_mutation_during_replay_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            risks = Path(temp) / "risks.yaml"
            risks.write_bytes(RISKS.read_bytes())

            def mutate(*args, **kwargs):
                risks.write_bytes(risks.read_bytes() + b"\n# changed during replay\n")
                return subprocess.CompletedProcess([], 0, stdout="PASS\n", stderr="")

            with mock.patch.object(m.subprocess, "run", side_effect=mutate):
                with self.assertRaisesRegex(RuntimeError, "Input changed during replay: risks"):
                    m.run(EXAMPLE, risks)

    def test_different_acceptance_corpora_change_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.yaml"
            second = Path(temp) / "second.yaml"
            first.write_text("records: []\n", encoding="utf-8")
            second.write_text("records:\n  - id: RA-EX\n    decision: pending\n", encoding="utf-8")
            reply = subprocess.CompletedProcess([], 0, stdout="PASS\n", stderr="")
            with mock.patch.object(m.subprocess, "run", return_value=reply) as runner:
                a = m.run(EXAMPLE, RISKS, acceptances=first)
                b = m.run(EXAMPLE, RISKS, acceptances=second)
            self.assertNotEqual(a["inputs_sha256"]["acceptances"], b["inputs_sha256"]["acceptances"])
            commands = [call.args[0] for call in runner.call_args_list]
            self.assertIn(str(first), commands[0])
            self.assertIn(str(second), commands[-1])

    def test_portable_report_redacts_local_paths_and_keeps_input_roles(self):
        with tempfile.TemporaryDirectory() as temp:
            local_review = Path(temp) / "review.yaml"
            local_review.write_bytes(EXAMPLE.read_bytes())
            output = f"PASS: {local_review}\nWARN: /home/person/other-private.yaml\n"
            reply = subprocess.CompletedProcess([], 0, stdout=output, stderr="")
            with mock.patch.object(m.subprocess, "run", return_value=reply):
                result = m.run(local_review, RISKS)
            retained = json.dumps(result)
            self.assertEqual(result["schema"], "rahp-review-replay-check/v2")
            self.assertNotIn(str(local_review), retained)
            self.assertNotIn("/home/person/", retained)
            self.assertIn("<input:review>", result["observed_result"]["stdout"])
            self.assertIn("<local-path>", result["observed_result"]["stdout"])
            self.assertEqual(len(result["observed_result_raw_sha256"]["stdout"]), 64)

    def test_environment_records_relevant_versions_only(self):
        reply = subprocess.CompletedProcess([], 0, stdout="PASS\n", stderr="")
        with mock.patch.object(m.subprocess, "run", return_value=reply):
            result = m.run(EXAMPLE, RISKS)
        environment = result["environment"]
        self.assertTrue(environment["python_version"])
        self.assertTrue(environment["python_implementation"])
        self.assertEqual(set(environment["packages"]), {"PyYAML", "jsonschema"})
        self.assertTrue(all(environment["packages"].values()))


if __name__ == "__main__":
    unittest.main()
