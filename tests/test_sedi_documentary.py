"""Check consistency of SEDI documentary examination records."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class SediDocumentaryTests(unittest.TestCase):
    def test_index_and_bindings(self):
        index = load("requirement-index.json")
        records = index["records"]
        ids = {r["id"] for r in records}
        self.assertEqual(len(records), 142)
        self.assertEqual(len(ids), 142)
        manifest = {r["path"]: r for r in load("archive-manifest.json")["files"]}
        roles = load("role-mappings.json")
        cases = load("cases.json")
        for ref in (index["source"], roles["source_matrix"], roles["source_roles"],
                    roles["source_requirements"], roles["companion_source"], cases["source"]):
            self.assertEqual(ref["sha256"], manifest[ref["member"]]["sha256"])
        self.assertTrue(all(1 <= r["pdf_page"] <= manifest[index["source"]["member"]]["pages"] for r in records))
        scoped = {r["id"] for r in roles["mappings"]}
        self.assertEqual(scoped, {"SEDI-BOR-03", "SEDI-BOR-04", "SEDI-BOR-09"})
        self.assertTrue(scoped <= ids)
        self.assertTrue({r["id"] for r in roles["companion_requirements"]} <= ids)
        hypotheses = {r["id"] for r in cases["hypotheses"]}
        contexts = {r["id"] for r in cases["contexts"]}
        self.assertEqual(len(cases["cases"]), 5)
        for case in cases["cases"]:
            self.assertTrue(set(case["requirements"]) <= scoped)
            self.assertTrue(set(case["risks"]) <= hypotheses)
            self.assertTrue(set(case["contexts"]) <= contexts)
            self.assertTrue(case["evidence_needed"])
        missing = next(c for c in cases["cases"] if c["id"] == "evidence-missing")
        self.assertIn("indeterminate", missing["candidate_disposition"])


if __name__ == "__main__":
    unittest.main()
