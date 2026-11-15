# RAHP Evaluation Runner (bounded experimental increment)

This is an **optional** source-pinned evaluation execution entry point for the
installed upstream RAHP retained-source TRQP examination. It does not inspect live
services, watch GitHub events, collect telemetry, automatically assess arbitrary
specifications, enforce controls, accept risks or confer assurance certification.
It is separate from the monitoring layer of the independent DTG Portfolio Monitor.

## Two independently bounded execution contracts

- **Offline retained-source examiner (v1alpha1):** `python3 -m runner`, exactly the installed TRQP examination with its retained evidence and example-local reasoning.
- **Multi-target documentary evaluation (v1alpha2):** `python3 -m runner.service`, configured public GitHub source acquisition, immutable revision verification, upstream `rahp-spec-review/v1` record validation, per-run provenance and conservative cross-run status comparison. This second mode does **not** automatically examine source semantics or execute the downstream RAHP controller.

Start with the [self-contained operations guide](docs/operations.md) for a real two-revision VRC example, a DTG Portfolio Monitor-derived pinned target selection, an OCI image build, and a systemd timer. The tests and [source-acquisition CI smoke workflow](../.github/workflows/evaluation-smoke.yml) cover the actual CLI path. The two execution contracts must not be conflated: documentary validation and retained-source target-specific examination establish different kinds of evidence.

## First result: entirely offline

Install dependencies from the repository root and execute:

```sh
python3 -m pip install -r requirements.txt
python3 -m runner validate --config runner/examples/retained-trqp.yaml
python3 -m runner run --config runner/examples/retained-trqp.yaml --target retained-trqp --output /tmp/rahp-evaluations
```

The second command invokes the **installed** `review/examine.py`; it does not
execute supplied target code. The executable checks the retained TRQP source
manifest, reruns the bounded observations and validates review/evidence bindings.
The CLI emits one run directory containing `evaluation.json` and
`evaluation.md`. An accepted machine reproduction is reported as
`validation: complete`, `assurance: review-required` and `execution: completed`.
A failed or incomplete examination exits nonzero and is never reported as
successful. The report is **not** an independent analysis or positive target
assurance determination.

## Configuration (v1alpha1)

`schema` must equal `rahp-evaluation-runner/v1alpha1`; `targets` is a nonempty
list. Every target requires a unique lower-case `id`, the exact supported
`repository`, `evaluator: upstream-retained-trqp`, and the complete immutable
40-character `source_revision` already pinned in the installed review.
Unknown config fields are rejected, not ignored. This deliberate restriction
prevents an operator from mistaking a repository name for an automatically
available RAHP evaluator. An optional `inventory` provenance block is validated
but is **advisory only**; it never grants assessment applicability or authority.

The runner reads local configuration as operator-trusted data, but neither config
nor target material can specify a shell command or executable module. The selected
upstream evaluator is installed in this checkout. The report records the exact
configuration hash and available runner Git revision. Result content is bounded
to the existing examiner's structured JSON (not raw logs). Review identity and
source material remain in the retained upstream example; revision agreement
against the review is checked before execution.

## Example: consuming a portfolio-derived selection

[`examples/dtg-portfolio-selection.yaml`](examples/dtg-portfolio-selection.yaml)
is a small **non-executable selection example**, adapted from the independent
[DTG Portfolio Monitor curated inventory](https://github.com/sankarshanmukhopadhyay/dtg-portfolio-monitor/blob/1a1982212bce36d79a5fb9dc6d58bec7b7d9e01a/config/repositories.yaml)
under Apache-2.0, source revision
`1a1982212bce36d79a5fb9dc6d58bec7b7d9e01a`.
The related [cross-spec compositions](https://github.com/sankarshanmukhopadhyay/dtg-portfolio-monitor/blob/1a1982212bce36d79a5fb9dc6d58bec7b7d9e01a/config/cross-spec-pressure-tests.yaml)
reference downstream RAHP assessment files, which this runner **cannot** execute.
Target role, lifecycle and material paths may guide a human in selecting a
reassessment; neither event materiality nor discovered scope establishes an
applicable RAHP risk evaluation. The first executable demonstration remains the
self-contained upstream TRQP example. A real interoperable profile adapter and a
second evaluator need separate upstream acceptance and test evidence.

## Scheduled execution and retention

The runner performs a single bounded evaluation and terminates. An operator may
invoke the same `run` command from cron or a systemd timer (for example, weekly
at 03:00 UTC), with a persistent output directory mounted on a VM or container.
The scheduler, time-zone normalization, retry policy, concurrency exclusion,
filesystem backup and retention period remain operator responsibilities in this
increment. Each execution gets a unique timestamp/nonce directory; no files are
overwritten or automatically deleted. No built-in scheduler or container release
is claimed.

Do not publish retained evidence directories blindly: even source-derived reports
may contain identifiers or contextual information. Restrict directory access and
report access, avoid secrets in config, and ensure read-only root checkout. The
runner intentionally does **not** perform remote Git fetches or trust a mutable
branch as proof of immutable source bytes.

## v1alpha1 limitations and upgrade path

The v1alpha1 offline path is a proof of the orchestration contract **for exactly one upstream-supported
retained-source evaluator**, not a generic evaluation service or general adapter
registry. Only trusted installed source is executed. Multi-target source acquisition, documentary profile selection, compatible-run comparison, and run locking are available under the separately documented v1alpha2 path. Durable multi-node evidence storage, cross-profile interpretation, generic target-specific evaluators and independent source authenticity verification are not established. Existing RAHP schemas, risk vocabulary, corpus and governance
status remain unchanged. The Task Force must independently review and accept any
wider methodology or operational commitment.

Tests: `python3 -m unittest discover -s tests -v`.
