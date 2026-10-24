"""Documentary readiness tests never confer risk-acceptance authority."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "risk_acceptance_documentation", ROOT / "review/check_risk_acceptance_documentation.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ACCEPTED = {
    "decision": "accepted", "risk_id": "RK-G05",
    "authority": "Example body", "authority_reference": "example-mandate-v1",
    "decided_by": ["Example reviewer"], "decision_date": "2026-10-01",
    "review_date": "2027-01-01", "evidence": "example/assessment@sha",
    "rationale": "A constructed demonstration with accountable review and scoped exposure.",
    "residual_risk": "Low",
}


class AdvisoryRiskAcceptanceTests(unittest.TestCase):
    def test_complete_example_is_documentary_ready_only(self):
        self.assertEqual(module.inspect(ACCEPTED, "High"), [])

    def test_critical_is_not_eligible(self):
        self.assertIn("Critical risk may not be accepted", module.inspect(ACCEPTED, "Critical"))

    def test_missing_authority_reference_rejected(self):
        record = {**ACCEPTED, "authority_reference": None}
        self.assertIn("missing authority_reference", module.inspect(record, "High"))

    def test_missing_evidence_rejected(self):
        record = {**ACCEPTED, "evidence": None}
        self.assertIn("missing evidence", module.inspect(record, "High"))

    def test_empty_deciders_rejected(self):
        record = {**ACCEPTED, "decided_by": []}
        self.assertTrue(module.inspect(record, "High"))

    def test_expired_window_rejected(self):
        record = {**ACCEPTED, "review_date": "2026-09-01"}
        self.assertIn("review_date must follow decision_date", module.inspect(record, "High"))

    def test_conditional_requires_conditions(self):
        record = {**ACCEPTED, "decision": "accepted_with_conditions", "conditions": []}
        self.assertIn("conditional acceptance lacks conditions", module.inspect(record, "High"))

    def test_pending_is_not_accepted(self):
        self.assertEqual(module.inspect({"decision": "pending", "risk_id": "RK-G05"}, "High"), [])

    def test_unknown_decision_fails(self):
        self.assertIn("unknown decision", module.inspect({"decision": "PASS"}, "High"))


if __name__ == "__main__":
    unittest.main()
