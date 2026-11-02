#!/usr/bin/env python3
"""Validate the bounded TEA source/replay/review/evidence package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator
import yaml

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parents[1]
sys.path.insert(0, str(REVIEW))
sys.path.insert(0, str(HERE))

from source_integrity import retained_file, verify_source
from validate_spec_review import validate_record
from replay import replay

EXAMPLE = HERE


def pointer_value(document, pointer: str):
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError("Observation pointer must start with /")
    value = document
    for token in pointer[1:].split("/"):
        if re.search(r"~(?![01])", token):
            raise ValueError("Malformed observation pointer escape")
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            if not token.isdigit() or (len(token) > 1 and token.startswith("0")):
                raise ValueError("Malformed observation array index")
            value = value[int(token)]
        elif isinstance(value, dict):
            value = value[token]
        else:
            raise ValueError("Observation pointer traverses a scalar")
    return value


def validate_examination(root: Path, record: dict, sidecar: dict,
                         observations: dict, risks_path: Path) -> list[str]:
    schema = json.loads((EXAMPLE / "evidence.schema.json").read_text(encoding="utf-8"))
    errors = [
        f"evidence schema: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(sidecar)
    ]
    if errors:
        return errors

    errors.extend(validate_record(record, risks_path))
    if errors:
        return errors

    manifest = verify_source(root)
    if record["target"]["repository"] != manifest["repository"] or record["target"]["revision"] != manifest["commit"]:
        errors.append("Review target disagrees with retained-source manifest")
    if sidecar["target"] != {key: record["target"][key] for key in ("repository", "revision")}:
        errors.append("Evidence target disagrees with review")
    if sidecar["assessment_id"] != record["assessment_id"]:
        errors.append("Evidence assessment identity disagrees with review")
    if record["rahp_version"] != "trustoverip/dtgwg-rahp-tf@" + sidecar["method_revision"]:
        errors.append("Method identity disagrees with review")

    for key in ("review_binding", "risks_binding"):
        binding = sidecar[key]
        path = retained_file(root, binding["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]:
            errors.append(f"{key}: digest mismatch")
        if key == "review_binding" and yaml.safe_load(path.read_text(encoding="utf-8")) != record:
            errors.append("Review binding does not identify supplied record")
        if key == "risks_binding" and path.resolve() != risks_path.resolve():
            errors.append("Risk binding does not identify selected corpus")

    if sidecar["execution"]["state"] != "complete" or sidecar["execution"]["observations"] != observations:
        errors.append("Execution incomplete or observations disagree with fresh replay")

    manifest_sources = {entry["path"] for entry in manifest["files"]}
    evidence = {}
    for entry in sidecar["evidence"]:
        identifier = entry["id"]
        if identifier in evidence:
            errors.append(f"Duplicate evidence identifier: {identifier}")
        evidence[identifier] = entry

        if entry["kind"] == "result":
            try:
                actual = pointer_value(observations, entry["pointer"])
                if json.dumps(actual, sort_keys=True) != json.dumps(entry["expected"], sort_keys=True):
                    errors.append(f"{identifier}: result contradicts observation")
            except (KeyError, IndexError, ValueError, TypeError):
                errors.append(f"{identifier}: observation reference does not resolve")
        else:
            path = retained_file(root, entry["path"])
            if entry["kind"] == "source" and entry["path"] not in manifest_sources:
                errors.append(f"{identifier}: source is not retained in manifest")
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                errors.append(f"{identifier}: evidence digest mismatch")

    findings = {finding["id"]: finding for finding in record["findings"]}
    seen = set()
    for finding in sidecar["findings"]:
        identifier = finding["id"]
        if identifier in seen:
            errors.append(f"Duplicate evidence finding: {identifier}")
        seen.add(identifier)
        if identifier not in findings:
            errors.append(f"Unknown evidence finding: {identifier}")
            continue
        if set(finding["risk_reasoning"]) != set(findings[identifier]["risks"]):
            errors.append(f"{identifier}: risk reasoning does not cover selected risks")
        for reference in finding["evidence"]:
            if reference not in evidence:
                errors.append(f"{identifier}: missing evidence {reference}")

    if seen != set(findings):
        errors.append("Evidence must cover every review finding exactly once")
    return errors


def examine(root: Path = EXAMPLE) -> dict:
    observations = replay(root)
    expected = json.loads(retained_file(root, "expected-replay.json").read_text(encoding="utf-8"))
    if observations != expected:
        raise ValueError("Fresh replay differs from retained expected results")

    record = yaml.safe_load(retained_file(root, "review.yaml").read_text(encoding="utf-8"))
    sidecar = json.loads(retained_file(root, "evidence.json").read_text(encoding="utf-8"))
    risks = retained_file(root, "risks.yaml")
    errors = validate_examination(root, record, sidecar, observations, risks)
    if errors:
        raise ValueError("\n".join(errors))

    return {
        "assessment_id": record["assessment_id"],
        "validation": "complete",
        "scope": observations["scope"],
        "overall_assurance": observations["overall_assurance"],
        "unassessed": observations["unassessed"],
        "findings": len(record["findings"]),
        "open_findings": sum(finding["status"] == "open" for finding in record["findings"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", type=Path, default=EXAMPLE,
                        help="retained TEA bundle directory; code is always loaded from this repository")
    args = parser.parse_args()
    try:
        result = examine(args.example)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: examination incomplete: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
