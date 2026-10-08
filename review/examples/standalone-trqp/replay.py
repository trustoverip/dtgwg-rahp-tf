#!/usr/bin/env python3
"""Replay bounded schema/source checks; this does not assess a live TRQP service."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from jsonschema import FormatChecker, validators

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from source_integrity import verify_source


def authorization_examples(path: Path) -> tuple[dict, dict]:
    # The first two HTTP blocks are the authorization query and response.
    blocks = re.findall(r"```http\n(.*?)```", path.read_text(), re.S)
    if len(blocks) < 2:
        raise ValueError(f"Missing authorization HTTP examples: {path.name}")
    try:
        query, response = (json.loads(block[block.index("{"):].strip()) for block in blocks[:2])
        if not isinstance(query, dict) or not isinstance(response, dict):
            raise ValueError("Authorization examples must be objects")
        return query, response
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Malformed authorization examples: {path.name}") from exc


def replay(root: Path = HERE) -> dict:
    manifest = verify_source(root)
    required = {'source/spec.md.txt', 'source/api.md.txt', 'source/https_binding.md.txt',
                'source/trqp_authorization_response.schema.json', 'source/LICENSE.md.txt',
                'source/COPYRIGHT_POLICY.md.txt'}
    if not required.issubset({entry['path'] for entry in manifest['files']}):
        raise ValueError('Manifest omits a required replay source')
    schema = json.loads((root / "source/trqp_authorization_response.schema.json").read_text())
    validator_type = validators.validator_for(schema)
    validator_type.check_schema(schema)
    validator = validator_type(schema, format_checker=FormatChecker())
    cases = json.loads((root / "cases.json").read_text())
    if not isinstance(cases, list) or not cases:
        raise ValueError("Response cases must be a nonempty list")
    outcomes = []
    seen = set()
    for case in cases:
        if (not isinstance(case, dict) or not isinstance(case.get("id"), str)
                or not case["id"] or case["id"] in seen
                or type(case.get("schema_valid")) is not bool
                or not isinstance(case.get("response"), dict)):
            raise ValueError("Malformed or duplicate response case")
        seen.add(case["id"])
        errors = list(validator.iter_errors(case["response"]))
        actual = not errors
        if actual != case["schema_valid"]:
            raise ValueError(f"Unexpected schema result: {case['id']}")
        outcomes.append({"id": case["id"], "schema_valid": actual})
    api_query, api_response = authorization_examples(root / "source/api.md.txt")
    https_query, https_response = authorization_examples(root / "source/https_binding.md.txt")
    return {
        "target_commit": manifest["commit"],
        "scope": "retained source and constructed response fixtures only",
        "source_integrity": "verified",
        "cases": outcomes,
        "api_example": {
            "query_time": api_query["context"]["time"],
            "response_time_requested": api_response["time_requested"],
            "requested_time_matches": api_query["context"]["time"] == api_response["time_requested"],
            "schema_valid": validator.is_valid(api_response),
        },
        "https_example": {
            "requested_time_matches": https_query["context"]["time"] == https_response["time_requested"],
            "schema_valid": validator.is_valid(https_response),
        },
        "runtime_authorization": "not-assessed",
        "authority_history": "not-assessed",
        "overall_assurance": "review-required",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with the retained expected replay")
    args = parser.parse_args()
    result = replay()
    if args.check:
        expected = json.loads((HERE / "expected-replay.json").read_text())
        if result != expected:
            raise ValueError("Replay differs from retained expected result")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
