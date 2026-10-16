import importlib.util
import pathlib
import tempfile
import unittest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "review" / "validate_spec_review.py"
spec = importlib.util.spec_from_file_location("validate_spec_review", VALIDATOR_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SpecReviewValidationTests(unittest.TestCase):
    def setUp(self):
        self.risks = ROOT / "data" / "risks.yaml"
        self.valid = yaml.safe_load((ROOT / "review" / "examples" / "minimal-review.yaml").read_text())

    def errors(self, record):
        return mod.validate_record(record, self.risks)

    def test_minimal_example_is_valid(self):
        self.assertEqual([], self.errors(self.valid))

    def test_missing_revision_is_rejected(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        del record["target"]["revision"]
        self.assertTrue(any("revision" in e for e in self.errors(record)))

    def test_mutable_branch_name_is_rejected_as_revision(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        record["target"]["revision"] = "main"
        self.assertTrue(any("does not match" in e for e in self.errors(record)))

    def test_duplicate_finding_id_is_rejected(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        record["findings"].append(yaml.safe_load(yaml.safe_dump(record["findings"][0])))
        self.assertTrue(any("duplicate finding identifier" in e for e in self.errors(record)))

    def test_unknown_risk_is_rejected(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        record["findings"][0]["risks"] = ["RK-ZZ99"]
        self.assertTrue(any("does not resolve" in e for e in self.errors(record)))

    def test_invalid_control_plane_is_rejected(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        record["findings"][0]["control_plane"] = "somewhere-else"
        self.assertTrue(any("control_plane" in e for e in self.errors(record)))

    def test_resolved_finding_requires_resolution(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        record["findings"][0]["status"] = "resolved"
        self.assertTrue(any("resolution" in e for e in self.errors(record)))

    def test_risk_acceptance_requires_reference(self):
        record = yaml.safe_load(yaml.safe_dump(self.valid))
        finding = record["findings"][0]
        finding["control_plane"] = "governance"
        finding["status"] = "risk_accepted"
        finding["resolution"] = {
            "type": "risk-acceptance",
            "rationale": "The competent authority accepted the bounded residual risk."
        }
        self.assertTrue(any("reference" in e for e in self.errors(record)))

    def test_invalid_mutable_revision_fixture_is_rejected(self):
        record = yaml.safe_load((ROOT / "review" / "examples" / "invalid-mutable-revision.yaml").read_text())
        self.assertTrue(any("does not match" in e for e in self.errors(record)))

    def test_invalid_unknown_risk_fixture_is_rejected(self):
        record = yaml.safe_load((ROOT / "review" / "examples" / "invalid-unknown-risk.yaml").read_text())
        self.assertTrue(any("does not resolve" in e for e in self.errors(record)))

    def test_invalid_resolved_fixture_is_rejected(self):
        record = yaml.safe_load((ROOT / "review" / "examples" / "invalid-resolved-without-resolution.yaml").read_text())
        self.assertTrue(any("resolution" in e for e in self.errors(record)))


    def test_review_vocabulary_matches_method_vocabularies(self):
        schema = mod.json.loads(mod.SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual([], mod.check_vocabulary(schema))

    def test_every_review_vocabulary_value_has_a_definition(self):
        vocab = yaml.safe_load(mod.VOCAB_PATH.read_text(encoding="utf-8"))
        for name in mod.REVIEW_VOCABULARIES.values():
            for value in vocab[name]["values"]:
                self.assertTrue(value.get("definition"), f"{name}: {value.get('value')} has no definition")

    def test_schema_enum_drift_is_rejected(self):
        schema = mod.json.loads(mod.SCHEMA_PATH.read_text(encoding="utf-8"))
        schema["properties"]["findings"]["items"]["properties"]["control_plane"]["enum"].append("vibes")
        errors = mod.check_vocabulary(schema)
        self.assertTrue(any("control_plane" in e and "vibes" in e for e in errors))

    def test_vocabulary_value_missing_from_schema_is_rejected(self):
        schema = mod.json.loads(mod.SCHEMA_PATH.read_text(encoding="utf-8"))
        schema["properties"]["findings"]["items"]["properties"]["status"]["enum"].remove("superseded")
        errors = mod.check_vocabulary(schema)
        self.assertTrue(any("finding_status" in e and "superseded" in e for e in errors))

    def test_missing_vocabulary_is_rejected(self):
        vocab = yaml.safe_load(mod.VOCAB_PATH.read_text(encoding="utf-8"))
        del vocab["resolution_type"]
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "vocabularies.yaml"
            path.write_text(yaml.safe_dump(vocab), encoding="utf-8")
            schema = mod.json.loads(mod.SCHEMA_PATH.read_text(encoding="utf-8"))
            errors = mod.check_vocabulary(schema, path)
        self.assertTrue(any("resolution_type" in e and "missing" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
