"""Multi-target RAHP evaluation service: source pinning, review validation and history.

Optional orchestration only. A valid documentary review is never target assurance.
Remote Git transport is read-only and restricted to public HTTPS GitHub projects.
"""
from __future__ import annotations

import argparse
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import uuid

import yaml

from runner.__main__ import ROOT, ConfigurationError, reject_unknown, installed_revision

SCHEMA = "rahp-evaluation-runner/v1alpha2"
SHA = re.compile(r"^[0-9a-f]{40}$")
IDENT = re.compile(r"^[a-z][a-z0-9-]{0,62}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BOUNDARY = ("Repository revision and review-record integrity can be checked; "
            "documentary validation does not establish source-authorship authenticity, "
            "evidence truth, completeness of harms, target assurance or authorized risk acceptance.")


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_bytes())
    if not isinstance(data, dict):
        raise ConfigurationError(f"{path}: expected YAML mapping")
    return data


def relative_file(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ConfigurationError("file path must be a nonempty relative POSIX path")
    if name.startswith("repo://"):
        root = ROOT
        name = name[len("repo://"):]
    value = PurePosixPath(name)
    if value.is_absolute() or any(part in (".", "..") for part in value.parts):
        raise ConfigurationError(f"unsafe relative path: {name}")
    resolved = (root / name).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ConfigurationError(f"path escapes configuration directory: {name}")
    if not resolved.is_file():
        raise ConfigurationError(f"required file missing: {name}")
    return resolved


def read_inventory(config_dir: Path, inventory: dict) -> tuple[set[str], dict]:
    reject_unknown(inventory, {"path", "sha256", "kind"}, "inventory")
    if inventory.get("kind") != "dtg-portfolio-monitor-curated-v1":
        raise ConfigurationError("unsupported portfolio inventory format")
    path = relative_file(config_dir, inventory.get("path"))
    if inventory.get("sha256") != hash_file(path):
        raise ConfigurationError("portfolio inventory digest mismatch")
    doc = read_yaml(path)
    if set(doc) != {"version", "repositories"} or doc["version"] != 1:
        raise ConfigurationError("unsupported portfolio registry schema")
    records = doc["repositories"]
    if not isinstance(records, list):
        raise ConfigurationError("portfolio repositories must be a list")
    indexed = {}
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get("repo"), str):
            raise ConfigurationError("invalid portfolio repository entry")
        if item["repo"] in indexed:
            raise ConfigurationError("duplicate portfolio repository")
        indexed[item["repo"]] = item
    return set(indexed), indexed


