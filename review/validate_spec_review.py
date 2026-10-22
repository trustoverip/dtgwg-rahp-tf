#!/usr/bin/env python3
"""Validate a RAHP specification pressure-test review record.

This validator is intentionally narrow. It validates the review record contract,
requires an immutable Git revision, rejects duplicate finding identifiers,
verifies that referenced RAHP risk identifiers exist in the current instance,
checks that the schema's review enums match method/vocabularies.yaml, and applies
the rules from the review vocabulary definitions that the schema cannot express
(see check_finding_semantics).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "review" / "spec-review.schema.json"
RISKS_PATH = ROOT / "data" / "risks.yaml"
VOCAB_PATH = ROOT / "method" / "vocabularies.yaml"
ACCEPTANCES_PATH = ROOT / "data" / "risk-acceptances.yaml"

# Statuses that are not terminal: treatment is still owed by some control plane.
NON_TERMINAL_STATUSES = {"open", "in_progress"}
# Risk-acceptance decisions that actually accept the risk (see risk_acceptance_decision).
ACCEPTING_DECISIONS = {"accepted", "accepted_with_conditions"}

# Schema location of each review enum -> its vocabulary in method/vocabularies.yaml.
REVIEW_VOCABULARIES = {
    ("properties", "findings", "items", "properties", "control_plane"): "control_plane",
    ("properties", "findings", "items", "properties", "status"): "finding_status",
    ("properties", "findings", "items", "properties", "resolution", "properties", "type"): "resolution_type",
}


def load_yaml(path: pathlib.Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_records(path: pathlib.Path) -> dict[str, dict]:
    """Records of a corpus file, keyed by id (accepts a list or a mapping of records)."""
    doc = load_yaml(path) or {}
    records = doc.get("records") or []
    if isinstance(records, dict):
        return {str(key): value or {} for key, value in records.items()}
    return {str(record.get("id")): record for record in records if record.get("id")}


def known_risk_ids(path: pathlib.Path = RISKS_PATH) -> set[str]:
    return set(load_records(path))


def check_finding_semantics(finding: dict, risks: dict[str, dict],
                            acceptances: dict[str, dict]) -> list[str]:
    """Rules from the review vocabulary definitions (#26) that the schema does not express."""
    errors = []
    finding_id = finding.get("id") or "?"
    status = finding.get("status")
    resolution = finding.get("resolution") if isinstance(finding.get("resolution"), dict) else {}

    # control_plane none means no layer owns treatment, so it cannot leave a finding unassigned.
    # It is not required for out_of_scope: an applicable risk treated outside this review
    # should still name the plane where its treatment belongs.
    if finding.get("control_plane") == "none" and status in NON_TERMINAL_STATUSES:
        errors.append(f"finding {finding_id}: control_plane none is only allowed on a closed finding,"
                      f" not status {status}")

    if status == "superseded" and resolution.get("type") != "superseded":
        errors.append(f"finding {finding_id}: status superseded needs resolution type superseded")

    if status == "risk_accepted":
        for risk_id in finding.get("risks") or []:
            if str((risks.get(risk_id) or {}).get("severity")) == "Critical":
                errors.append(f"finding {finding_id}: risk {risk_id} is Critical and may not be risk-accepted")
        reference = resolution.get("reference")
        if reference:
            acceptance = acceptances.get(reference)
            if acceptance is None:
                errors.append(f"finding {finding_id}: risk acceptance {reference} does not resolve"
                              " in data/risk-acceptances.yaml")
            else:
                if acceptance.get("decision") not in ACCEPTING_DECISIONS:
                    errors.append(f"finding {finding_id}: risk acceptance {reference} has decision"
                                  f" {acceptance.get('decision')}, not accepted or accepted_with_conditions")
                if acceptance.get("risk_id") not in (finding.get("risks") or []):
                    errors.append(f"finding {finding_id}: risk acceptance {reference} is for"
                                  f" {acceptance.get('risk_id')}, which the finding does not cite")
    return errors


def vocabulary_values(entry) -> list:
    values = (entry or {}).get("values") or []
    return [v.get("value") if isinstance(v, dict) else v for v in values]


def check_vocabulary(schema: dict, vocab_path: pathlib.Path = VOCAB_PATH) -> list[str]:
    """The review enums are owned by method/vocabularies.yaml; the schema must match."""
    vocab = load_yaml(vocab_path) or {}
    errors = []
    for path, name in REVIEW_VOCABULARIES.items():
        node = schema
        for key in path:
            node = node.get(key, {}) if isinstance(node, dict) else {}
        enum = node.get("enum") if isinstance(node, dict) else None
        expected = vocabulary_values(vocab.get(name))
        if not expected:
            errors.append(f"vocabulary {name}: missing from method/vocabularies.yaml")
            continue
        if enum is None:
            errors.append(f"vocabulary {name}: no enum at schema {'.'.join(path)}")
            continue
        missing = sorted(set(expected) - set(enum))
        extra = sorted(set(enum) - set(expected))
        if missing or extra or len(enum) != len(set(enum)):
            errors.append(f"vocabulary {name}: schema enum does not match method/vocabularies.yaml"
                          f" (missing from schema: {missing}, not in vocabulary: {extra})")
    return errors


def validate_record(record: dict, risks_path: pathlib.Path = RISKS_PATH,
                    vocab_path: pathlib.Path = VOCAB_PATH,
                    acceptances_path: pathlib.Path = ACCEPTANCES_PATH) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = check_vocabulary(schema, vocab_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors += [
        f"schema {'.'.join(str(p) for p in err.absolute_path) or '(record)'}: {err.message}"
        for err in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    ]

    findings = record.get("findings") if isinstance(record, dict) else None
    if isinstance(findings, list):
        seen: set[str] = set()
        risks = load_records(risks_path)
        acceptances = load_records(acceptances_path)
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            finding_id = finding.get("id")
            if finding_id:
                if finding_id in seen:
                    errors.append(f"finding {finding_id}: duplicate finding identifier")
                seen.add(finding_id)
            for risk_id in finding.get("risks") or []:
                if risk_id not in risks:
                    errors.append(f"finding {finding_id or '?'}: risk {risk_id} does not resolve in data/risks.yaml")
            errors += check_finding_semantics(finding, risks, acceptances)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=pathlib.Path)
    parser.add_argument("--risks", type=pathlib.Path, default=RISKS_PATH)
    parser.add_argument("--acceptances", type=pathlib.Path, default=ACCEPTANCES_PATH)
    args = parser.parse_args()

    record = load_yaml(args.record)
    errors = validate_record(record, args.risks, acceptances_path=args.acceptances)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} problem(s)")
        return 1

    print(f"PASS: {args.record}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
