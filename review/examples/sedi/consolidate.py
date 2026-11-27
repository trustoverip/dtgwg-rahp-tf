"""Compose retained-source integrity and documentary consistency (not assurance)."""
import argparse
import json
from pathlib import Path
from normalize_coverage import normalize, load
from verify_archive import verify_archive

def compose(archive, loader=load):
    register = loader("requirement-coverage.json")
    manifest = loader("archive-manifest.json")
    integrity = verify_archive(archive, manifest)
    view = normalize(register, loader("requirement-index.json"), manifest, loader)
    index = loader("consolidation-index.json")
    if index["archive_sha256"] != manifest["sha256"] or index["rahp_baseline"] != register["rahp_baseline"]:
        raise ValueError("Consolidation baseline mismatch")
    risks, cases = {}, {}
    rows = {r["id"]: r for r in view["records"]}
    for name in index["records"]:
        if Path(name).name != name:
            raise ValueError("Unsafe record path")
        doc = loader(name)
        for risk in doc.get("hypotheses", doc.get("local_risks", [])):
            if risk["id"] in risks:
                raise ValueError("Duplicate risk")
            risks[risk["id"]] = risk
        for case in doc["cases"]:
            if case["id"] in cases:
                raise ValueError("Duplicate case")
            cases[case["id"]] = (name, case)
    if len(risks) != 31 or len(cases) != 47:
        raise ValueError("Unexpected risk/case universe")
    for row in rows.values():
        if not set(row.get("risk_refs") or []) <= risks.keys():
            raise ValueError("Unknown requirement risk")
        if not set(row.get("related_requirements") or []) <= rows.keys():
            raise ValueError("Unknown requirement dependency")
    findings = []
    seen = set()
    for f in index["findings"]:
        if f["case"] not in cases or f["case"] in seen or f["status"] != "open":
            raise ValueError("Invalid case or unsupported disposition")
        seen.add(f["case"])
        name, case = cases[f["case"]]
        refs = case.get("risks") or [case.get("risk")]
        reqs = case["requirements"]
        evidence = case.get("proposed_evidence") or case.get("evidence_needed") or case.get("evidence")
        if name != f["source_record"] or not refs or not set(refs) <= risks.keys() or not reqs or not set(reqs) <= rows.keys() or not evidence:
            raise ValueError("Invalid finding linkage")
        if case.get("status", "open") != "open" or case.get("operational_evidence", "not acquired") != "not acquired":
            raise ValueError("Unsupported case assurance claim")
        findings.append({**f, "risk_refs": refs, "requirements": reqs,
                         "sources": [rows[r].get("source") for r in reqs],
                         "proposition": case["constructed"], "evidence_needed": evidence,
                         "authority": case.get("authority"), "classification": "constructed; not observed"})
    if seen != cases.keys() or len({f["id"] for f in findings}) != len(findings):
        raise ValueError("Incomplete or duplicate finding index")
    return {**integrity, "coverage": view["summary"], "risks": list(risks.values()),
            "candidate_propositions": findings, "overall_assurance": "review-required",
            "formal_review": "not-established", "documentary_coverage_complete": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(compose(args.archive), indent=2))
