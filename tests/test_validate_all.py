"""Increment 3 validation composition and drift regression tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_all", ROOT / "tools/validate_all.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VocabularyTests(unittest.TestCase):
    def test_repository_vocabulary_compatible(self):
        self.assertEqual(module.check_vocabulary(), [])

    def test_changed_review_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            schema = json.loads(module.REVIEW_SCHEMA.read_text())
            schema["properties"]["findings"]["items"]["properties"]["status"]["enum"].append("approved")
            path = Path(td) / "schema.json"
            path.write_text(json.dumps(schema))
            self.assertTrue(any("review vocabulary drift: status" in e
                                for e in module.check_vocabulary(path)))

    def test_duplicate_method_value_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            import yaml
            vocab = yaml.safe_load(module.METHOD_VOCAB.read_text())
            vocab["control_type"]["values"].append(vocab["control_type"]["values"][0])
            path = Path(td) / "vocab.yaml"
            path.write_text(yaml.safe_dump(vocab))
            self.assertTrue(any("duplicate" in e for e in
                                module.check_vocabulary(method_path=path)))

    @patch.object(module, "check_vocabulary", return_value=[])
    @patch.object(module.subprocess, "run")
    def test_selected_reviews_are_explicit_and_fail_closed(self, run, _):
        run.side_effect = [SimpleNamespace(returncode=0), SimpleNamespace(returncode=1)]
        self.assertEqual(module.validate(Path("data"), [Path("bad.yaml")]), 1)
        self.assertEqual(run.call_count, 2)
        self.assertIn("bad.yaml", run.call_args.args[0])

    @patch.object(module, "check_vocabulary", return_value=[])
    @patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=0))
    def test_no_review_does_not_imply_review_validation(self, run, _):
        self.assertEqual(module.validate(Path("data"), []), 0)
        self.assertEqual(run.call_count, 1)

    @patch.object(module, "check_vocabulary", return_value=["schema drift"])
    @patch.object(module.subprocess, "run")
    def test_vocabulary_drift_stops_execution(self, run, _):
        self.assertEqual(module.validate(Path("data"), []), 1)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
