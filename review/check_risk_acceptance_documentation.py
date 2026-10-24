#!/usr/bin/env python3
"""Advisory documentary gate for proposed risk acceptance; no authority is granted.

Does not replace canonical corpus validation or authenticate signatories.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml

REQUIRED = ("authority", "authority_reference", "decided_by",
            "decision_date", "review_date", "evidence", "rationale",
            "residual_risk")


def inspect(record: dict, severity: str) -> list[str]:
    failures = []
    decision = record.get("decision")
    if decision not in ("pending", "accepted", "accepted_with_conditions", "rejected", "deferred"):
        failures.append("unknown decision")
    if decision not in ("accepted", "accepted_with_conditions"):
        return failures  # Pending/rejection do not prove authority or acceptance.
    if severity.lower() == "critical":
        failures.append("Critical risk may not be accepted")
    for name in REQUIRED:
        value = record.get(name)
        if not value or (isinstance(value, str) and not value.strip()):
            failures.append(f"missing {name}")
    if not isinstance(record.get("decided_by"), list) or not all(
        isinstance(s, str) and s.strip() for s in record.get("decided_by", [])):
        failures.append("decided_by must be a nonempty list of named participants")
    for name in ("decision_date", "review_date"):
        value = record.get(name)
        if value:
            import datetime
            try:
                datetime.date.fromisoformat(str(value))
            except ValueError:
                failures.append(f"invalid {name}")
    if record.get("decision_date") and record.get("review_date"):
        try:
            from datetime import date
            if date.fromisoformat(str(record["review_date"])) <= date.fromisoformat(str(record["decision_date"])):
                failures.append("review_date must follow decision_date")
        except ValueError:
            pass
    if decision == "accepted_with_conditions" and not record.get("conditions"):
        failures.append("conditional acceptance lacks conditions")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("record", type=Path)
    ap.add_argument("--severity", required=True,
                    help="Severity read from the relevant canonical risk, not trusted from decision record")
    args = ap.parse_args()
    record = yaml.safe_load(args.record.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        print(json.dumps({"documentary_ready": False, "errors": ["record must be a mapping"]}))
        return 1
    errors = inspect(record, args.severity)
    print(json.dumps({"documentary_ready": not errors and record.get("decision") in
                      ("accepted", "accepted_with_conditions"),
                      "decision": record.get("decision"),
                      "errors": errors,
                      "authority_authenticated": False,
                      "target_assurance": False}, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
