"""INV-6: a risk acceptance record cannot say accepted without its required fields."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
RULE = "accepted_risk_has_required_fields"
COMPLETE = {
    "decision": "accepted",
    "authority": "Example body",
    "decided_by": ["Example person"],
    "decision_date": "2026-10-01",
    "residual_risk": "Medium",
    "review_date": "2027-01-01",
    "evidence": "Example assessment, v1, 2026-10-01",
}


class AcceptedRiskFieldTests(unittest.TestCase):
    def validate(self, **changes):
        """Validate a copy of data/ with RA-001 changed, and return its INV-6 errors."""
        with tempfile.TemporaryDirectory() as td:
            data = Path(td) / "data"
            shutil.copytree(ROOT / "data", data)
            path = data / "risk-acceptances.yaml"
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            doc["records"][0].update(changes)
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/validate.py"), "--data", str(data), "--json"],
                cwd=ROOT, text=True, capture_output=True, check=False)
        report = json.loads(result.stdout)
        return result.returncode, [e for e in report["errors"] if RULE in e]

    def test_current_pending_records_pass(self):
        self.assertEqual(self.validate(), (0, []))

    def test_accepted_with_no_authority_fails(self):
        code, errors = self.validate(decision="accepted")
        self.assertEqual(code, 1)
        self.assertEqual(len(errors), 1)
        for field in ("authority", "decided_by", "decision_date", "review_date"):
            self.assertIn(field, errors[0])

    def test_complete_acceptance_passes(self):
        self.assertEqual(self.validate(**COMPLETE), (0, []))

    def test_each_required_field_is_enforced(self):
        required = ("authority", "decided_by", "decision_date", "residual_risk",
                    "review_date", "evidence")
        for field in required:
            with self.subTest(field=field):
                code, errors = self.validate(**{**COMPLETE, field: None})
                self.assertEqual(code, 1)
                self.assertIn(field, errors[0])

    def test_blank_values_do_not_count(self):
        for changes in ({"authority": "   "}, {"decided_by": []}, {"decided_by": [" "]}):
            with self.subTest(changes=changes):
                code, errors = self.validate(**{**COMPLETE, **changes})
                self.assertEqual(code, 1)
                self.assertEqual(len(errors), 1)

    def test_conditional_acceptance_needs_conditions(self):
        complete = {**COMPLETE, "decision": "accepted_with_conditions"}
        self.assertEqual(self.validate(**complete), (0, []))
        code, errors = self.validate(**{**complete, "conditions": []})
        self.assertEqual(code, 1)
        self.assertIn("conditions", errors[0])

    def test_rejected_is_not_treated_as_an_acceptance(self):
        self.assertEqual(self.validate(decision="rejected"), (0, []))


if __name__ == "__main__":
    unittest.main()
