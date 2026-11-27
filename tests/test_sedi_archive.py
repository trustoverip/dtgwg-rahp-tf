"""Regression tests for local archive verification and candidate boundaries."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"
SPEC = importlib.util.spec_from_file_location("sedi_verify_archive", ROOT / "verify_archive.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class SediArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fixture.zip"
        self.data = b"synthetic fixture, not SEDI source"
        with zipfile.ZipFile(self.path, "w") as archive:
            archive.writestr("source.pdf", self.data)
        self.manifest = {"sha256": sha(self.path.read_bytes()),
                         "files": [{"path": "source.pdf", "bytes": len(self.data),
                                    "sha256": sha(self.data)}]}

    def test_exact_input(self):
        result = MODULE.verify_archive(self.path, self.manifest)
        self.assertEqual(result["verified_members"], 1)
        self.assertEqual(result["publisher_release_identity"], "not-established")

    def test_archive_mismatch(self):
        self.path.write_bytes(self.path.read_bytes() + b"changed")
        with self.assertRaises(ValueError):
            MODULE.verify_archive(self.path, self.manifest)

    def test_member_mismatch(self):
        self.manifest["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            MODULE.verify_archive(self.path, self.manifest)

    def test_missing_unexpected_duplicate_and_unsafe_members(self):
        for names in (["other.pdf"], ["source.pdf", "extra.pdf"],
                      ["source.pdf", "../escape.pdf"]):
            with self.subTest(names=names):
                with zipfile.ZipFile(self.path, "w") as archive:
                    for name in names:
                        archive.writestr(name, self.data)
                self.manifest["sha256"] = sha(self.path.read_bytes())
                with self.assertRaises(ValueError):
                    MODULE.verify_archive(self.path, self.manifest)

    def test_duplicate_manifest_member(self):
        self.manifest["files"].append(copy.deepcopy(self.manifest["files"][0]))
        with self.assertRaises(ValueError):
            MODULE.verify_archive(self.path, self.manifest)


class SediCandidateTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("sedi_examine", ROOT / "examine.py")
        import sys
        sys.path.insert(0, str(ROOT))
        self.addCleanup(sys.path.remove, str(ROOT))
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.candidate = json.loads((ROOT / "review-candidate.json").read_text())
        self.original_load = self.module.load

    def run_candidate(self, candidate):
        with patch.object(self.module, "verify_archive", return_value={"source_integrity": "fixture-only"}), \
             patch.object(self.module, "load", side_effect=lambda n: candidate if n == "review-candidate.json" else self.original_load(n)):
            return self.module.examine("unused-fixture-path")

    def test_valid_candidate_never_formal_review(self):
        result = self.run_candidate(self.candidate)
        self.assertEqual(result["formal_review"], "not-established")
        self.assertEqual(result["overall_assurance"], "review-required")

    def test_false_success_mutations(self):
        for mutation in ("target", "reviewer", "status", "missing-binding", "digest", "page", "risk"):
            with self.subTest(mutation=mutation):
                candidate = copy.deepcopy(self.candidate)
                if mutation == "target":
                    candidate["target"]["sha256"] = "0" * 64
                elif mutation == "reviewer":
                    candidate["reviewer"] = "unverified reviewer"
                elif mutation == "status":
                    candidate["findings"][0]["status"] = "risk_accepted"
                elif mutation == "missing-binding":
                    candidate["bindings"].pop()
                elif mutation == "digest":
                    candidate["bindings"][0]["sources"][0]["sha256"] = "0" * 64
                elif mutation == "page":
                    candidate["bindings"][0]["sources"][0]["pages"] = [0]
                else:
                    candidate["findings"][0]["risks"] = ["EX-RK-HX99"]
                with self.assertRaises(ValueError):
                    self.run_candidate(candidate)


if __name__ == "__main__":
    unittest.main()
