import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "review" / "examples" / "vrc-v03" / "evaluate.py"
spec = importlib.util.spec_from_file_location("vrc_v03_evaluate", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class VRCReassessmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "vrc-v03"
        shutil.copytree(mod.HERE, self.root)

    def test_reassessment_is_source_derived_and_bounded(self):
        result = mod.evaluate(self.root)
        self.assertEqual("complete", result["validation"])
        self.assertEqual("review-required", result["overall_assurance"])
        self.assertTrue(result["observations"]["baseline"]["general_vrc_zkp_requires_shared_community_evidence"])
        self.assertFalse(result["observations"]["reassessed"]["general_vrc_zkp_requires_shared_community_evidence"])
        self.assertTrue(result["observations"]["reassessed"]["pairwise_zkp_section"])
        self.assertTrue(result["observations"]["reassessed"]["community_anchored_zkp_section"])
        self.assertTrue(result["observations"]["reassessed"]["explicit_no_shared_membership_precondition"])
        self.assertEqual("open->resolved", result["finding_transitions"]["F-001"])
        self.assertEqual("open->open", result["finding_transitions"]["F-002"])

    def test_missing_reviewer_fails_closed(self):
        path = self.root / "baseline-review.yaml"
        record = yaml.safe_load(path.read_text())
        record.pop("reviewer")
        path.write_text(yaml.safe_dump(record, sort_keys=False))
        with self.assertRaisesRegex(ValueError, "reviewer"):
            mod.evaluate(self.root)

    def test_retained_source_mutation_fails_closed(self):
        path = self.root / "baseline" / "source" / "dtg.md.txt"
        path.write_text(path.read_text() + "\nmutated\n")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            mod.evaluate(self.root)

    def test_reassessment_cannot_reuse_baseline_revision(self):
        path = self.root / "reassessed-review.yaml"
        review = yaml.safe_load(path.read_text())
        review["target"]["revision"] = "62bbd8a19d598078f50560948ca71ec0e034a6fc"
        path.write_text(yaml.safe_dump(review, sort_keys=False))
        with self.assertRaisesRegex(ValueError, "review binding mismatch|review target"):
            mod.evaluate(self.root)

    def test_stale_observation_fails_closed(self):
        path = self.root / "reassessed-evidence.json"
        evidence = json.loads(path.read_text())
        evidence["execution"]["observations"]["pairwise_zkp_section"] = False
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "observations disagree"):
            mod.evaluate(self.root)

    def test_missing_finding_evidence_is_rejected(self):
        path = self.root / "baseline-evidence.json"
        evidence = json.loads(path.read_text())
        evidence["findings"].pop()
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "every review finding"):
            mod.evaluate(self.root)

    def test_risk_reasoning_must_cover_selected_risk(self):
        path = self.root / "baseline-evidence.json"
        evidence = json.loads(path.read_text())
        evidence["findings"][0]["risk_reasoning"] = {"RK-ID05": "Wrong risk mapping used deliberately for the negative test."}
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "risk reasoning"):
            mod.evaluate(self.root)

    def test_evidence_proposition_must_resolve_in_retained_source(self):
        path = self.root / "reassessed-evidence.json"
        evidence = json.loads(path.read_text())
        evidence["evidence"][0]["contains"] = ["text that is not present in the retained specification"]
        path.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "proposition does not resolve"):
            mod.evaluate(self.root)


if __name__ == "__main__":
    unittest.main()
