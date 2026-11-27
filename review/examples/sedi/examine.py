"""Validate the SEDI local candidate; never substitute a Git revision."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))
from validate_spec_review import check_finding_semantics, check_vocabulary
from jsonschema import Draft202012Validator
from verify_archive import verify_archive


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def examine(archive):
    manifest = load("archive-manifest.json")
    integrity = verify_archive(archive, manifest)
    candidate = load("review-candidate.json")
    if (candidate["schema"] != "sedi-local-review-candidate/v1"
            or candidate["target"] != {"kind": "local-archive",
                                       "sha256": manifest["sha256"],
                                       "manifest": "archive-manifest.json",
                                       "publisher_release_identity": "not independently established"}
            or candidate["reviewer"] is not None
            or candidate["review_state"] != "awaiting-accountable-review"):
        raise ValueError("Unsupported candidate identity or review state")
    cases = load("cases.json")
    risks = {r["id"]: r for r in cases["hypotheses"]}
    case_ids = {r["id"] for r in cases["cases"]}
    req_ids = {r["id"] for r in load("requirement-index.json")["records"]}
    sources = {r["path"]: r for r in manifest["files"]}
    schema = json.loads((ROOT.parents[1] / "spec-review.schema.json").read_text())
    errors = check_vocabulary(schema)
    finding_validator = Draft202012Validator(schema["properties"]["findings"])
    errors.extend(e.message for e in finding_validator.iter_errors(candidate["findings"]))
    ids = [f["id"] for f in candidate["findings"]]
    if not ids or len(ids) != len(set(ids)):
        errors.append("Empty or duplicate findings")
    for f in candidate["findings"]:
        if f["status"] != "open" or "resolution" in f or not set(f["risks"]) <= risks.keys():
            errors.append("Unsupported candidate finding disposition or risk")
        errors.extend(check_finding_semantics(f, risks, {}))
    bindings = candidate["bindings"]
    if sorted(b["finding"] for b in bindings) != sorted(ids):
        errors.append("Missing or duplicate finding binding")
    for b in bindings:
        if (not b["cases"] or not set(b["cases"]) <= case_ids
                or not b["requirements"] or not set(b["requirements"]) <= req_ids
                or not b["sources"] or not b["resolution_evidence"]):
            errors.append("Incomplete evidence binding")
        for ref in b["sources"]:
            record = sources.get(ref["member"], {})
            if (ref["sha256"] != record.get("sha256") or not ref["pages"]
                    or any(type(p) is not int or not 1 <= p <= record.get("pages", 0)
                           for p in ref["pages"])):
                errors.append("Invalid source reference")
    if errors:
        raise ValueError("; ".join(errors))
    return {**integrity, "candidate_validation": "complete",
            "findings": len(ids), "formal_review": "not-established",
            "overall_assurance": "review-required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(examine(args.archive), indent=2))


if __name__ == "__main__":
    main()
