"""Check WP-C source/coverage bindings and the explicit missing-source boundary."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class SediIdentityProofingTests(unittest.TestCase):
    def test_tranche(self):
        doc = load("identity-proofing-examination.json")
        manifest = load("archive-manifest.json")
        members = {r["path"]: r for r in manifest["files"]}
        register = {r["id"]: r for r in load("requirement-coverage.json")["records"]}
        self.assertEqual(doc["archive_sha256"], manifest["sha256"])
        self.assertEqual(len(doc["requirements"]), 15)
        self.assertEqual(len({r["id"] for r in doc["requirements"]}), 15)
        def check_source(ref):
            member = members[ref["member"]]
            self.assertEqual(ref["sha256"], member["sha256"])
            self.assertTrue(all(1 <= p <= member["pages"] for p in ref["pages"]))
        for r in doc["requirements"]:
            check_source(r["source"])
            self.assertEqual(set().union(*(set(v["objectives"]) for v in r["verification"].values())), set(r["objectives"]))
            self.assertTrue(set(r["related_requirements"]) <= register.keys())
            self.assertEqual(register[r["id"]]["examination"]["record"], "identity-proofing-examination.json")
            self.assertEqual(register[r["id"]]["disposition"], r["disposition"])
        gap, = doc["source_gaps"]
        self.assertEqual(gap["id"], "SEDI-IDP-08")
        for ref in gap["sources"]:
            check_source(ref)
        self.assertIsNone(gap["objectives"])
        self.assertIsNone(gap["verification"])
        self.assertEqual(register[gap["id"]]["status"], "indexed")
        self.assertIsNone(register[gap["id"]]["examination"])
        self.assertEqual(register[gap["id"]]["source_gap"]["id"], gap["id"])
        self.assertTrue(all(set(c["requirements"]) <= register.keys() for c in doc["cases"]))
