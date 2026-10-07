#!/usr/bin/env python3
"""Validate a RAHP specification pressure-test review record.

This validator is intentionally narrow. It validates the review record contract,
requires an immutable Git revision, rejects duplicate finding identifiers, and
verifies that referenced RAHP risk identifiers exist in the current instance.
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


def load_yaml(path: pathlib.Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def known_risk_ids(path: pathlib.Path = RISKS_PATH) -> set[str]:
    doc = load_yaml(path) or {}
    records = doc.get("records") or []
    if isinstance(records, dict):
        return set(records)
    return {str(record.get("id")) for record in records if record.get("id")}


def validate_record(record: dict, risks_path: pathlib.Path = RISKS_PATH) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"schema {'.'.join(str(p) for p in err.absolute_path) or '(record)'}: {err.message}"
        for err in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    ]

    findings = record.get("findings") if isinstance(record, dict) else None
    if isinstance(findings, list):
        seen: set[str] = set()
        known = known_risk_ids(risks_path)
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            finding_id = finding.get("id")
            if finding_id:
                if finding_id in seen:
                    errors.append(f"finding {finding_id}: duplicate finding identifier")
                seen.add(finding_id)
            for risk_id in finding.get("risks") or []:
                if risk_id not in known:
                    errors.append(f"finding {finding_id or '?'}: risk {risk_id} does not resolve in data/risks.yaml")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=pathlib.Path)
    parser.add_argument("--risks", type=pathlib.Path, default=RISKS_PATH)
    args = parser.parse_args()

    record = load_yaml(args.record)
    errors = validate_record(record, args.risks)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} problem(s)")
        return 1

    print(f"PASS: {args.record}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
