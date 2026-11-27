"""Consistency checks for the SEDI conformance documentary tranche."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class SediConformanceTests(unittest.TestCase):
    def test_scope_and_bindings(self):
        doc = load("conformance-examination.json")
        manifest = load("archive-manifest.json")
        self.assertEqual(doc["archive_sha256"], manifest["sha256"])
        members = {r["path"]: r for r in manifest["files"]}
        index = {r["id"] for r in load("requirement-index.json")["records"]}
        reqs = {r["id"]: r for r in doc["requirements"]}
        self.assertEqual(len(reqs), 7)
        self.assertEqual(len(doc["requirements"]), 7)
        self.assertTrue(set(reqs) <= index)
        for r in reqs.values():
            ref = r["source"]
            member = members[ref["member"]]
            self.assertEqual(ref["sha256"], member["sha256"])
            self.assertTrue(all(1 <= p <= member["pages"] for p in ref["pages"]))
            self.assertEqual(set().union(*(set(r["verification"][k]) for k in ("AUTO", "EXPT", "ADMN"))), set(r["objectives"]))
        framework = doc["framework"]["source"]
        self.assertEqual(framework["sha256"], members[framework["member"]]["sha256"])
        self.assertTrue(all(1 <= p <= members[framework["member"]]["pages"] for p in framework["pages"]))
        risks = {r["id"] for r in doc["hypotheses"]}
        self.assertEqual(len(risks), 5)
        self.assertEqual(len({r["id"] for r in doc["cases"]}), 6)
        self.assertEqual(set().union(*(set(r["requirements"]) for r in doc["cases"])), set(reqs))
        for case in doc["cases"]:
            self.assertIn(case["risk"], risks)
            self.assertEqual(case["status"], "open")
            self.assertEqual(case["operational_evidence"], "not acquired")
