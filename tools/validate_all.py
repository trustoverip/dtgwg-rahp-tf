#!/usr/bin/env python3
"""Compose corpus and explicitly selected specification-review validation.

This entry point checks repository integrity, not target assurance. No review is
implicitly selected. The review vocabulary is owned by its existing JSON Schema;
the enumerations below describe compatibility invariants and fail if they drift.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
REVIEW_SCHEMA = ROOT / "review" / "spec-review.schema.json"
METHOD_VOCAB = ROOT / "method" / "vocabularies.yaml"

# Review vocabulary is intentionally distinct from corpus method vocabulary.
# This is a compatibility lock, not an alternative source of runtime values.
REVIEW_ENUMS = {
    "control_plane": (
        "specification", "companion-specification", "governance",
        "implementation-guidance", "runtime-control", "operational-policy", "none",
    ),
    "status": (
        "open", "in_progress", "resolved", "risk_accepted",
        "out_of_scope", "superseded",
    ),
    "resolution.type": (
        "specification-change", "companion-specification-change",
        "governance-action", "implementation-guidance", "runtime-control",
        "operational-policy", "risk-acceptance", "already-addressed",
        "no-action", "superseded",
    ),
}
CORPUS_VOCABS = (
    "severity", "likelihood", "standards_priority", "standards_status",
    "normative_language", "control_type", "persona_type",
    "risk_acceptance_decision", "governance_precedent_status",
)


def check_vocabulary(schema_path: pathlib.Path = REVIEW_SCHEMA,
                     method_path: pathlib.Path = METHOD_VOCAB) -> list[str]:
    errors: list[str] = []
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    vocab = yaml.safe_load(method_path.read_text(encoding="utf-8"))
    for name in CORPUS_VOCABS:
        item = vocab.get(name) if isinstance(vocab, dict) else None
        if not isinstance(item, dict) or not isinstance(item.get("values"), list) or not item["values"]:
            errors.append(f"method vocabulary {name} is missing or empty")
            continue
        values = [v.get("value") if isinstance(v, dict) else v for v in item["values"]]
        if len({json.dumps(v, sort_keys=True) for v in values}) != len(values):
            errors.append(f"method vocabulary {name} contains duplicate values")
    item = schema["properties"]["findings"]["items"]["properties"]
    actual = {
        "control_plane": item["control_plane"]["enum"],
        "status": item["status"]["enum"],
        "resolution.type": item["resolution"]["properties"]["type"]["enum"],
    }
    for name, expected in REVIEW_ENUMS.items():
        if set(actual[name]) != set(expected) or len(actual[name]) != len(expected):
            errors.append(f"review vocabulary drift: {name}; review contract change requires explicit review")
    return errors


def validate(data: pathlib.Path, reviews: list[pathlib.Path],
             risks: pathlib.Path | None = None, strict: bool = False) -> int:
    failures = check_vocabulary()
    for error in failures:
        print(f"ERROR: {error}", file=sys.stderr)
    if failures:
        return 1

    cmd = [sys.executable, str(ROOT / "tools" / "validate.py"), "--data", str(data)]
    if strict:
        cmd.append("--strict")
    print("CHECK: corpus integrity", flush=True)
    corpus = subprocess.run(cmd, check=False, cwd=ROOT)
    failed = corpus.returncode != 0

    for record in reviews:
        print(f"CHECK: review {record}", flush=True)
        cmd = [sys.executable, str(ROOT / "review" / "validate_spec_review.py"),
               str(record), "--risks", str(risks or (data / "risks.yaml"))]
        result = subprocess.run(cmd, check=False, cwd=ROOT)
        failed |= result.returncode != 0

    if not reviews:
        print("NOTE: no review selected; only corpus and vocabulary checks executed")
    print("FAIL: composed validation" if failed else "PASS: composed validation")
    return int(failed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=pathlib.Path, default=ROOT / "data")
    parser.add_argument("--review", type=pathlib.Path, action="append", default=[],
                        help="review YAML to validate; repeat for multiple records")
    parser.add_argument("--risks", type=pathlib.Path,
                        help="explicit risk corpus for review references (default: --data/risks.yaml)")
    parser.add_argument("--strict", action="store_true",
                        help="treat corpus warnings as failure (same as tools/validate.py)")
    args = parser.parse_args()
    return validate(args.data, args.review, args.risks, args.strict)


if __name__ == "__main__":
    sys.exit(main())