def validate(config_path: Path) -> tuple[dict, dict]:
    config_path = config_path.resolve()
    config = read_yaml(config_path)
    reject_unknown(config, {"schema", "inventory", "targets"}, "service")
    if config.get("schema") != SCHEMA:
        raise ConfigurationError(f"service.schema must equal {SCHEMA}")
    targets = config.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ConfigurationError("targets must be a nonempty list")
    registry = None
    if "inventory" in config:
        registry, _ = read_inventory(config_path.parent, config["inventory"])
    seen = set()
    for target in targets:
        reject_unknown(target, {"id", "repository", "ref", "revision", "review", "risks",
                                "artifact", "artifact_sha256", "assessment", "series"}, "target")
        identifier = target.get("id")
        if not isinstance(identifier, str) or not IDENT.fullmatch(identifier) or identifier in seen:
            raise ConfigurationError("invalid or duplicate target ID")
        seen.add(identifier)
        series = target.get("series", identifier)
        if not isinstance(series, str) or not IDENT.fullmatch(series):
            raise ConfigurationError(f"{identifier}: invalid comparison series")
        repo = target.get("repository")
        if not isinstance(repo, str) or not REPO.fullmatch(repo):
            raise ConfigurationError(f"{identifier}: invalid owner/repository")
        if registry is not None and repo not in registry:
            raise ConfigurationError(f"{identifier}: not admitted by pinned portfolio registry")
        if target.get("assessment") != "upstream-review-validation":
            raise ConfigurationError(f"{identifier}: only documentary review validation is supported")
        ref = target.get("ref")
        sha = target.get("revision")
        if ref is not None and (not isinstance(ref, str) or
                                not re.fullmatch(r"[A-Za-z0-9._/-]{1,128}", ref) or
                                ".." in ref or ref.startswith("-") or ref.endswith("/")):
            raise ConfigurationError(f"{identifier}: unsupported ref syntax")
        if sha is not None and (not isinstance(sha, str) or not SHA.fullmatch(sha)):
            raise ConfigurationError(f"{identifier}: invalid immutable revision")
        if ref is None and sha is None:
            raise ConfigurationError(f"{identifier}: specify ref or revision")
        for key in ("review", "risks"):
            relative_file(config_path.parent, target.get(key))
        artifact = target.get("artifact")
        if not isinstance(artifact, str) or not artifact or artifact.startswith("/") or "\\" in artifact:
            raise ConfigurationError(f"{identifier}: artifact must be a relative source path")
        parts = PurePosixPath(artifact).parts
        if ".." in parts or "." in parts or artifact.startswith("-"):
            raise ConfigurationError(f"{identifier}: artifact path is unsafe")
        digest = target.get("artifact_sha256")
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ConfigurationError(f"{identifier}: invalid artifact digest")
        review = read_yaml(relative_file(config_path.parent, target["review"]))
        if review.get("schema") != "rahp-spec-review/v1":
            raise ConfigurationError(f"{identifier}: unsupported review schema")
        review_target = review.get("target") or {}
        if review_target.get("repository") != repo:
            raise ConfigurationError(f"{identifier}: review repository mismatch")
        if not isinstance(review_target.get("revision"), str) or not SHA.fullmatch(review_target["revision"]):
            raise ConfigurationError(f"{identifier}: review must assert immutable SHA")
        if sha is not None and sha != review_target["revision"]:
            raise ConfigurationError(f"{identifier}: configured revision disagrees with review")
    return config, {"configuration_sha256": hash_file(config_path),
                    "targets": [t["id"] for t in targets]}


def git(*args: str, timeout: int = 90, cwd: Path | None = None) -> str:
    # No shell, hooks, file protocol, credential prompting, or externally configured transport.
    environment = dict(os.environ)
    environment.update({"GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                        "GIT_ALLOW_PROTOCOL": "https", "GIT_OPTIONAL_LOCKS": "0"})
    result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args],
                            cwd=cwd, env=environment, capture_output=True, text=True,
                            timeout=timeout, check=False)
    if result.returncode:
        raise ConfigurationError(f"Git source acquisition failed (exit {result.returncode})")
    return result.stdout.strip()


def acquire(target: dict, destination: Path) -> tuple[str, Path]:
    owner_repo = target["repository"]
    url = f"https://github.com/{owner_repo}.git"
    # Remote branch/ref is only a discovery hint. Review requires exact SHA agreement.
    branch = target.get("ref")
    if branch:
        if branch.startswith("refs/") or branch.endswith(".lock"):
            raise ConfigurationError("unsupported ref")
        observed = git("ls-remote", "--exit-code", "--heads", url, branch)
        entries = [line.split() for line in observed.splitlines() if len(line.split()) == 2]
        expected = next((sha for sha, remote_ref in entries
                         if remote_ref == "refs/heads/" + branch), None)
        if expected is None or not SHA.fullmatch(expected):
            raise ConfigurationError("no unique immutable revision for ref")
    else:
        expected = target["revision"]
    if target.get("revision") and target["revision"] != expected:
        raise ConfigurationError("remote ref changed from configured revision")
    git("init", "--quiet", str(destination))
    git("-C", str(destination), "remote", "add", "origin", url)
    git("-C", str(destination), "fetch", "--depth", "1", "origin", expected)
    actual = git("-C", str(destination), "rev-parse", "FETCH_HEAD^{commit}")
    if actual != expected:
        raise ConfigurationError("fetched revision differs from expected SHA")
    git("-C", str(destination), "checkout", "--detach", "--quiet", actual)
    return actual, destination


