"""Check SEDI coverage inventory and referenced documentary records."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATUSES = {"indexed", "examined", "scenario-examined"}
DISPOSITIONS = {"addressed-in-design", "partially-addressed", "decision-dependent",
                "evidence-required", "clarification-required", "gap-identified",
                "indeterminate", "out-of-scope"}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def check(register, index, manifest, loader=load, require_complete=False):
    if register["archive_sha256"] != manifest["sha256"]:
        raise ValueError("Coverage archive identity mismatch")
    indexed = {r["id"]: r["pdf_page"] for r in index["records"]}
    records = register["records"]
    if len(indexed) != 142 or len(index["records"]) != 142:
        raise ValueError("Unexpected index universe")
    if len(records) != len(indexed) or len({r["id"] for r in records}) != len(indexed):
        raise ValueError("Missing or duplicate coverage record")
    if {r["id"] for r in records} != set(indexed):
        raise ValueError("Coverage universe differs from index")
    packages = {p["id"]: set(p["domains"]) for p in register["work_packages"]}
    docs = {}
    counts = {s: 0 for s in sorted(STATUSES)}
    for r in records:
        if r["index_page"] != indexed[r["id"]] or r["status"] not in STATUSES:
            raise ValueError("Invalid index binding or status")
        if r["review_state"] != "not-reviewed":
            raise ValueError("Unsupported accountable review claim")
        counts[r["status"]] += 1
        if r["status"] == "indexed":
            if r["examination"] is not None or r["disposition"] is not None:
                raise ValueError("Unexamined requirement has assessment claim")
            if r["id"].split("-")[1] not in packages.get(r["work_package"], set()):
                raise ValueError("Missing or invalid work package")
            continue
        ref = r["examination"]
        if not isinstance(ref, dict) or ref["id"] != r["id"] or r["disposition"] not in DISPOSITIONS:
            raise ValueError("Invalid examination reference or disposition")
        name = ref["record"]
        if Path(name).name != name or not name.endswith(".json"):
            raise ValueError("Unsafe examination record path")
        if name not in docs:
            docs[name] = loader(name)
        matches = [x for x in docs[name]["requirements"] if x["id"] == r["id"]]
        if len(matches) != 1 or not ref["objectives"] or ref["objectives"] != matches[0]["objectives"]:
            raise ValueError("Missing examination or objective mismatch")
        if r["status"] == "scenario-examined" and not r.get("case_refs"):
            raise ValueError("Scenario status lacks case references")
    if require_complete:
        # Lazy import: normalization invokes the inventory check with require_complete=False.
        from normalize_coverage import normalize, require_complete as require_documentary_complete
        require_documentary_complete(normalize(register, index, manifest, loader))
    return {"indexed_universe": len(indexed), "counts": counts,
            "documentary_coverage_complete": counts["indexed"] == 0,
            "overall_assurance": "review-required"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    register, index, manifest = (load(n) for n in ("requirement-coverage.json", "requirement-index.json", "archive-manifest.json"))
    print(json.dumps(check(register, index, manifest, require_complete=args.require_complete), indent=2))


if __name__ == "__main__":
    main()
