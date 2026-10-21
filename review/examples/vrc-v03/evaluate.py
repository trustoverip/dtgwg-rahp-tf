#!/usr/bin/env python3
"""Reproduce the bounded VRC v0.3 baseline and reassessment examination."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "review"))

from source_integrity import retained_file, verify_source
from validate_spec_review import validate_record

BASELINE = "baseline"
REASSESSED = "reassessed"
RISK_CORPUS = ROOT / "data" / "risks.yaml"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source(name: str, root: Path) -> tuple[dict, Path, str]:
    bundle = root / name
    manifest = verify_source(bundle)
    path = retained_file(bundle, "source/dtg.md.txt")
    return manifest, path, path.read_text(encoding="utf-8")


def observations(root: Path = HERE) -> dict:
    _, _, baseline = _source(BASELINE, root)
    _, _, reassessed = _source(REASSESSED, root)
    shared_requirement = (
        "#### Zero-Knowledge Proof Requirements" in baseline
        and "2. Possession of the underlying VMC (proving membership in the community)" in baseline
        and "3. The VRC issuer possesses a VMC from the *same* C-DID" in baseline
    )
    residual = (
        "**M-DID reuse:** Allowed for bootstrapping" in baseline
        and "Migration from M-DID-based to R-DID-based edges recommended post-bootstrapping" in baseline
    )
    residual_after = (
        "**M-DID reuse:** Allowed for bootstrapping" in reassessed
        and "Migration from M-DID-based to R-DID-based edges recommended post-bootstrapping" in reassessed
    )
    return {
        BASELINE: {
            "general_vrc_zkp_requires_shared_community_evidence": shared_requirement,
            "pairwise_zkp_section": "#### Pairwise Zero-Knowledge Proof" in baseline,
            "explicit_no_shared_membership_precondition": "Community membership is **not** a precondition" in baseline,
            "mdid_bootstrapping_residual": residual,
        },
        REASSESSED: {
            "general_vrc_zkp_requires_shared_community_evidence":
                "#### Zero-Knowledge Proof Requirements" in reassessed
                and "Possession of the underlying VMC (proving membership in the community)" in reassessed,
            "pairwise_zkp_section": "#### Pairwise Zero-Knowledge Proof" in reassessed,
            "community_anchored_zkp_section": "#### Community-Anchored Zero-Knowledge Proof" in reassessed,
            "explicit_no_shared_membership_precondition": "Community membership is **not** a precondition" in reassessed,
            "mdid_bootstrapping_residual": residual_after,
        },
    }


def _validate_sidecar(name: str, fresh: dict, root: Path) -> tuple[dict, dict]:
    review_path = root / f"{name}-review.yaml"
    evidence_path = root / f"{name}-evidence.json"
    record = yaml.safe_load(review_path.read_text(encoding="utf-8"))
    sidecar = json.loads(evidence_path.read_text(encoding="utf-8"))
    schema = json.loads((root / "evidence.schema.json").read_text(encoding="utf-8"))
    errors = [f"evidence schema: {e.message}" for e in Draft202012Validator(schema).iter_errors(sidecar)]
    errors += validate_record(record, RISK_CORPUS)

    manifest_path = root / sidecar["source_manifest"]
    bundle = manifest_path.parent
    manifest = verify_source(bundle, manifest_path.name)
    if record["target"]["repository"] != manifest["repository"] or record["target"]["revision"] != manifest["commit"]:
        errors.append(f"{name}: review target does not match retained manifest")
    if sidecar["target"] != {k: record["target"][k] for k in ("repository", "revision")}:
        errors.append(f"{name}: evidence target does not match review")
    if sidecar["assessment_id"] != record["assessment_id"]:
        errors.append(f"{name}: assessment identity does not match review")
    if record["rahp_version"] != "trustoverip/dtgwg-rahp-tf@" + sidecar["method_revision"]:
        errors.append(f"{name}: method revision does not match review")
    if sidecar["review_binding"]["path"] != review_path.name or sidecar["review_binding"]["sha256"] != digest(review_path):
        errors.append(f"{name}: review binding mismatch")
    risk_path = ROOT / sidecar["risks_binding"]["path"]
    if risk_path.resolve() != RISK_CORPUS.resolve() or sidecar["risks_binding"]["sha256"] != digest(risk_path):
        errors.append(f"{name}: risk corpus binding mismatch")
    if sidecar["execution"]["state"] != "complete" or sidecar["execution"]["observations"] != fresh:
        errors.append(f"{name}: retained observations disagree with fresh source examination")

    source_entry = manifest["files"][0]
    expected_source = str(Path(sidecar["source_manifest"]).parent / source_entry["path"])
    evidence_by_id = {}
    for evidence in sidecar["evidence"]:
        if evidence["id"] in evidence_by_id:
            errors.append(f"{name}: duplicate evidence identifier {evidence['id']}")
        evidence_by_id[evidence["id"]] = evidence
        if evidence["source"] != expected_source:
            errors.append(f"{name}: evidence {evidence['id']} does not identify retained source")
            continue
        text = retained_file(root, evidence["source"]).read_text(encoding="utf-8")
        if evidence["section"] not in text:
            errors.append(f"{name}: evidence {evidence['id']} section does not resolve")
        for needle in evidence["contains"]:
            if needle not in text:
                errors.append(f"{name}: evidence {evidence['id']} proposition does not resolve")

    findings = {f["id"]: f for f in record["findings"]}
    seen = set()
    for finding in sidecar["findings"]:
        fid = finding["id"]
        if fid in seen:
            errors.append(f"{name}: duplicate evidence finding {fid}")
        seen.add(fid)
        if fid not in findings:
            errors.append(f"{name}: unknown evidence finding {fid}")
            continue
        if set(finding["risk_reasoning"]) != set(findings[fid]["risks"]):
            errors.append(f"{name}: {fid} risk reasoning does not cover selected risks")
        for eid in finding["evidence"]:
            if eid not in evidence_by_id:
                errors.append(f"{name}: {fid} references missing evidence {eid}")
    if seen != set(findings):
        errors.append(f"{name}: evidence must cover every review finding exactly once")
    if errors:
        raise ValueError("\n".join(errors))
    return record, sidecar


def evaluate(root: Path = HERE) -> dict:
    fresh = observations(root)
    baseline_review, _ = _validate_sidecar(BASELINE, fresh[BASELINE], root)
    reassessed_review, _ = _validate_sidecar(REASSESSED, fresh[REASSESSED], root)

    if baseline_review["target"]["revision"] == reassessed_review["target"]["revision"]:
        raise ValueError("Reassessment must use a different immutable source revision")
    baseline_findings = {f["id"]: f for f in baseline_review["findings"]}
    reassessed_findings = {f["id"]: f for f in reassessed_review["findings"]}
    if baseline_findings["F-001"]["status"] != "open" or reassessed_findings["F-001"]["status"] != "resolved":
        raise ValueError("F-001 reassessment transition is not preserved")
    if baseline_findings["F-002"]["status"] != "open" or reassessed_findings["F-002"]["status"] != "open":
        raise ValueError("F-002 residual finding must remain open")

    return {
        "validation": "complete",
        "overall_assurance": "review-required",
        "baseline_assessment": baseline_review["assessment_id"],
        "reassessed_assessment": reassessed_review["assessment_id"],
        "observations": fresh,
        "finding_transitions": {"F-001": "open->resolved", "F-002": "open->open"},
    }


def main() -> int:
    try:
        print(json.dumps(evaluate(), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: VRC examination incomplete: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
