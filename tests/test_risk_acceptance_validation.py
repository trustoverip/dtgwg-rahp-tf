"""Canonical acceptance invariant tests: helper and real-file validation."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rahp_validate", ROOT / "tools/validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

COMPLETE = {
    "decision": "accepted",
    "authority": "Example competent body",
    "decided_by": ["Example reviewer"],
    "decision_date": "2026-11-01",
    "rationale": "Documented and bounded residual risk for a constructed fixture.",
    "residual_risk": "Low",
    "conditions": [],
    "review_date": "2027-02-01",
    "evidence": "example/assessment@sha",
}
RULE = "accepted_risk_has_required_fields"


class RiskAcceptanceValidationTests(unittest.TestCase):
    def test_complete_accepted_record_is_valid(self):
        self.assertEqual([], module.risk_acceptance_errors(COMPLETE))

    def test_pending_record_does_not_require_acceptance_fields(self):
        self.assertEqual([], module.risk_acceptance_errors({"decision": "pending"}))

    def test_accepted_record_requires_authority(self):
        self.assertIn("missing authority",
                      module.risk_acceptance_errors({**COMPLETE, "authority": None}))

    def test_accepted_record_requires_named_deciders(self):
        errors = module.risk_acceptance_errors({**COMPLETE, "decided_by": []})
        self.assertEqual(["decided_by must be a nonempty list of named participants"], errors)

    def test_conditional_acceptance_requires_conditions(self):
        record = {**COMPLETE, "decision": "accepted_with_conditions", "conditions": []}
        self.assertIn("accepted_with_conditions requires nonempty named conditions",
                      module.risk_acceptance_errors(record))

    def test_review_date_must_follow_decision_date(self):
        self.assertIn("review_date must follow decision_date",
                      module.risk_acceptance_errors({**COMPLETE, "review_date": "2026-10-31"}))

    def test_dates_must_use_iso_calendar_format(self):
        for date_value in ("20261101", "2026-02-30", "yesterday", None):
            with self.subTest(date_value=date_value):
                self.assertIn("invalid or missing decision_date (expected YYYY-MM-DD)",
                              module.risk_acceptance_errors({**COMPLETE, "decision_date": date_value}))

    def test_residual_risk_uses_noncritical_method_vocabulary(self):
        for value in ("banana", "Critical"):
            with self.subTest(value=value):
                errors = module.risk_acceptance_errors({**COMPLETE, "residual_risk": value})
                self.assertTrue(any("residual_risk must be one of:" in e for e in errors))

    def test_residual_risk_uses_current_vocabulary_not_hardcoded_values(self):
        vocab = {"severity": {"values": [
            {"value": "Critical", "absolute": True},
            {"value": "Elevated", "score": 3},
            {"value": "Low", "score": 1},
        ]}}
        self.assertEqual([], module.risk_acceptance_errors({**COMPLETE, "residual_risk": "Elevated"}, vocab))
        self.assertTrue(any("residual_risk" in e for e in
                            module.risk_acceptance_errors(COMPLETE | {"residual_risk": "High"}, vocab)))

    def test_blank_values_do_not_count(self):
        for field, value in (("authority", " "), ("evidence", ""), ("decided_by", [" "]),
                             ("conditions", [" "])):
            with self.subTest(field=field):
                record = {**COMPLETE, field: value}
                if field == "conditions":
                    record["decision"] = "accepted_with_conditions"
                self.assertNotEqual([], module.risk_acceptance_errors(record))

    def validate_real_data(self, changes):
        """Exercise canonical main(), not just the helper, on an isolated data copy."""
        with tempfile.TemporaryDirectory() as td:
            data = Path(td) / "data"
            shutil.copytree(ROOT / "data", data)
            path = data / "risk-acceptances.yaml"
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
            document["records"][0].update(changes)
            path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate.py"), "--data", str(data), "--json"],
                cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        report = json.loads(result.stdout)
        messages = [e for e in report["errors"] if RULE in e]
        return result.returncode, messages, report

    def test_real_pending_data_passes(self):
        code, errors, _ = self.validate_real_data({})
        self.assertEqual((0, []), (code, errors))

    def test_real_incomplete_accepted_record_fails(self):
        code, errors, report = self.validate_real_data({"decision": "accepted"})
        self.assertEqual(1, code)
        self.assertTrue(any("authority" in e for e in errors))
        self.assertTrue(report["errors"])

    def test_real_complete_accepted_record_passes(self):
        code, errors, _ = self.validate_real_data(COMPLETE)
        self.assertEqual((0, []), (code, errors))

    def test_real_conditional_acceptance_checks_conditions(self):
        code, errors, _ = self.validate_real_data(
            {**COMPLETE, "decision": "accepted_with_conditions", "conditions": []})
        self.assertEqual(1, code)
        self.assertTrue(any("conditions" in e for e in errors))

    def test_real_invalid_residual_and_date_fail(self):
        code, errors, _ = self.validate_real_data(
            {**COMPLETE, "residual_risk": "Critical", "review_date": "2026-10-01"})
        self.assertEqual(1, code)
        self.assertTrue(any("residual_risk" in e for e in errors))
        self.assertTrue(any("review_date" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
