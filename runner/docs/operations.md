# Operating RAHP scheduled evaluations

Status: optional **experimental** upstream tooling. First read [runner/README](../README.md).
The two commands are different contracts:
- `python3 -m runner`: v1alpha1, offline retained TRQP *examination* with example-local evidence checking.
- `python3 -m runner.service`: v1alpha2, multi-target *documentary review validation*, Git revision acquisition, source artifact digest, comparison and reports. It does **not** execute arbitrary target-specific evaluators, derive harms, certify conformance or establish risk acceptance.

## Run the v1alpha2 example

```sh
python3 -m pip install -r requirements.txt
python3 -m runner.service validate --config runner/examples/dtg-service.yaml
python3 -m runner.service run-all --config runner/examples/dtg-service.yaml --output ./evaluation-runs
```

The example is based on the independent [DTG Portfolio Monitor curated inventory](https://github.com/sankarshanmukhopadhyay/dtg-portfolio-monitor/blob/1a1982212bce36d79a5fb9dc6d58bec7b7d9e01a/config/repositories.yaml) at immutable commit `1a1982212bce36d79a5fb9dc6d58bec7b7d9e01a` (Apache-2.0). It includes a **small adapted subset**, with its own SHA-256 binding, of the source project's curated registry. The monitor itself is not invoked, and neither its materiality classifications nor downstream cross-spec test definitions grant upstream RAHP authority.

Two distinct VRC historical review records, maintained upstream under `review/examples/vrc-v03/`, are configured with the same `series: vrc-review`. Each pins a different immutable commit of `trustoverip/dtgwg-cred-tf`. The source `dtg.md` is acquired from public GitHub over HTTPS, checked against the reviewed commit, and hashed. The installed upstream review schema/validator checks reviewer-authored findings, their risk references and statuses. A historical comparison can show `F-001` moving from `open` to `resolved` **as asserted in the two authored review records**. It does not independently prove that the specification modification eliminated the harm. The VRC example's separately retained evidence and evaluator remain the stronger target-specific examination path.

A successful service run emits per-target `evaluation.json` and `evaluation.md`, with `execution: completed`, `validation: review-record-valid`, `assurance: review-required`. A target failure produces a retained failure report, `assurance: not-assessed` and an aggregate nonzero exit while remaining targets are attempted.

## Configuration and source scope

The `rahp-evaluation-runner/v1alpha2` configuration accepts `targets` and optionally a versioned, pinned `dtg-portfolio-monitor-curated-v1` `inventory`. Each target declares:
- `id`: unique stable local name;
- `series`: optional comparison cohort; reusing this value is appropriate only for the *same evaluation question and target* across revisions;
- `repository`: public GitHub owner/repository, required to match the reviewer-authored record and any portfolio allowlist;
- `revision`: exact 40-character Git commit, or `ref`: a branch discovery hint. For a reviewed target, the resolved commit **must equal** the review's source revision. Both may be present to detect branch drift;
- `assessment: upstream-review-validation`: the sole portable documentary evaluator supported in v1alpha2;
- `review`, `risks`: paths to trusted review and selected risk corpus. `repo://path` resolves within this installed upstream checkout; plain relative paths resolve beneath the config directory. Traversal and symlink escapes are rejected;
- `artifact`: relative repository source artifact path, with optional `artifact_sha256` to confirm expected bytes.

A portfolio inventory is **advisory scope metadata**, not assessment selection or acceptance authority. Its local snapshot digest must match the configured `sha256`. Unknown config keys, duplicate IDs, unsupported evaluator types, unsafe paths and unapproved target names are rejected.

## Containerized evaluation

```sh
docker build -f runner/Dockerfile -t rahp-evaluation-runner:local .
docker run --rm --read-only --cap-drop=ALL --security-opt=no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev --mount type=volume,src=rahp-evidence,dst=/evaluations \
  rahp-evaluation-runner:local run-all \
  --config runner/examples/dtg-service.yaml --output /evaluations
```

The image supplies Python, Git and pinned source files from the checked-out RAHP release. It performs one bounded invocation and exits. The image requires network access to public GitHub in v1alpha2. Never expose credentials in a world-readable deployment manifest. When using a private Git source, use a separately reviewed credential/transport design; v1alpha2 is *public HTTPS GitHub only* and does not support arbitrary repository hosts or target-controlled execution.

## External scheduler

On a VM, a systemd timer or cron should run the same command with an explicit working directory and persistent output path. See [systemd example](../deployments/systemd/rahp-evaluation.service) and [timer](../../deployments/systemd/rahp-evaluation.timer). For Kubernetes, prefer a CronJob with `concurrencyPolicy: Forbid`, read-only application filesystem, immutable image digest, restricted service account and a persistent evidence volume. Kubernetes-specific YAML is intentionally not declared production-tested here.

## Failure and evidence handling

- No successful evaluation is inferred from scheduling, Git fetch, review schema validity alone, or absence of a changed finding.
- A failed source acquisition, stale revision, malformed review, missing artifact, artifact digest mismatch or validator rejection is recorded as failed/not-assessed.
- Reports are per-run files; do not automatically publish raw reports or private repositories. The output directory is operational evidence and needs access control, backup and a retention/disposition policy.
- Comparison is permitted only where repository, assessment type, risk corpus digest, method-validator digest and review schema match. A changed finding status is **a difference in reviewer assertions**, not independent remediation proof. An absent finding is `absent`, not automatically resolved.
- No built-in alert delivery, web API, indefinite background process, automatic GitHub issue mutation, risk acceptance or runtime enforcement is provided.
- The container is supplied as a reproducible build recipe, not a released, independently security-audited artifact.
- Remote Git operations require a Git installation and public GitHub network access; tests use isolated local source fixtures and do not establish that external transport will always be available.
