"""Contract regression for the bounded control-consequence research in issue #38.

These tests check fixture consistency and evidence boundaries, not empirical harms
or task-force approval of a proposed portable-method amendment.
"""
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs/research/control-consequences"
CASES = json.loads((RESEARCH / "cases.json").read_text(encoding="utf-8"))
RISKS = yaml.safe_load((ROOT / "data/risks.yaml").read_text(encoding="utf-8"))
LIFECYCLE = yaml.safe_load((ROOT / "method/lifecycle.yaml").read_text(encoding="utf-8"))


class ControlConsequenceResearch(unittest.TestCase):
    def test_four_distinct_cross_domain_cases_and_pinned_evidence(self):
        self.assertEqual(len(CASES["cases"]), 4)
        self.assertEqual(len({c["control_class"] for c in CASES["cases"]}), 4)
        self.assertEqual(len({c["id"] for c in CASES["cases"]}), 4)
        for key in ("upstream_revision", "downstream_evidence_revision"):
            self.assertRegex(CASES[key], r"^[0-9a-f]{40}$")
        self.assertEqual({c["source_case"] for c in CASES["cases"]},
                         {"CCA-001", "CCA-002", "CCA-004", "CCA-005"})

    def test_all_risk_candidates_exist_in_canonical_upstream_instance(self):
        known = {r["id"] for r in RISKS["records"]}
        for case in CASES["cases"]:
            with self.subTest(case=case["id"]):
                cited = set(case["target_mitigation"]["upstream_risks"] +
                            case["consequence_risk_candidates"])
                self.assertTrue(cited)
                self.assertFalse(cited - known)

    def test_actor_redistribution_is_explicit_not_aggregated(self):
        for case in CASES["cases"]:
            with self.subTest(case=case["id"]):
                actors = case["affected_actors"]
                self.assertGreaterEqual(len(actors), 2)
                self.assertEqual(len({a["actor"] for a in actors}), len(actors))
                self.assertTrue(all(a["effect"] and a["change"] for a in actors))
                self.assertTrue(case["target_mitigation"]["hypothesis"])
                self.assertTrue(case["rationale"])

    def test_indeterminate_case_never_receives_control_credit(self):
        case = next(c for c in CASES["cases"] if c["id"] == "UCCA-004")
        self.assertEqual(case["disposition"], "insufficient_evidence")
        self.assertEqual(case["assurance_implication"], "indeterminate")
        self.assertEqual(case["control_credit"], "withheld")
        for candidate in CASES["cases"]:
            if candidate["evidence_state"].startswith("missing_"):
                self.assertNotEqual(candidate["assurance_implication"], "pass")

    def test_fixture_dispositions_are_bounded_and_not_schema_claims(self):
        allowed = set(CASES["dispositions"])
        self.assertEqual(len(allowed), 4)
        self.assertTrue(all(c["disposition"] in allowed for c in CASES["cases"]))
        self.assertEqual(CASES["status"], "research-fixtures-not-canonical-records")

    def test_method_note_preserves_control_observability_and_adds_consequence_check(self):
        stage = next(s for s in LIFECYCLE["records"] if s["id"] == "STAGE-2")
        control = next(s for s in stage["stations"] if s["id"] == "STAGE-2-3")
        note = control["note"]
        self.assertIn("metric", note)
        self.assertIn("assurance test", note)
        self.assertIn("redistribute", note)
        self.assertIn("does not establish overall control adequacy", note)


if __name__ == "__main__":
    unittest.main()
