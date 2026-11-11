"""Regression coverage for the consumer-facing first-use RAHP tutorial."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import yaml


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "review" / "examples" / "standalone-trqp"
TUTORIAL = EXAMPLE / "TUTORIAL.md"


class FirstUseTutorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TUTORIAL.read_text(encoding="utf-8")

    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_local_tutorial_links_resolve(self):
        targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", self.text)
        local_targets = [
            target.split("#", 1)[0]
            for target in targets
            if target and not target.startswith(("http://", "https://", "#"))
        ]
        self.assertTrue(local_targets)
        for target in local_targets:
            with self.subTest(target=target):
                self.assertTrue((TUTORIAL.parent / target).resolve().exists())

    def test_first_use_entry_and_setup_are_discoverable(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("review/examples/standalone-trqp/TUTORIAL.md", readme)
        self.assertIn("First technical RAHP examination (start here)", readme)
        self.assertIn("technical first-use path", self.text)
        self.assertIn("review record", self.text)
        self.assertIn("python3 -m venv .venv", self.text)
        self.assertIn("python -m pip install -r requirements.txt", self.text)
        self.assertIn("python3-venv", self.text)
        self.assertIn("commit ID", self.text)
        self.assertIn("40-character SHA", self.text)

    def test_tutorial_identifiers_match_selected_source_and_review(self):
        source = yaml.safe_load((EXAMPLE / "risks.yaml").read_text(encoding="utf-8"))
        review = yaml.safe_load((EXAMPLE / "review.yaml").read_text(encoding="utf-8"))
        identifiers = {record["id"] for record in source["records"]}
        self.assertTrue(identifiers)
        self.assertTrue(all(identifier.startswith("EX-RK-") for identifier in identifiers))
        tutorial_ids = set(re.findall(r"\b(?:EX-)?RK-[A-Z]+[0-9]+\b", self.text))
        self.assertEqual(tutorial_ids, identifiers)
        referenced = {risk for finding in review["findings"] for risk in finding["risks"]}
        self.assertEqual(referenced, identifiers)
        self.assertIn(f'reviewer: {review["reviewer"]}', self.text)

    def test_independent_review_not_asserted_as_completed(self):
        self.assertIn("did not prepare this assessment", self.text)
        self.assertIn("No independent review is claimed", self.text)

    def test_documented_success_commands_execute(self):
        commands = [
            (
                "python3 review/examples/standalone-trqp/replay.py --check",
                ("review/examples/standalone-trqp/replay.py", "--check"),
            ),
            (
                "python3 review/validate_spec_review.py review/examples/standalone-trqp/review.yaml --risks review/examples/standalone-trqp/risks.yaml",
                (
                    "review/validate_spec_review.py",
                    "review/examples/standalone-trqp/review.yaml",
                    "--risks",
                    "review/examples/standalone-trqp/risks.yaml",
                ),
            ),
            (
                "python3 review/examine.py",
                ("review/examine.py",),
            ),
        ]
        for documented, argv in commands:
            with self.subTest(command=documented):
                self.assertIn(documented, self.text)
                result = self.run_command(*argv)
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_representative_output_matches_retained_result(self):
        expected = json.loads((EXAMPLE / "expected-replay.json").read_text(encoding="utf-8"))
        self.assertEqual(expected["source_integrity"], "verified")
        self.assertFalse(expected["api_example"]["requested_time_matches"])
        self.assertEqual(expected["overall_assurance"], "review-required")

        self.assertIn('"source_integrity": "verified"', self.text)
        self.assertIn('"requested_time_matches": false', self.text)
        self.assertIn('"overall_assurance": "review-required"', self.text)

    def test_documented_fail_closed_example_rejects_mutable_revision(self):
        documented = (
            "python3 review/validate_spec_review.py "
            "review/examples/invalid-mutable-revision.yaml"
        )
        self.assertIn(documented, self.text)
        result = self.run_command(
            "review/validate_spec_review.py",
            "review/examples/invalid-mutable-revision.yaml",
        )
        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        self.assertIn("schema target.revision", output)
        self.assertIn("does not match", output)
        self.assertIn("FAIL: 1 problem(s)", output)


if __name__ == "__main__":
    unittest.main()
