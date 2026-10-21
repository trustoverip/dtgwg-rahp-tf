#!/usr/bin/env python3
"""Compose corpus and explicitly selected specification-review validation.

This entry point checks repository integrity, not target assurance. No review is
implicitly selected. Governed method vocabularies are checked here; review/schema parity is
checked by review/validate_spec_review.py.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
METHOD_VOCAB = ROOT / "method" / "vocabularies.yaml"

def check_vocabulary(method_path: pathlib.Path = METHOD_VOCAB) -> list[str]:
    """Check every declared vocabulary; schema parity is checked by the review validator."""
    try:
        vocab = yaml.safe_load(method_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"vocabulary unavailable: {exc}"]
    if not isinstance(vocab, dict):
        return ["vocabularies must be a mapping"]
    errors: list[str] = []
    for name, entry in vocab.items():
        if name == "risk_score":
            continue  # A formula, not an enumeration.
        if not isinstance(entry, dict) or not isinstance(entry.get("values"), list) or not entry["values"]:
            errors.append(f"method vocabulary {name} is missing or empty")
            continue
        seen = set()
        for i, raw in enumerate(entry["values"]):
            value = raw.get("value") if isinstance(raw, dict) else raw
            if isinstance(raw, dict):
                if "value" not in raw:
                    errors.append(f"method vocabulary {name} entry {i} missing value")
                if name in ("control_plane", "finding_status", "resolution_type") and not (
                    isinstance(raw.get("definition"), str) and raw["definition"].strip()
                ):
                    errors.append(f"method vocabulary {name} entry {i} missing definition")
            key = json.dumps(value, sort_keys=True)
            if key in seen:
                errors.append(f"method vocabulary {name} contains duplicate values")
            seen.add(key)
    for name in ("control_plane", "finding_status", "resolution_type"):
        if name not in vocab:
            errors.append(f"method vocabulary {name} missing")
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
