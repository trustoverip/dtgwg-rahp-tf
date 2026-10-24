#!/usr/bin/env python3
"""Replay one explicitly selected RAHP review and record deterministic validation evidence.

This tool checks repeatability of machine validation, NOT scientific agreement of
independent analysts or authenticity of the target at its claimed Git revision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(review: pathlib.Path, risks: pathlib.Path, repeat: int = 2,
        source: pathlib.Path | None = None) -> dict:
    if repeat < 2 or repeat > 20:
        raise ValueError("repeat must be between 2 and 20")
    fixed = {
        "review": review, "risks": risks,
        "schema": ROOT / "review/spec-review.schema.json",
        "vocabulary": ROOT / "method/vocabularies.yaml",
        "validator": ROOT / "review/validate_spec_review.py",
    }
    if source is not None:
        fixed["supplied_source"] = source
    for name, path in fixed.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required input {name} missing: {path}")
    hashes = {name: digest(path) for name, path in fixed.items()}
    cmd = [sys.executable, str(fixed["validator"]), str(review), "--risks", str(risks)]
    observations = []
    for _ in range(repeat):
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                check=False, timeout=120)
        observations.append({"exit_code": result.returncode,
                             "stdout": result.stdout, "stderr": result.stderr})
        for name, path in fixed.items():
            if digest(path) != hashes[name]:
                raise RuntimeError(f"Input changed during replay: {name}")
    same = all(item == observations[0] for item in observations[1:])
    valid = observations[0]["exit_code"] == 0
    return {
        "schema": "rahp-review-replay-check/v1",
        "repeat": repeat,
        "inputs_sha256": hashes,
        "validation_accepted": valid,
        "machine_results_identical": same,
        "observed_result": observations[0],
        "interpretation": "Machine validation repeatability only; no source authenticity or target assurance",
        "status": "repeatable" if same else "unstable",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=pathlib.Path)
    parser.add_argument("--risks", required=True, type=pathlib.Path)
    parser.add_argument("--source", type=pathlib.Path,
                        help="Optional local source file to digest; not verified against Git revision")
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    report = run(args.review.resolve(), args.risks.resolve(), args.repeat,
                 args.source.resolve() if args.source else None)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if report["machine_results_identical"] and report["validation_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