def report_comparison(prior: dict | None, current: dict) -> dict:
    if prior is None:
        return {"state": "no-baseline", "changes": []}
    a = prior.get("comparison_key")
    b = current.get("comparison_key")
    if not a or a != b or prior.get("execution", {}).get("state") != "completed":
        return {"state": "not-comparable", "changes": []}
    older = prior.get("findings") or {}
    newer = current.get("findings") or {}
    changes = [{"finding": key, "before": older.get(key, "absent"),
                "after": newer.get(key, "absent")}
               for key in sorted(set(older) | set(newer)) if older.get(key) != newer.get(key)]
    # An absent finding is not automatically a resolved finding.
    return {"state": "comparable", "changes": changes}


def comparable_baseline(output: Path, target_id: str, current: dict) -> dict | None:
    candidates = []
    if not output.exists():
        return None
    for directory in output.iterdir():
        if not directory.is_dir():
            continue
        location = directory / "evaluation.json"
        if not location.is_file():
            continue
        try:
            candidate = json.loads(location.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if candidate.get("series") == target_id and candidate.get("schema") == SCHEMA:
            candidates.append(candidate)
    candidates.sort(key=lambda item: item.get("observed_at", ""), reverse=True)
    for candidate in candidates:
        if candidate.get("execution", {}).get("state") == "completed":
            if candidate.get("comparison_key") == current["comparison_key"]:
                return candidate
    # Never compare across incompatible method/profile/corpus baselines.
    return candidates[0] if candidates else None


def render(report: dict) -> str:
    lines = ["# RAHP evaluation report", "",
             f"- Target: `{report['target_id']}`",
             f"- Repository: `{report['repository']}`",
             f"- Source revision: `{report.get('source_revision') or 'unavailable'}`",
             f"- Execution: **{report['execution']['state']}**",
             f"- Review validation: **{report['execution']['validation']}**",
             f"- Target assurance: **{report['execution']['assurance']}**",
             f"- Historical comparison: {report['comparison']['state']}", "",
             "## Findings (reviewer-authored, not independently verified)", ""]
    lines += [f"- `{key}`: {value}" for key, value in sorted(report["findings"].items())] or ["No validated findings available."]
    lines += ["", "## Changed review-record states", ""]
    lines += [f"- `{change['finding']}`: {change['before']} → {change['after']}"
              for change in report["comparison"]["changes"]] or ["No comparable changes established."]
    lines += ["", "## Evidence and limitations", "", BOUNDARY, "",
              f"- Config SHA-256: `{report['configuration_sha256']}`",
              f"- Review SHA-256: `{report['review_sha256']}`",
              f"- Risk source SHA-256: `{report['risks_sha256']}`",
              f"- Source artifact SHA-256: `{report.get('artifact_sha256') or 'unavailable'}`",
              f"- Evaluation method SHA-256: `{report['method_sha256']}`",
              f"- Run timestamp (UTC): {report['observed_at']}", ""]
    return "\n".join(lines)


def evaluate_target(config_path: Path, target: dict, output: Path,
                    acquire_source=acquire) -> tuple[dict, Path]:
    config_path = config_path.resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
    report = {
        "schema": SCHEMA, "run_id": run_id, "observed_at": datetime.now(timezone.utc).isoformat(),
        "target_id": target["id"], "series": target.get("series", target["id"]),
        "repository": target["repository"],
        "source_revision": None, "artifact_sha256": None, "configuration_sha256": hash_file(config_path),
        "review_sha256": hash_file(relative_file(config_path.parent, target["review"])),
        "risks_sha256": hash_file(relative_file(config_path.parent, target["risks"])),
        "method_sha256": hash_file(ROOT / "review/validate_spec_review.py"),
        "runner_revision": installed_revision(), "findings": {},
        "execution": {"state": "failed", "validation": "indeterminate",
                      "assurance": "not-assessed", "reason": "not executed"},
        "claim_boundary": BOUNDARY,
    }
    # Comparison key does not include target revision; changes to source are precisely
    # what comparable reviews of the same profile should be able to describe.
    profile = {"repository": target["repository"], "assessment": target["assessment"],
               "risk_sha256": report["risks_sha256"], "method_sha256": report["method_sha256"],
               "review_schema": "rahp-spec-review/v1"}
    report["comparison_key"] = hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="rahp-evaluation-") as temporary:
        try:
            source = Path(temporary) / "checkout"
            revision, source = acquire_source(target, source)
            report["source_revision"] = revision
            review_path = relative_file(config_path.parent, target["review"])
            risks_path = relative_file(config_path.parent, target["risks"])
            review = read_yaml(review_path)
            if review["target"]["revision"] != revision:
                raise ConfigurationError("fetched revision disagrees with reviewer-authored review")
            artifact = relative_file(source, target["artifact"])
            report["artifact_sha256"] = hash_file(artifact)
            if target.get("artifact_sha256") and report["artifact_sha256"] != target["artifact_sha256"]:
                raise ConfigurationError("fetched artifact digest differs from configured source")
            cmd = [sys.executable, str(ROOT / "review/validate_spec_review.py"),
                   str(review_path), "--risks", str(risks_path)]
            process = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                     timeout=120, check=False)
            if process.returncode:
                raise ConfigurationError("upstream review-record validator rejected review")
            report["findings"] = {f["id"]: f["status"] for f in review["findings"]}
            report["execution"] = {"state": "completed", "validation": "review-record-valid",
                                   "assurance": "review-required", "reason": None}
        except (OSError, ConfigurationError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
            report["execution"]["reason"] = f"Evaluation incomplete ({type(exc).__name__})"
    report["comparison"] = report_comparison(comparable_baseline(output, report["series"], report), report)
    output.mkdir(parents=True, exist_ok=True)
    folder = output / (target["id"] + "-" + run_id)
    folder.mkdir(mode=0o700)
    (folder / "evaluation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (folder / "evaluation.md").write_text(render(report) + "\n")
    return report, folder


def run_service(config_path: Path, output: Path, selected: str | None = None,
                acquire_source=acquire) -> tuple[list[dict], int]:
    config, _ = validate(config_path)
    targets = [t for t in config["targets"] if selected is None or t["id"] == selected]
    if not targets:
        raise ConfigurationError("requested target is not declared")
    output.mkdir(parents=True, exist_ok=True)
    results = []
    # One host/volume-level exclusive lock prevents racing comparison baselines.
    # A second invocation fails visibly rather than writing misleading history.
    with (output / ".rahp-evaluation.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ConfigurationError("another evaluation owns the output lock") from exc
        try:
            for target in targets:
                report, _ = evaluate_target(config_path, target, output, acquire_source)
                results.append(report)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    return results, 0 if all(r["execution"]["state"] == "completed" for r in results) else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="RAHP source-pinned documentary evaluation")
    parser.add_argument("action", choices=("validate", "run", "run-all"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--target")
    parser.add_argument("--output", type=Path, default=Path("evaluation-runs"))
    args = parser.parse_args(argv)
    try:
        if args.action == "validate":
            _, metadata = validate(args.config)
            print(json.dumps({"status": "valid", **metadata}, sort_keys=True))
            return 0
        if args.action == "run" and not args.target:
            raise ConfigurationError("run requires --target")
        if args.action == "run-all" and args.target:
            raise ConfigurationError("run-all does not take --target")
        results, status = run_service(args.config, args.output, args.target)
        print(json.dumps([{"id": r["target_id"], "execution": r["execution"],
                           "run_id": r["run_id"], "comparison": r["comparison"]}
                          for r in results], indent=2))
        return status
    except (ConfigurationError, OSError, yaml.YAMLError, ValueError) as exc:
        print(f"RAHP evaluation service: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
