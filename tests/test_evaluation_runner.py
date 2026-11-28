"""Negative and contract tests for the optional RAHP Evaluation Runner."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
from unittest.mock import patch

from runner.__main__ import ConfigurationError, read_config, run

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "runner/examples/retained-trqp.yaml"


class RunnerContractTests(unittest.TestCase):
    def test_shipped_example_is_valid(self):
        document, digest = read_config(EXAMPLE)
        self.assertEqual(len(document["targets"]), 1)
        self.assertEqual(len(digest), 64)

    def malformed(self, text):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.yaml"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                read_config(path)

    def test_unknown_field_fails_closed(self):
        self.malformed(EXAMPLE.read_text() + "command: 'curl | sh'\n")

    def test_missing_evaluator_fails_closed(self):
        self.malformed(EXAMPLE.read_text().replace("upstream-retained-trqp", "arbitrary-plugin"))

    def test_missing_required_evaluator_is_rejected(self):
        self.malformed(EXAMPLE.read_text().replace(
            "    evaluator: upstream-retained-trqp\n", ""))

    def test_unapproved_repository_fails_closed(self):
        self.malformed(EXAMPLE.read_text().replace(
            "trustoverip/tswg-trust-registry-protocol", "trustoverip/dtgwg-cred-spec"))

    def test_mutable_revision_fails_closed(self):
        self.malformed(EXAMPLE.read_text().replace(
            "6863733878f3657e05f70764bb474a9fb918de9a", "main"))

    def test_empty_or_duplicate_targets_rejected(self):
        self.malformed("schema: rahp-evaluation-runner/v1alpha1\ntargets: []\n")
        text = EXAMPLE.read_text()
        self.malformed(text + text[text.index("  - id:"):])

    def test_false_portfolio_authority_rejected(self):
        self.malformed(EXAMPLE.read_text() + """
inventory:
  origin: https://example.org/inventory
  revision: 6863733878f3657e05f70764bb474a9fb918de9a
  sha256: """ + "a" * 64 + """
  role: reference-example
  meaning: authoritative
""")

    @patch("runner.__main__.installed_revision", return_value=None)
    @patch("runner.__main__.subprocess.run")
    def test_success_is_review_required_not_assurance_pass(self, mocked_run, _revision):
        data = {"assessment_id": "SR-001", "validation": "complete",
                "overall_assurance": "review-required", "findings": 2}
        mocked_run.return_value = CompletedProcess([], 0, json.dumps(data), "")
        with tempfile.TemporaryDirectory() as temporary:
            folder, report = run(EXAMPLE, Path(temporary), "retained-trqp")
            self.assertEqual(report["execution"]["state"], "completed")
            self.assertEqual(report["execution"]["assurance"], "review-required")
            self.assertTrue((folder / "evaluation.md").exists())
            self.assertEqual(json.loads((folder / "evaluation.json").read_text()), report)

    @patch("runner.__main__.installed_revision", return_value=None)
    @patch("runner.__main__.subprocess.run")
    def test_incomplete_output_cannot_become_success(self, mocked_run, _revision):
        mocked_run.return_value = CompletedProcess([], 0, '{"validation":"complete"}', "")
        with tempfile.TemporaryDirectory() as temporary:
            _, report = run(EXAMPLE, Path(temporary), "retained-trqp")
            self.assertEqual(report["execution"]["state"], "failed")
            self.assertEqual(report["execution"]["validation"], "indeterminate")
            self.assertEqual(report["execution"]["assurance"], "not-assessed")

    @patch("runner.__main__.installed_revision", return_value=None)
    @patch("runner.__main__.subprocess.run")
    def test_evaluator_failure_is_retained_as_failed(self, mocked_run, _revision):
        mocked_run.return_value = CompletedProcess([], 1, "", "error")
        with tempfile.TemporaryDirectory() as temporary:
            _, report = run(EXAMPLE, Path(temporary), "retained-trqp")
            self.assertEqual(report["execution"]["state"], "failed")
            self.assertIsNone(report["observed_result"])

    @patch("runner.__main__.installed_revision", return_value=None)
    @patch("runner.__main__.subprocess.run", side_effect=TimeoutExpired(["examiner"], 1))
    def test_timeout_does_not_infer_success(self, _run, _revision):
        with tempfile.TemporaryDirectory() as temporary:
            _, report = run(EXAMPLE, Path(temporary), "retained-trqp", timeout=1)
            self.assertEqual(report["execution"]["state"], "failed")
            self.assertEqual(report["execution"]["assurance"], "not-assessed")

    def test_undeclared_target_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ConfigurationError):
                run(EXAMPLE, Path(temporary), "not-declared")

    def test_source_revision_drift_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = EXAMPLE.read_text().replace(
                "6863733878f3657e05f70764bb474a9fb918de9a",
                "a" * 40)
            file = Path(temporary) / "drift.yaml"
            file.write_text(config)
            with self.assertRaises(ConfigurationError):
                run(file, Path(temporary) / "results", "retained-trqp")


    def test_real_installed_evaluator_consumer_path(self):
        """Exercise the actual installed examiner, not a mocked subprocess."""
        with tempfile.TemporaryDirectory() as temporary:
            folder, report = run(EXAMPLE, Path(temporary), "retained-trqp")
            self.assertEqual(report["execution"]["state"], "completed")
            self.assertEqual(report["execution"]["validation"], "complete")
            self.assertEqual(report["execution"]["assurance"], "review-required")
            self.assertGreaterEqual(report["observed_result"]["findings"], 1)
            self.assertIn("not independent source authenticity",
                          report["claim_boundary"])
            self.assertTrue((folder / "evaluation.json").is_file())

if __name__ == "__main__":
    unittest.main()
