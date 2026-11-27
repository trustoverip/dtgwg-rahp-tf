"""Compose retained-source integrity and documentary consistency (not assurance)."""
import argparse
import json
from pathlib import Path
from normalize_coverage import normalize, load, require_complete as require_documentary_complete
from verify_archive import verify_archive

def compose(archive, loader=load, require_complete=False):
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
        if f["case"] not in cases or f["case"] in seen or f["status"] != "open" or "control_plane" in f:
            raise ValueError("Invalid case or unsupported disposition")
        seen.add(f["case"])
        name, case = cases[f["case"]]
        refs = case.get("risks") or [case.get("risk")]
        reqs = case["requirements"]
        evidence = case.get("proposed_evidence") or case.get("evidence_needed") or case.get("evidence")
        if name != f["source_record"] or not refs or not set(refs) <= risks.keys() or not reqs or not set(reqs) <= rows.keys() or not evidence:
            raise ValueError("Invalid finding linkage")
        if any(rows[r]["status"] == "indexed" or not rows[r].get("source") for r in reqs):
            raise ValueError("Case cites unexamined requirement")
        if case.get("status", "open") != "open" or case.get("operational_evidence", "not acquired") != "not acquired":
            raise ValueError("Unsupported case assurance claim")
        findings.append({**f, "risk_refs": refs, "requirements": reqs,
                         "sources": [rows[r].get("source") for r in reqs],
                         "proposition": case["constructed"], "evidence_needed": evidence,
                         "authority": case.get("authority"), "affected_context": view["affected_contexts"][f["case"]],
                         "classification": "constructed; not observed"})
    if seen != cases.keys() or len({f["id"] for f in findings}) != len(findings):
        raise ValueError("Incomplete or duplicate finding index")
    synthesis = loader("synthesis.json")
    if synthesis["archive_sha256"] != manifest["sha256"]:
        raise ValueError("Synthesis baseline mismatch")
    synth_ids = set()
    synthesis_cases = set()
    for finding in synthesis["findings"]:
        if finding["id"] in synth_ids or finding["status"] != "open" or not finding["authority"] or not finding["resolution_evidence"]:
            raise ValueError("Invalid synthesis disposition or authority")
        synth_ids.add(finding["id"])
        if finding["control_plane"] not in {"specification", "companion-specification", "governance", "implementation-guidance", "runtime-control", "operational-policy", "none"}:
            raise ValueError("Invalid control plane")
        if not set(finding["cases"]) <= cases.keys() or (not finding["cases"] and not finding.get("source_gap")):
            raise ValueError("Invalid synthesis binding")
        expected_requirements = set().union(*(set(cases[k][1]["requirements"]) for k in finding["cases"]))
        if finding.get("source_gap"):
            expected_requirements.add(finding["source_gap"])
        if (len(finding["requirements"]) != len(set(finding["requirements"]))
                or set(finding["requirements"]) != expected_requirements
                or not finding["observation"].strip()
                or not finding["interpretation"].strip()
                or not finding["design_protection"].strip()
                or not finding["recommendation"].strip()
                or not finding["interpretation_boundary"].strip()):
            raise ValueError("Incomplete synthesis reasoning or requirement binding")
        extra = finding.get("additional_requirements", [])
        extra_ids = [r["id"] for r in extra]
        if (len(set(extra_ids)) != len(extra_ids)
                or set(extra_ids) & expected_requirements
                or any(r["id"] not in rows or not rows[r["id"]].get("source") or not r["reason"].strip() for r in extra)):
            raise ValueError("Invalid additional synthesis source binding")
        synthesis_cases.update(finding["cases"])
        if finding.get("source_gap") and not rows.get(finding["source_gap"], {}).get("source_gap"):
            raise ValueError("Unknown source gap")
    if synthesis_cases != cases.keys():
        raise ValueError("Incomplete synthesis case coverage")
    source_bound_synthesis = [{**f, "sources": {r: rows[r].get("source") or rows[r].get("source_gap_record") for r in f["requirements"] + [x["id"] for x in f.get("additional_requirements", [])]}} for f in synthesis["findings"]]
    if require_complete:
        require_documentary_complete(view)
    return {**integrity, "coverage": view["summary"], "risks": list(risks.values()),
            "affected_contexts": view["affected_contexts"],
            "normalization_gaps": {r["id"]: r["normalization_gaps"] for r in view["records"] if r["normalization_gaps"]},
            "synthesis": source_bound_synthesis,
            "candidate_propositions": findings, "overall_assurance": "review-required",
            "formal_review": "not-established", "documentary_coverage_complete": all(r["status"] != "indexed" for r in rows.values()),
            "normalization_complete": not any(r["normalization_gaps"] for r in rows.values())}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--require-complete", action="store_true", help="Reject indexed-only or analytically incomplete documentary records")
    args = parser.parse_args()
    print(json.dumps(compose(args.archive, require_complete=args.require_complete), indent=2))
