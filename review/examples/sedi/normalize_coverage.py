"""Deterministic documentary view; does not certify source interpretations."""
import json
from pathlib import Path
from check_coverage import check, load

METHODS = ("AUTO", "EXPT", "ADMN")


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
        gaps = [k for k in ("authority_reference", "roles", "protection", "limitation", "evidence_needed", "risk_refs", "related_requirements", "disposition_rationale") if row[k] is None]
        if any(v["applicability"] is None for v in verification.values()):
            gaps.append("verification applicability")
        row["normalization_gaps"] = gaps
        rows.append(row)
    return {"schema": "sedi-normalized-documentary-view/v1", "archive_sha256": manifest["sha256"],
            "source_interpretations_independently_verified": False, "overall_assurance": "review-required",
            "records": rows,
            "summary": {"requirements": len(rows), "examined": sum(r["status"] != "indexed" for r in rows),
                        "numbered_objectives": sum(len(r.get("objectives", [])) for r in rows),
                        "records_with_normalization_gaps": sum(bool(r["normalization_gaps"]) for r in rows)}}


if __name__ == "__main__":
    print(json.dumps(normalize(load("requirement-coverage.json"), load("requirement-index.json"),
                               load("archive-manifest.json")), indent=2))
