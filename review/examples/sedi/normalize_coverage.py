"""Deterministic documentary view; does not certify source interpretations."""
import json
from pathlib import Path
from check_coverage import check, load

METHODS = ("AUTO", "EXPT", "ADMN")



LEGACY_RECORDS = {"initial-requirements.json", "companion-requirements.json",
                  "privacy-examination.json", "lifecycle-examination.json",
                  "delegation-examination.json", "conformance-examination.json"}
REQUIRED_ANALYSIS = ("authority_reference", "roles", "protection", "limitation",
                     "evidence_needed", "risk_refs", "related_requirements",
                     "disposition_rationale", "risk_relevance")


def present(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple)):
        return bool(value) and all(present(x) for x in value)
    return bool(value)


def reconcile(rows, manifest, loader):
    """Derive analytical links from existing examination records, not new risk claims."""
    notes = loader("legacy-analysis.json")
    if (notes["schema"] != "sedi-legacy-analytical-reconciliation/v1"
            or notes["archive_sha256"] != manifest["sha256"]):
        raise ValueError("Invalid analytical reconciliation baseline")
    case_records, risk_records = {}, {}
    for name in loader("consolidation-index.json")["records"]:
        if Path(name).name != name:
            raise ValueError("Unsafe analytical record path")
        doc = loader(name)
        for risk in doc.get("hypotheses", doc.get("local_risks", [])):
            if risk["id"] in risk_records:
                raise ValueError("Duplicate analytical risk")
            risk_records[risk["id"]] = risk
        for case in doc["cases"]:
            if case["id"] in case_records:
                raise ValueError("Duplicate analytical case")
            case_records[case["id"]] = case
    contexts = {}
    for group in notes["context_groups"]:
        if not present(group["context"]) or not present(group["reason"]) or not group["cases"]:
            raise ValueError("Incomplete affected-context justification")
        for case_id in group["cases"]:
            if case_id in contexts or case_id not in case_records:
                raise ValueError("Duplicate or unknown affected-context case")
            contexts[case_id] = {"context": group["context"], "reason": group["reason"]}
    if contexts.keys() != case_records.keys():
        raise ValueError("Missing affected-context case")
    known_ids = {r["id"] for r in rows}
    by_requirement = {i: set() for i in known_ids}
    for case_id, case in case_records.items():
        refs = case.get("risks") or [case.get("risk")]
        if not refs or not set(refs) <= risk_records.keys() or not set(case["requirements"]) <= known_ids:
            raise ValueError("Invalid analytical case binding")
        for req in case["requirements"]:
            by_requirement[req].add(case_id)
    used_risks = {risk for case in case_records.values() for risk in (case.get("risks") or [case.get("risk")])}
    if used_risks != risk_records.keys() or not all(present(r["harm"]) for r in risk_records.values()):
        raise ValueError("Missing risk-to-case or harm linkage")
    # Companion requirements participate through the existing bounded review bindings.
    bindings = loader("review-candidate.json")["bindings"]
    for binding in bindings:
        if not set(binding["requirements"]) <= known_ids or not set(binding["cases"]) <= case_records.keys():
            raise ValueError("Invalid bounded review binding")
        for req in binding["requirements"]:
            by_requirement[req].update(binding["cases"])
    control_rows = loader("objective-controls.json")["records"]
    controls = {r["id"]: r for r in control_rows}
    legacy = {r["id"] for r in rows if r["examination_reference"] and r["examination_reference"]["record"] in LEGACY_RECORDS}
    selected = {r["id"] for r in rows if r["examination_reference"] and r["examination_reference"]["record"] in {"initial-requirements.json", "companion-requirements.json"}}
    if len(controls) != len(control_rows) or controls.keys() != selected:
        raise ValueError("Invalid selected objective-control records")
    expected_limits = {r["id"] for r in rows if r["id"] in legacy and not r.get("limitation")}
    if set(notes["limitations"]) != expected_limits or not all(present(x) for x in notes["limitations"].values()):
        raise ValueError("Missing, extra or blank legacy limitation")
    members = {m["path"]: m for m in manifest["files"]}
    for row in rows:
        if row["status"] == "indexed":
            ref = row.get("source_gap")
            if not ref or ref["id"] != row["id"] or Path(ref["record"]).name != ref["record"]:
                raise ValueError("Missing or invalid indexed source-gap reference")
            matches = [r for r in loader(ref["record"])["source_gaps"] if r["id"] == row["id"]]
            if len(matches) != 1:
                raise ValueError("Missing or duplicate source-gap record")
            gap = matches[0]
            if (gap["status"] != "source-gap" or gap["objectives"] is not None or gap["verification"] is not None
                    or gap["operational_evidence"] != "not acquired" or not gap["sources"]
                    or not gap["risk_refs"] or not set(gap["risk_refs"]) <= risk_records.keys()
                    or not set(gap["related_requirements"]) <= known_ids - {row["id"]}
                    or not all(present(gap[k]) for k in ("observation", "evidence_needed", "potential_harm"))):
                raise ValueError("Invalid source-gap examination boundary")
            for source in gap["sources"]:
                member = members.get(source["member"], {})
                if (source["sha256"] != member.get("sha256") or not source["pages"]
                        or any(type(n) is not int or not 1 <= n <= member.get("pages", 0) for n in source["pages"])):
                    raise ValueError("Invalid source-gap citation")
            row["source_gap_record"] = gap
            continue
        req = row["id"]
        case_ids = sorted(by_requirement[req])
        row["associated_cases"] = case_ids
        row["case_risk_refs"] = sorted({risk for cid in case_ids for risk in (case_records[cid].get("risks") or [case_records[cid].get("risk")])})
        if req in legacy:
            if not case_ids:
                raise ValueError(f"{req}: legacy analytical linkage missing")
            control = controls.get(req)
            if control:
                if (control["objectives"] != row["objectives"] or not control["risks"]
                        or not set(control["risks"]) <= risk_records.keys()
                        or not all(present(control[k]) for k in ("control", "authority", "assurance_test", "guardrail"))
                        or control["operational_evidence"] != "not acquired"):
                    raise ValueError(f"{req}: invalid selected objective-control record")
                for method in METHODS:
                    declared = control["verification"][method]
                    objectives = declared if isinstance(declared, list) else declared["objectives"]
                    if (objectives != row["verification"][method]["objectives"]
                            or (isinstance(declared, dict) and declared.get("applicability") != row["verification"][method]["applicability"])):
                        raise ValueError(f"{req}: selected objective-control method mismatch")
                row["selected_objective_control"] = control
                row["risk_refs"] = control["risks"]
                row["protection"] = row["protection"] or control["control"]
                basis = "Explicit selected objective-control mapping; case risk links are separately recorded."
            else:
                row["risk_refs"] = row["case_risk_refs"]
                basis = "Requirement participates in the cited constructed cases; risk relevance is contextual, not proof of an individual objective's effectiveness."
            row["risk_relevance"] = {"basis": basis, "harms": [risk_records[r]["harm"] for r in row["risk_refs"]]}
            row["limitation"] = row["limitation"] or notes["limitations"][req]
            case_evidence = []
            related = set()
            for cid in case_ids:
                case = case_records[cid]
                evidence = case.get("proposed_evidence") or case.get("evidence_needed") or case.get("evidence")
                if not present(evidence):
                    raise ValueError(f"{cid}: missing evidence request")
                case_evidence.append(f"{cid}: {evidence}")
                related.update(case["requirements"])
            for binding in bindings:
                if req in binding["requirements"]:
                    related.update(binding["requirements"])
            row["related_requirements"] = sorted(related - {req})
            row["relationship_basis"] = "Co-examination in cited cases or bounded review bindings; not asserted as a normative dependency."
            row["evidence_needed"] = row["evidence_needed"] or case_evidence
            row["case_evidence_requests"] = case_evidence
            row["disposition_rationale"] = "Evidence required: " + row["limitation"]
        else:
            if not set(row.get("risk_refs") or []) <= risk_records.keys():
                raise ValueError(f"{req}: unknown local risk")
            row["risk_relevance"] = {"basis": "Explicit requirement-level analytical mapping in the referenced coverage tranche.",
                                     "harms": [risk_records[r]["harm"] for r in row.get("risk_refs") or []]}
            row["relationship_basis"] = "Recorded analytical relationships in coverage tranche; not asserted as normative dependencies."
        if not set(row.get("related_requirements") or []) <= known_ids - {req}:
            raise ValueError(f"{req}: invalid related requirement")
        row["normalization_gaps"] = [k for k in REQUIRED_ANALYSIS if not present(row.get(k))]
        if not row["risk_relevance"]["harms"]:
            row["normalization_gaps"].append("risk relevance harms")
        if any(v["applicability"] is None for v in row["verification"].values()):
            row["normalization_gaps"].append("verification applicability undeclared or unresolved")
    return contexts


