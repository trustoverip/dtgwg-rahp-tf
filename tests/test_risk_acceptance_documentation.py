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
    "affected_people": ["Credential holders"],
    "alternatives_considered": ["Mitigate", "Reject the exception"],
    "conflicts_of_interest": [],
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

    def test_review_window_order_rejected(self):
        record = {**ACCEPTED, "review_date": "2026-09-01"}
        self.assertIn("review_date must follow decision_date", module.inspect(record, "High"))

    def test_conditional_requires_conditions(self):
        record = {**ACCEPTED, "decision": "accepted_with_conditions", "conditions": []}
        self.assertIn("conditional acceptance lacks conditions", module.inspect(record, "High"))

    def test_missing_affected_people_rejected(self):
        record = {**ACCEPTED, "affected_people": []}
        self.assertTrue(any("affected_people" in e for e in module.inspect(record, "High")))

    def test_missing_alternatives_rejected(self):
        record = {**ACCEPTED, "alternatives_considered": []}
        self.assertTrue(any("alternatives_considered" in e for e in module.inspect(record, "High")))

    def test_conflicts_must_be_explicit(self):
        record = {**ACCEPTED}
        del record["conflicts_of_interest"]
        self.assertIn("conflicts_of_interest must be an explicit list",
                      module.inspect(record, "High"))

    def test_residual_risk_is_bounded(self):
        record = {**ACCEPTED, "residual_risk": "banana"}
        self.assertIn("residual_risk must be a non-Critical method severity",
                      module.inspect(record, "High"))


    def test_rejection_requires_accountable_decision(self):
        record = {"risk_id": "RK-G05", "decision": "rejected"}
        errors = module.inspect(record, "High")
        for field in ("authority", "authority_reference", "decided_by",
                      "decision_date", "rationale"):
            self.assertTrue(any(field in error for error in errors))

    def test_deferral_requires_reason_and_follow_up(self):
        record = {**ACCEPTED, "decision": "deferred"}
        record.pop("deferral_reason", None)
        record.pop("review_trigger", None)
        errors = module.inspect(record, "High")
        self.assertIn("missing deferral_reason", errors)
        record["deferral_reason"] = "Awaiting independent evidence"
        self.assertEqual(module.inspect(record, "High"), [])
        record.pop("review_date")
        self.assertIn("deferral needs review_trigger or review_date",
                      module.inspect(record, "High"))
        record["review_trigger"] = "Material evidence submitted"
        self.assertEqual(module.inspect(record, "High"), [])

    def test_rejection_is_valid_but_not_acceptance_ready(self):
        record = {**ACCEPTED, "decision": "rejected"}
        corpus = {"records": [{"id": "RK-G05", "severity": "High"}]}
        result = module.evaluate(record, corpus)
        self.assertTrue(result["documentary_valid"])
        self.assertFalse(result["documentary_ready"])
        self.assertFalse(result["authority_authenticated"])

    def test_governed_residual_severities(self):
        allowed = module.permitted_residual_severities()
        self.assertIn("Low", allowed)
        self.assertNotIn("Critical", allowed)

    def test_duplicate_and_unknown_risk_fails_closed(self):
        record = dict(ACCEPTED)
        for entries in ([{"id": "RK-OTHER", "severity": "High"}],
                        [{"id": "RK-G05", "severity": "High"}] * 2):
            outcome = module.evaluate(record, {"records": entries})
            self.assertFalse(outcome["documentary_valid"])
            self.assertFalse(outcome["documentary_ready"])

    def test_invalid_corpus_fails_closed(self):
        for corpus in (None, {}, {"records": "invalid"}):
            outcome = module.evaluate(ACCEPTED, corpus)
            self.assertFalse(outcome["documentary_ready"])

    def test_critical_and_invalid_severity_fail_closed(self):
        for severity in ("Critical", "Unknown"):
            outcome = module.evaluate(ACCEPTED, {"records": [
                {"id": "RK-G05", "severity": severity}]})
            self.assertFalse(outcome["documentary_ready"])

    def test_cli_end_to_end_and_exit_status(self):
        import contextlib
        import io
        import json
        import tempfile
        import yaml
        with tempfile.TemporaryDirectory() as tmp:
            record_file = Path(tmp) / "record.yaml"
            risks_file = Path(tmp) / "risks.yaml"
            record_file.write_text(yaml.safe_dump(ACCEPTED), encoding="utf-8")
            for entries, expected_code in (
                ([{"id": "RK-G05", "severity": "High"}], 0),
                ([{"id": "RK-OTHER", "severity": "High"}], 1),
                ([{"id": "RK-G05", "severity": "High"}] * 2, 1),
                ([{"id": "RK-G05", "severity": "Critical"}], 1),
            ):
                risks_file.write_text(yaml.safe_dump({"records": entries}), encoding="utf-8")
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = module.main([str(record_file), "--risks", str(risks_file)])
                self.assertEqual(code, expected_code)
                result = json.loads(output.getvalue())
                self.assertEqual(result["documentary_ready"], expected_code == 0)
                self.assertFalse(result["authority_authenticated"])
            risks_file.unlink()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(module.main([str(record_file), "--risks", str(risks_file)]), 1)
            self.assertFalse(json.loads(output.getvalue())["documentary_ready"])

    def test_malformed_scalar_values_fail_closed(self):
        for invalid in ([], {}, 7):
            self.assertIn("unknown decision", module.inspect(
                {**ACCEPTED, "decision": invalid}, "High"))
            self.assertIn("residual_risk must be a non-Critical method severity",
                          module.inspect({**ACCEPTED, "residual_risk": invalid}, "High"))

    def test_non_acceptance_cli_exits_zero_without_readiness(self):
        import contextlib
        import io
        import json
        import tempfile
        import yaml
        with tempfile.TemporaryDirectory() as temp:
            record_path = Path(temp) / "record.yaml"
            corpus_path = Path(temp) / "risks.yaml"
            corpus_path.write_text(yaml.safe_dump({"records": [
                {"id": "RK-G05", "severity": "High"}]}), encoding="utf-8")
            for decision in ("rejected", "deferred"):
                record = {**ACCEPTED, "decision": decision}
                if decision == "deferred":
                    record["deferral_reason"] = "Awaiting evidence"
                record_path.write_text(yaml.safe_dump(record), encoding="utf-8")
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    self.assertEqual(module.main([
                        str(record_path), "--risks", str(corpus_path)]), 0)
                result = json.loads(out.getvalue())
                self.assertTrue(result["documentary_valid"])
                self.assertFalse(result["documentary_ready"])

    def test_pending_is_not_accepted(self):
        self.assertEqual(module.inspect({"decision": "pending", "risk_id": "RK-G05"}, "High"), [])

    def test_unknown_decision_fails(self):
        self.assertIn("unknown decision", module.inspect({"decision": "PASS"}, "High"))


if __name__ == "__main__":
    unittest.main()
