"""Source-pinning, comparison, inventory and failure-isolation tests (offline)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from runner.service import (ConfigurationError, read_inventory, validate, acquire,
                            run_service, report_comparison, relative_file)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "runner/examples/service.yaml"
DTG_CONFIG = ROOT / "runner/examples/dtg-service.yaml"


class EvaluationServiceTests(unittest.TestCase):
    def test_reference_configs_validate(self):
        config, meta = validate(CONFIG)
        self.assertEqual(len(config["targets"]), 3)
        self.assertEqual(len(meta["targets"]), 3)
        selected, _ = validate(DTG_CONFIG)
        self.assertEqual(len(selected["targets"]), 2)

    def test_portfolio_inventory_is_advisory_and_pinned(self):
        config = yaml.safe_load(DTG_CONFIG.read_text())
        registry, entries = read_inventory(DTG_CONFIG.parent, config["inventory"])
        self.assertIn("trustoverip/dtgwg-cred-tf", registry)
        self.assertEqual(entries["trustoverip/dtgwg-cred-spec"]["role"],
                         "normative-specification")
        with self.assertRaises(ConfigurationError):
            read_inventory(DTG_CONFIG.parent, {**config["inventory"], "sha256": "0" * 64})

    def test_path_escape_and_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "safe.yaml").write_text("{}\n")
            self.assertEqual(relative_file(root, "safe.yaml"), root / "safe.yaml")
            for name in ("../unsafe", "/tmp/unsafe", "a\\b", "repo://../README.md"):
                with self.assertRaises(ConfigurationError):
                    relative_file(root, name)
            (root / "alias").symlink_to(ROOT / "README.md")
            with self.assertRaises(ConfigurationError):
                relative_file(root, "alias")

    def test_invalid_ref_and_unbound_review_rejected(self):
        doc = yaml.safe_load(CONFIG.read_text())
        doc["targets"][0]["ref"] = "refs/heads/main..old"
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.yaml"
            path.write_text(yaml.safe_dump(doc))
            with self.assertRaises(ConfigurationError):
                validate(path)

    def test_comparison_does_not_infer_resolution_from_absence(self):
        key = "compatible"
        old = {"comparison_key": key, "execution": {"state": "completed"},
               "findings": {"F-001": "open", "F-002": "open"}}
        new = {"comparison_key": key, "findings": {"F-001": "resolved"}}
        diff = report_comparison(old, new)
        self.assertEqual(diff["state"], "comparable")
        self.assertIn({"finding": "F-002", "before": "open", "after": "absent"}, diff["changes"])
        self.assertEqual(report_comparison({**old, "comparison_key": "different"}, new)["state"],
                         "not-comparable")

    def test_actual_review_validator_multiple_targets_and_history_offline(self):
        # Simulates acquisition of fixed source bytes; the actual installed review
        # validator runs, and no network or downstream controller is consulted.
        configs = yaml.safe_load(DTG_CONFIG.read_text())
        payload = b"retained source placeholder, not an asserted Git identity"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for t in configs["targets"]:
                t["artifact_sha256"] = hashlib.sha256(payload).hexdigest()
            config = root / "config.yaml"
            # Use repo:// for reference to known checked-in example inventory
            configs["inventory"]["path"] = "repo://runner/examples/dtg-curated.yaml"
            config.write_text(yaml.safe_dump(configs))
            output = root / "runs"

            def staged_source(target, directory):
                directory.mkdir()
                (directory / "dtg.md").write_bytes(payload)
                return target["revision"], directory

            reports, result = run_service(config, output, acquire_source=staged_source)
            self.assertEqual(result, 0)
            self.assertEqual(len(reports), 2)
            self.assertTrue(all(x["execution"]["assurance"] == "review-required" for x in reports))
            self.assertEqual(reports[0]["comparison"]["state"], "no-baseline")
            self.assertEqual(reports[1]["comparison"]["state"], "comparable")
            self.assertIn({"finding": "F-001", "before": "open", "after": "resolved"},
                          reports[1]["comparison"]["changes"])
            self.assertTrue(list(output.glob("*/evaluation.md")))

    def test_failed_target_does_not_hide_other_target(self):
        doc = yaml.safe_load(DTG_CONFIG.read_text())
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            doc["inventory"]["path"] = "repo://runner/examples/dtg-curated.yaml"
            config = root / "service.yaml"
            config.write_text(yaml.safe_dump(doc))

            def acquire_one_failure(target, directory):
                if target["id"] == "vrc-baseline":
                    raise ConfigurationError("fixture source intentionally unavailable")
                directory.mkdir()
                (directory / "dtg.md").write_text("present")
                return target["revision"], directory

            reports, status = run_service(config, root / "runs", acquire_source=acquire_one_failure)
            self.assertEqual(status, 1)
            self.assertEqual(reports[0]["execution"]["state"], "failed")
            self.assertEqual(reports[0]["execution"]["assurance"], "not-assessed")
            self.assertEqual(reports[1]["execution"]["state"], "completed")

    @patch("runner.service.git")
    def test_source_acquisition_requires_expected_commit(self, fake_git):
        # No subprocess or GitHub traffic: test the strict revision binding.
        fake_git.side_effect = ["x" * 40 + "\trefs/heads/main", "", "", "x" * 40, ""]
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ConfigurationError):
                acquire({"repository": "trustoverip/dtgwg-cred-tf",
                         "ref": "main", "revision": "a" * 40}, Path(d) / "git")


if __name__ == "__main__":
    unittest.main()
