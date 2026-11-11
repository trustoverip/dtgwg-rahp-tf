#!/usr/bin/env python3
"""Replay bounded TEA capability observations; this is not a TEA conformance engine."""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from source_integrity import verify_source


def is_subresource(candidate: str, parent: str) -> bool:
    if parent == "/":
        return candidate.startswith("/")
    parent = parent.rstrip("/")
    candidate = candidate.rstrip("/")
    return candidate == parent or candidate.startswith(parent + "/")


def meet_resource(left: str, right: str) -> str | None:
    if is_subresource(left, right):
        return left.rstrip("/") or "/"
    if is_subresource(right, left):
        return right.rstrip("/") or "/"
    return None


def meet_amount(left, right):
    if left is None:
        return right
    if right is None:
        return left
    return min(left, right)


def source_propositions(root: Path) -> dict:
    clauses = (root / "source/clauses.md.txt").read_text(encoding="utf-8")
    required = {
        "capability_triple": "capability = ( resource, ability, limitation )",
        "authorization_from_capability_only": "computed only from the capability, and composes by meet down a delegation chain",
        "strict_attenuation": "MUST be strictly attenuating",
        "obligations_post_gate": "They do not enter the authorization decision and are settled after the act",
        "exercise_rechecked": "For each Exercise the service MUST confirm",
        "nonperformance_not_retroactive": "Non-performance never invalidates authority already exercised",
    }
    result = {name: phrase in clauses for name, phrase in required.items()}
    missing = [name for name, present in result.items() if not present]
    if missing:
        raise ValueError("Retained TEA source no longer contains required proposition(s): " + ", ".join(missing))
    return result


def evaluate_case(case: dict) -> dict:
    chain = case.get("chain")
    if not isinstance(chain, list):
        raise ValueError("case chain must be a list")

    if not chain:
        return {
            "id": case["id"],
            "restriction_conformant": True,
            "authorized": False,
            "reason": "no-capability",
            "effective": None,
            "post_gate_breach": False,
        }

    root = chain[0]
    resource = root["resource"]
    abilities = set(root["abilities"])
    max_amount = (root.get("limitations") or {}).get("max_amount")
    obligations = set(root.get("obligations") or [])
    restriction_conformant = True

    for restriction in chain[1:]:
        next_resource = restriction.get("resource", resource)
        next_abilities = set(restriction.get("abilities", abilities))
        next_max = (restriction.get("limitations") or {}).get("max_amount")

        if not is_subresource(next_resource, resource):
            restriction_conformant = False
        if not next_abilities.issubset(abilities):
            restriction_conformant = False
        if max_amount is not None and next_max is not None and next_max > max_amount:
            restriction_conformant = False

        resource = meet_resource(resource, next_resource)
        abilities &= next_abilities
        max_amount = meet_amount(max_amount, next_max)
        obligations.update(restriction.get("obligations") or [])

    effective = {
        "resource": resource,
        "abilities": sorted(abilities),
        "max_amount": max_amount,
    }

    exercise = case["exercise"]
    if not case.get("authenticated", False):
        authorized, reason = False, "unauthenticated"
    elif not restriction_conformant:
        authorized, reason = False, "invalid-redelegation"
    elif resource is None or not abilities:
        authorized, reason = False, "empty-capability"
    elif not is_subresource(exercise["resource"], resource):
        authorized, reason = False, "exceeds-capability"
    elif exercise["ability"] not in abilities:
        authorized, reason = False, "exceeds-capability"
    elif max_amount is not None and exercise.get("amount", 0) > max_amount:
        authorized, reason = False, "exceeds-capability"
    else:
        authorized, reason = True, "within-capability"

    state = case.get("obligation_state") or {}
    post_gate_breach = authorized and any(state.get(name) == "unmet" for name in obligations)

    return {
        "id": case["id"],
        "restriction_conformant": restriction_conformant,
        "authorized": authorized,
        "reason": reason,
        "effective": effective,
        "post_gate_breach": post_gate_breach,
    }


def replay(root: Path = HERE) -> dict:
    manifest = verify_source(root)
    propositions = source_propositions(root)
    cases = json.loads((root / "cases.json").read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases.json must contain a nonempty list")

    seen = set()
    outcomes = []
    for case in cases:
        identifier = case.get("id") if isinstance(case, dict) else None
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Malformed or duplicate case identifier")
        seen.add(identifier)
        outcome = evaluate_case(case)
        if outcome != case.get("expected"):
            expected = dict(case.get("expected") or {})
            expected["id"] = identifier
            if outcome != expected:
                raise ValueError(f"Unexpected case result: {identifier}")
        outcomes.append(outcome)

    return {
        "target_commit": manifest["commit"],
        "scope": "retained TEA v0.2 Draft source and constructed capability fixtures only",
        "source_integrity": "verified",
        "source_propositions": propositions,
        "cases": outcomes,
        "unassessed": {
            "tsp_transport": "not-assessed",
            "vid_resolution": "not-assessed",
            "revocation": "not-assessed",
            "live_service": "not-assessed",
            "full_tea_conformance": "not-assessed",
        },
        "overall_assurance": "review-required",
    }


def main() -> int:
    result = replay()
    expected = json.loads((HERE / "expected-replay.json").read_text(encoding="utf-8"))
    if result != expected:
        raise ValueError("Replay differs from retained expected result")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
