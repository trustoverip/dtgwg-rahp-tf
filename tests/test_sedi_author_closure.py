"""Reject false documentary closure and preserve affected-context traceability."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "review/examples/sedi"
sys.path.insert(0, str(ROOT))
from normalize_coverage import normalize, load, require_complete
from check_coverage import check
from consolidate import compose


class SediAuthorClosureTests(unittest.TestCase):
    def setUp(self):
        self.register = load("requirement-coverage.json")
        self.index = load("requirement-index.json")
        self.manifest = load("archive-manifest.json")

    def view(self, loader=load):
        return normalize(self.register, self.index, self.manifest, loader)

    def test_qualified_documentary_view(self):
        view = self.view()
        self.assertEqual(view["summary"]["records_with_normalization_gaps"], 2)
        rows = {r["id"]: r for r in view["records"]}
        self.assertEqual({r["id"] for r in rows.values() if r["normalization_gaps"]},
                         {"SEDI-IDP-08", "SEDI-INT-04"})
        self.assertIsNone(rows["SEDI-INT-04"]["verification"]["ADMN"]["applicability"])
        gap = rows["SEDI-IDP-08"]["source_gap_record"]
        self.assertIsNone(gap["objectives"])
        self.assertEqual(len(gap["sources"]), 5)
        self.assertEqual(len(view["affected_contexts"]), 47)
        controls = [r for r in rows.values() if r.get("selected_objective_control")]
        self.assertEqual(len(controls), 7)
        self.assertEqual(sum(len(r["objectives"]) for r in controls), 32)
        self.assertIn("digital-enrollment-condition", rows["SEDI-APP-04"]["associated_cases"])
        self.assertTrue(all(r["risk_relevance"]["harms"] for r in rows.values() if r["status"] != "indexed"))
        self.assertFalse(view["source_interpretations_independently_verified"])

    def test_strict_consumer_and_inventory_api(self):
        with self.assertRaisesRegex(ValueError, "SEDI-IDP-08.*SEDI-INT-04"):
            check(self.register, self.index, self.manifest, require_complete=True)
        with patch("consolidate.verify_archive", return_value={}), self.assertRaisesRegex(ValueError, "SEDI-IDP-08.*SEDI-INT-04"):
            compose("fixture", require_complete=True)
        # The guard also rejects an analytical gap even without an indexed-only record.
        with self.assertRaisesRegex(ValueError, "SEDI-FIXTURE: limitation"):
            require_complete({"records": [{"id": "SEDI-FIXTURE", "status": "examined", "normalization_gaps": ["limitation"]}]})
        require_complete({"records": [{"id": "SEDI-FIXTURE", "status": "examined", "normalization_gaps": []}]})

    def test_false_closure_mutations(self):
        for mutation in ("missing-limitation", "blank-limitation", "context-missing", "context-duplicate",
                         "context-unknown", "control-missing", "control-method", "gap-objectives", "gap-digest",
                         "unknown-risk", "self-dependency", "synthesis-interpretation", "synthesis-protection"):
            with self.subTest(mutation=mutation):
                def loader(name):
                    d = copy.deepcopy(load(name))
                    if name == "legacy-analysis.json":
                        if mutation == "missing-limitation":
                            d["limitations"].pop("SEDI-BOR-02")
                        elif mutation == "blank-limitation":
                            d["limitations"]["SEDI-BOR-02"] = " "
                        elif mutation == "context-missing":
                            d["context_groups"][0]["cases"].pop()
                        elif mutation == "context-duplicate":
                            d["context_groups"][0]["cases"].append(d["context_groups"][1]["cases"][0])
                        elif mutation == "context-unknown":
                            d["context_groups"][0]["cases"].append("fixture-unknown")
                    elif name == "objective-controls.json":
                        if mutation == "control-missing":
                            d["records"].pop()
                        elif mutation == "control-method":
                            d["records"][0]["verification"]["ADMN"]["objectives"] = []
                    elif name == "identity-proofing-examination.json":
                        if mutation == "gap-objectives":
                            d["source_gaps"][0]["objectives"] = [1]
                        elif mutation == "gap-digest":
                            d["source_gaps"][0]["sources"][0]["sha256"] = "0" * 64
                    elif name == "technical-architecture-examination.json":
                        r = d["requirements"][0]
                        if mutation == "unknown-risk":
                            r["risk_refs"] = ["EX-RK-UNKNOWN"]
                        elif mutation == "self-dependency":
                            r["related_requirements"] = [r["id"]]
                    elif name == "synthesis.json":
                        if mutation == "synthesis-interpretation":
                            d["findings"][0]["interpretation"] = " "
                        elif mutation == "synthesis-protection":
                            d["findings"][0]["design_protection"] = " "
                    return d
                with patch("consolidate.verify_archive", return_value={}), self.assertRaises(ValueError):
                    compose("fixture", loader)

    def test_blank_tranche_metadata_is_not_complete(self):
        def loader(name):
            d = copy.deepcopy(load(name))
            if name == "technical-architecture-examination.json":
                d["requirements"][0]["limitation"] = " "
            return d
        view = self.view(loader)
        self.assertEqual(view["summary"]["records_with_normalization_gaps"], 3)
        r = next(r for r in view["records"] if r["id"] == load("technical-architecture-examination.json")["requirements"][0]["id"])
        self.assertIn("limitation", r["normalization_gaps"])
        with self.assertRaisesRegex(ValueError, r["id"] + ": limitation"):
            require_complete(view)
