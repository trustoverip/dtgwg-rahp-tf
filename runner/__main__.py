"""Bounded, optional orchestration of *installed upstream* RAHP evaluations.

This is an evaluation runner, not a target-scanning or assurance decision engine.
Only a built-in retained-source evaluator is supported in this first increment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXECUTOR = ROOT / "review" / "examine.py"
EXAMPLE = ROOT / "review" / "examples" / "standalone-trqp"
CONTRACT = "rahp-evaluation-runner/v1alpha1"
EVALUATOR = "upstream-retained-trqp"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
TARGET_ID = re.compile(r"^[a-z][a-z0-9-]{0,62}$")
SUPPORTED_TARGET = "trustoverip/tswg-trust-registry-protocol"
BOUNDARY = (
    "Machine reproduction of the installed, retained-source TRQP examination only; "
    "not independent source authenticity, live-system evaluation, target assurance, "
    "risk acceptance, Task Force approval or independent human review."
)


class ConfigurationError(ValueError):
    pass


def reject_unknown(value, allowed, where):
    if not isinstance(value, dict):
        raise ConfigurationError(f"{where} must be a mapping")
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        raise ConfigurationError(f"{where}: unsupported fields: {', '.join(unknown)}")


def read_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    document = yaml.safe_load(raw)
    reject_unknown(document, {"schema", "targets", "inventory"}, "config")
    if document.get("schema") != CONTRACT:
        raise ConfigurationError(f"config.schema must equal {CONTRACT}")
    targets = document.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ConfigurationError("targets must be a nonempty list")
    seen = set()
    for index, target in enumerate(targets):
        label = f"targets[{index}]"
        reject_unknown(target, {"id", "repository", "evaluator", "source_revision"}, label)
        ident = target.get("id")
        if not isinstance(ident, str) or not TARGET_ID.fullmatch(ident):
            raise ConfigurationError(f"{label}.id is invalid")
        if ident in seen:
            raise ConfigurationError(f"duplicate target id: {ident}")
        seen.add(ident)
        if target.get("repository") != SUPPORTED_TARGET:
            raise ConfigurationError(f"{label}: target is not supported by the installed evaluator")
        if target.get("evaluator") != EVALUATOR:
            raise ConfigurationError(f"{label}: unsupported evaluator (no arbitrary commands)")
        revision = target.get("source_revision")
        if not isinstance(revision, str) or not FULL_SHA.fullmatch(revision):
            raise ConfigurationError(f"{label}.source_revision must be a full immutable Git SHA")
    inventory = document.get("inventory")
    if inventory is not None:
        reject_unknown(inventory, {"origin", "revision", "sha256", "role", "meaning"}, "inventory")
        if not isinstance(inventory.get("origin"), str) or not inventory["origin"].startswith("https://"):
            raise ConfigurationError("inventory.origin must be an HTTPS source")
        if not isinstance(inventory.get("revision"), str) or not FULL_SHA.fullmatch(inventory["revision"]):
            raise ConfigurationError("inventory.revision must be a full Git SHA")
        if not isinstance(inventory.get("sha256"), str) or not SHA256.fullmatch(inventory["sha256"]):
            raise ConfigurationError("inventory.sha256 must be a SHA-256 digest")
        if inventory.get("meaning") != "advisory":
            raise ConfigurationError("inventory.meaning must be advisory, never RAHP authority")
        if inventory.get("role") != "reference-example":
            raise ConfigurationError("inventory.role must be reference-example")
    return document, hashlib.sha256(raw).hexdigest()


def installed_revision() -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, timeout=10, check=False)
    rev = result.stdout.strip()
    return rev if result.returncode == 0 and FULL_SHA.fullmatch(rev) else None


def source_revision() -> str:
    manifest = json.loads((EXAMPLE / "source-manifest.json").read_text(encoding="utf-8"))
    # The retained example has its own source-manifest verification in examine.py.
    # The review record is the canonical assertion of the source commit.
    review = yaml.safe_load((EXAMPLE / "review.yaml").read_text(encoding="utf-8"))
    revision = review["target"]["revision"]
    if not isinstance(revision, str) or not FULL_SHA.fullmatch(revision):
        raise ConfigurationError("installed review contains no immutable target revision")
    if not isinstance(manifest, dict):
        raise ConfigurationError("installed retained-source manifest is invalid")
    return revision


def markdown_report(report: dict) -> str:
    outcome = report["execution"]
    observed = report.get("observed_result") or {}
    return "\n".join([
        "# RAHP evaluation execution report", "",
        f"- Run: `{report['run_id']}`",
        f"- Target: `{report['target']['repository']}`",
        f"- Source revision: `{report['target']['source_revision']}`",
        f"- Evaluator: `{report['target']['evaluator']}`",
        f"- Evaluated at (UTC): {report['observed_at']}",
        f"- Execution: **{outcome['state']}** (exit code {outcome['exit_code']})",
        f"- Machine validation: **{outcome['validation']}**",
        f"- Substantive assurance: **{outcome['assurance']}**", "",
        "## Observation", "",
        f"- Installed examiner result: `{observed.get('validation', 'unavailable')}`",
        f"- Findings recorded by examiner: {observed.get('findings', 'unavailable')}", "",
        "## Claim boundary", "", report["claim_boundary"], "",
        "## Provenance", "",
        f"- Configuration SHA-256: `{report['config_sha256']}`",
        f"- Runner Git revision: `{report['runner_revision'] or 'unavailable'}`",
        "- Target source is retained by the installed upstream example; the runner "
        "does not acquire or authenticate remote Git content.", "",
        "## Diagnostics", "", "See the JSON report for the bounded execution error, if any.", ""
    ])


def run(config_path: Path, output: Path, target_id: str, timeout: int = 120) -> tuple[Path, dict]:
    config, config_hash = read_config(config_path)
    target = next((item for item in config["targets"] if item["id"] == target_id), None)
    if target is None:
        raise ConfigurationError(f"target not declared: {target_id}")
    if source_revision() != target["source_revision"]:
        raise ConfigurationError("configured source revision differs from the installed retained review")
    if not 1 <= timeout <= 600:
        raise ConfigurationError("timeout must be 1..600 seconds")

    # No executor strings, shell commands or supplied code can enter this invocation.
    try:
        process = subprocess.run([sys.executable, str(EXECUTOR)], cwd=ROOT,
                                 text=True, capture_output=True, timeout=timeout,
                                 check=False)
        result = json.loads(process.stdout) if process.returncode == 0 else None
        accepted = (isinstance(result, dict) and result.get("validation") == "complete"
                    and result.get("overall_assurance") == "review-required"
                    and result.get("assessment_id") and isinstance(result.get("findings"), int))
        successful = process.returncode == 0 and bool(accepted)
        exit_code = process.returncode
        error = None if successful else "Installed evaluator failed or returned an unsupported/incomplete result"
    except (subprocess.TimeoutExpired, ValueError) as exc:
        exit_code, result, successful = -1, None, False
        error = f"Evaluation did not complete: {type(exc).__name__}"

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8]
    report = {
        "schema": CONTRACT,
        "run_id": run_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "config_sha256": config_hash,
        "runner_revision": installed_revision(),
        "execution": {
            "state": "completed" if successful else "failed",
            "exit_code": exit_code,
            "validation": "complete" if successful else "indeterminate",
            "assurance": "review-required" if successful else "not-assessed",
            "error": error,
        },
        "observed_result": result if successful else None,
        "claim_boundary": BOUNDARY,
    }
    output.mkdir(parents=True, exist_ok=True)
    destination = output / run_id
    destination.mkdir(mode=0o700)
    # A complete pair of files is retained for successes and failures.
    for name, payload in (("evaluation.json", json.dumps(report, sort_keys=True, indent=2) + "\n"),
                          ("evaluation.md", markdown_report(report))):
        filename = destination / name
        with filename.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    return destination, report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("validate", "run"):
        cmd = sub.add_parser(action)
        cmd.add_argument("--config", type=Path, required=True)
        if action == "run":
            cmd.add_argument("--target", required=True)
            cmd.add_argument("--output", type=Path, default=Path("evaluation-runs"))
            cmd.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    try:
        if args.action == "validate":
            config, digest = read_config(args.config)
            print(json.dumps({"config": "valid", "targets": len(config["targets"]),
                              "sha256": digest}, sort_keys=True))
        else:
            destination, report = run(args.config, args.output, args.target, args.timeout)
            print(json.dumps({"report": str(destination), "execution": report["execution"]},
                             sort_keys=True))
            return 0 if report["execution"]["state"] == "completed" else 1
        return 0
    except (ConfigurationError, OSError, yaml.YAMLError, ValueError, KeyError,
            subprocess.SubprocessError) as exc:
        print(f"RAHP evaluation runner: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
