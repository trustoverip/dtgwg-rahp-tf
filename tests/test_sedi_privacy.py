"""Consistency checks for the separate SEDI privacy documentary tranche."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class SediPrivacyTests(unittest.TestCase):
    def test_privacy_scope_and_source_bindings(self):
        doc = load("privacy-examination.json")
        manifest = load("archive-manifest.json")
        self.assertEqual(doc["archive_sha256"], manifest["sha256"])
        members = {r["path"]: r for r in manifest["files"]}
        index = {r["id"] for r in load("requirement-index.json")["records"]}
        reqs = {r["id"]: r for r in doc["requirements"]}
        self.assertEqual(len(reqs), 12)
        self.assertEqual(len(doc["requirements"]), 12)
        self.assertTrue(set(reqs) <= index)
        for r in reqs.values():
            ref = r["source"]
            member = members[ref["member"]]
            self.assertEqual(ref["sha256"], member["sha256"])
            self.assertTrue(all(1 <= p <= member["pages"] for p in ref["pages"]))
            covered = set().union(*(set(r["verification"][k]) for k in ("AUTO", "EXPT", "ADMN")))
            self.assertEqual(covered, set(r["objectives"]))
        risks = {r["id"] for r in doc["hypotheses"]}
        self.assertEqual(len(risks), 5)
        self.assertEqual(len({r["id"] for r in doc["cases"]}), 6)
        self.assertEqual(set().union(*(set(r["requirements"]) for r in doc["cases"])), set(reqs))
        for case in doc["cases"]:
            self.assertIn(case["risk"], risks)
            self.assertEqual(case["status"], "open")
            self.assertEqual(case["operational_evidence"], "not acquired")