def require_complete(view):
    """Reject incomplete documentary/analytical coverage, not open operational risks."""
    incomplete = [r for r in view["records"] if r["status"] == "indexed" or r["normalization_gaps"]]
    if incomplete:
        details = "; ".join(f'{r["id"]}: {", ".join(r["normalization_gaps"])}' for r in incomplete)
        raise ValueError("Incomplete documentary examination: " + details)


def normalize(register, index, manifest, loader=load):
    check(register, index, manifest, loader)
    members = {m["path"]: m for m in manifest["files"]}
    part1, = [m for m in members.values() if Path(m["path"]).name.startswith("Part 1_")]
    docs = {}
    rows = []
    for entry in register["records"]:
        row = {k: entry[k] for k in ("id", "index_page", "status", "disposition", "review_state")}
        row["operational_evidence"] = "not acquired"
        row["examination_reference"] = entry["examination"]
        if entry["status"] == "indexed":
            row["source_gap"] = entry.get("source_gap")
            row["normalization_gaps"] = ["detailed examination unavailable"]
            rows.append(row)
            continue
        name = entry["examination"]["record"]
        if name not in docs:
            docs[name] = loader(name)
        doc = docs[name]
        source, = [r for r in doc["requirements"] if r["id"] == entry["id"]]
        binding = source.get("source")
        if binding is None and name == "initial-requirements.json":
            binding = {"member": part1["path"], "sha256": part1["sha256"], "pages": source["pdf_pages"]}
        if not binding or binding["member"] not in members:
            raise ValueError(f'{entry["id"]}: missing source member')
        member = members[binding["member"]]
        pages = binding["pages"]
        if binding["sha256"] != member["sha256"] or not pages or pages != sorted(set(pages)) or any(type(n) is not int or not 1 <= n <= member["pages"] for n in pages):
            raise ValueError(f'{entry["id"]}: invalid source binding')
        objectives = source["objectives"]
        if objectives != list(range(1, len(objectives) + 1)) or not objectives:
            raise ValueError(f'{entry["id"]}: invalid objective sequence')
        verification = {}
        raw = source["verification"]
        for method in METHODS:
            v = raw[method]
            if isinstance(v, list):
                v = {"objectives": v, "applicability": source.get("verification_applicability", {}).get(method)}
            else:
                v = dict(v)
            v.setdefault("applicability", None)
            if v["applicability"] not in (None, "Mandatory", "Recommended", "N/A"):
                raise ValueError(f'{entry["id"]}: invalid applicability')
            if len(set(v["objectives"])) != len(v["objectives"]) or not set(v["objectives"]) <= set(objectives):
                raise ValueError(f'{entry["id"]}: invalid method objective binding')
            if v["applicability"] == "N/A" and v["objectives"]:
                raise ValueError(f'{entry["id"]}: N/A method has objective coverage')
            if raw.get(method + "_parameter_check"):
                v["parameter_check"] = True
            verification[method] = v
        if set().union(*(set(v["objectives"]) for v in verification.values())) != set(objectives):
            raise ValueError(f'{entry["id"]}: incomplete objective coverage')
        roles = source.get("roles")
        if isinstance(roles, str):
            roles = [r.strip() for r in roles.split(",")]
        row.update(source=binding, authority_reference=source.get("authority_reference", source.get("statute")),
                   roles=roles, objectives=objectives, verification=verification,
                   protection=source.get("protection", source.get("observation")),
                   limitation=source.get("limitation"),
                   evidence_needed=source.get("evidence_needed", source.get("evidence_categories", source.get("treatment"))),
                   risk_refs=source.get("risk_refs"), related_requirements=source.get("related_requirements"),
                   disposition_rationale=source.get("disposition_rationale"),
                   implementation_decision=source.get("decision"))
        rows.append(row)
    contexts = reconcile(rows, manifest, loader)
    return {"schema": "sedi-normalized-documentary-view/v1",
            "affected_contexts": contexts, "archive_sha256": manifest["sha256"],
            "source_interpretations_independently_verified": False, "overall_assurance": "review-required",
            "records": rows,
            "summary": {"requirements": len(rows), "examined": sum(r["status"] != "indexed" for r in rows),
                        "numbered_objectives": sum(len(r.get("objectives", [])) for r in rows),
                        "records_with_normalization_gaps": sum(bool(r["normalization_gaps"]) for r in rows)}}


if __name__ == "__main__":
    print(json.dumps(normalize(load("requirement-coverage.json"), load("requirement-index.json"),
                               load("archive-manifest.json")), indent=2))
