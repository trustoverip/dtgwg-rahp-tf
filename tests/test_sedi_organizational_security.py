"""Validate source, objective and register bindings for WP-F."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class SediOrganizationalSecurityTests(unittest.TestCase):
    def test_tranche(self):
        doc = load("organizational-security-examination.json")
        manifest = load("archive-manifest.json")
        members = {r["path"]: r for r in manifest["files"]}
        register = {r["id"]: r for r in load("requirement-coverage.json")["records"]}
        self.assertEqual(doc["archive_sha256"], manifest["sha256"])
        self.assertEqual(len(doc["requirements"]), 7)
        self.assertEqual(len({r["id"] for r in doc["requirements"]}), 7)
        for r in doc["requirements"]:
            ref = r["source"]
            member = members[ref["member"]]
            self.assertEqual(ref["sha256"], member["sha256"])
            self.assertTrue(all(1 <= p <= member["pages"] for p in ref["pages"]))
            self.assertEqual(set().union(*(set(v["objectives"]) for v in r["verification"].values())), set(r["objectives"]))
            self.assertTrue(set(r["related_requirements"]) <= register.keys())
            self.assertEqual(register[r["id"]]["examination"]["record"], "organizational-security-examination.json")
            self.assertEqual(register[r["id"]]["disposition"], r["disposition"])
            self.assertEqual(r["operational_evidence"], "not acquired")
