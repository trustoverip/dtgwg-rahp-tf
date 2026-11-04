#!/usr/bin/env python3
"""Advisory documentary checks; no acceptance authority is authenticated."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = {"accepted", "accepted_with_conditions"}
ACCOUNTABLE = ACCEPTANCE | {"rejected", "deferred"}
DECISIONS = ACCOUNTABLE | {"pending"}
COMMON = ("authority", "authority_reference", "decided_by", "decision_date", "rationale")
ACCEPTANCE_REQUIRED = ("review_date", "evidence", "residual_risk",
                       "affected_people", "alternatives_considered")


def permitted_residual_severities() -> set[str]:
    """Read the governed method vocabulary rather than copying severity literals."""
    vocab = yaml.safe_load((ROOT / "method/vocabularies.yaml").read_text(encoding="utf-8"))
    values = vocab["severity"]["values"]
    allowed = {entry["value"] for entry in values
               if isinstance(entry, dict) and entry.get("absolute") is not True}
    if not allowed or not all(isinstance(value, str) for value in allowed):
        raise ValueError("invalid method severity vocabulary")
    return allowed


def _present(value: object) -> bool:
    return value is not None and value != "" and value != [] and (
        not isinstance(value, str) or bool(value.strip()))


def _date(value: object, field: str, failures: list[str]) -> date | None:
    if not _present(value):
        return None
    try:
        # Avoid accepting loose timestamps or interpreting a datetime as a date.
        if not isinstance(value, (str, date)):
            raise ValueError("not an ISO date")
        if isinstance(value, date) and not isinstance(value, str):
            return value
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        failures.append(f"invalid {field}")
        return None


def inspect(record: dict, severity: str,
            allowed_residual: set[str] | None = None) -> list[str]:
    failures: list[str] = []
    if not isinstance(record.get("risk_id"), str) or not record["risk_id"].strip():
        failures.append("missing risk_id")
    decision = record.get("decision")
    if decision not in DECISIONS:
        failures.append("unknown decision")
        return failures
    if decision == "pending":
        return failures  # A pending record makes no decision or authority claim.

    for field in COMMON:
        if not _present(record.get(field)):
            failures.append(f"missing {field}")
    participants = record.get("decided_by")
    if not isinstance(participants, list) or not participants or not all(
            isinstance(item, str) and item.strip() for item in participants):
        failures.append("decided_by must be a nonempty list of named participants")

    decision_date = _date(record.get("decision_date"), "decision_date", failures)
    if decision == "deferred":
        if not _present(record.get("deferral_reason")):
            failures.append("missing deferral_reason")
        if not _present(record.get("review_trigger")) and not _present(record.get("review_date")):
            failures.append("deferral needs review_trigger or review_date")
        review_date = _date(record.get("review_date"), "review_date", failures)
        if decision_date and review_date and review_date <= decision_date:
            failures.append("review_date must follow decision_date")
        return failures

    if decision == "rejected":
        return failures

    # Acceptance is only documentary-ready, never authorized by this helper.
    if severity == "Critical":
        failures.append("Critical risk may not be accepted")
    for field in ACCEPTANCE_REQUIRED:
        if not _present(record.get(field)):
            failures.append(f"missing {field}")
    review_date = _date(record.get("review_date"), "review_date", failures)
    if decision_date and review_date and review_date <= decision_date:
        failures.append("review_date must follow decision_date")
    if allowed_residual is None:
        allowed_residual = permitted_residual_severities()
    if record.get("residual_risk") not in allowed_residual:
        failures.append("residual_risk must be a non-Critical method severity")
    for field in ("affected_people", "alternatives_considered"):
        value = record.get(field)
        if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item.strip() for item in value):
            failures.append(f"{field} must be a nonempty list")
    conflicts = record.get("conflicts_of_interest")
    if not isinstance(conflicts, list) or not all(
            isinstance(item, str) and item.strip() for item in conflicts):
        failures.append("conflicts_of_interest must be an explicit list")
    if decision == "accepted_with_conditions" and not _present(record.get("conditions")):
        failures.append("conditional acceptance lacks conditions")
    return failures


def evaluate(record: object, corpus: object) -> dict:
    errors: list[str] = []
    decision = record.get("decision") if isinstance(record, dict) else None
    if not isinstance(record, dict):
        errors.append("record must be a mapping")
    entries = corpus.get("records") if isinstance(corpus, dict) else None
    if not isinstance(entries, list):
        errors.append("invalid risk corpus")
    if isinstance(record, dict) and isinstance(entries, list):
        matches = [entry for entry in entries if isinstance(entry, dict)
                   and entry.get("id") == record.get("risk_id")]
        if len(matches) != 1 or not isinstance(matches[0].get("severity"), str):
            errors.append("risk_id does not resolve uniquely to a severity in selected corpus")
        else:
            severity = matches[0]["severity"]
            try:
                allowed = permitted_residual_severities()
                if severity not in allowed | {"Critical"}:
                    errors.append("risk severity is not in governed vocabulary")
                else:
                    errors.extend(inspect(record, severity, allowed))
            except (KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
                errors.append(f"invalid method severity vocabulary: {exc}")
    return {
        "documentary_valid": not errors,
        "documentary_ready": not errors and decision in ACCEPTANCE,
        "decision": decision,
        "errors": errors,
        "authority_authenticated": False,
        "target_assurance": False,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("record", type=Path)
    ap.add_argument("--risks", required=True, type=Path,
                    help="Selected risk corpus (caller must establish provenance)")
    args = ap.parse_args(argv)
    try:
        record = yaml.safe_load(args.record.read_text(encoding="utf-8"))
        corpus = yaml.safe_load(args.risks.read_text(encoding="utf-8"))
        result = evaluate(record, corpus)
    except (OSError, yaml.YAMLError) as exc:
        result = {"documentary_valid": False, "documentary_ready": False,
                  "errors": [f"unreadable or invalid input: {exc}"],
                  "authority_authenticated": False, "target_assurance": False}
    result["severity_source"] = str(args.risks)
    print(json.dumps(result, indent=2))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
