# Upstream RAHP functional sufficiency and repeatability qualification

Tracking: upstream convergence issue #17. **Engineering qualification**, not Increment 7's unfamiliar-adopter trial.

## Proposition and current assessment

The accepted upstream baseline has a coherent **bounded specification-review** workflow: an immutable review target, explicitly selected risks, review schema and vocabulary, validation, and TRQP/VRC example-local source/evidence examination and reassessment. Another group may author its own RAHP review record using these contracts without the downstream toolkit.

**Important limitation:** It does **not** supply a general evaluator that automatically extracts harms from arbitrary specifications or certifies the truth of reviewer judgments. TRQP and VRC evaluators are specific to those subjects. For a third specification, the reusable generic path is **documentary review, risk mapping and schema validation**; any machine-observable proposition requires separately described, target-specific checks. Do not present validation-only operation as a full automated examination.

## First-use protocol (no downstream checkout)

1. Install `requirements.txt` in a fresh Python environment; record Python and dependency versions.
2. Select a bounded question and immutable target Git commit. Record the exact reviewed artifact and how the bytes were obtained. Retain source bytes where rights permit, and hash them.
3. Choose an explicit risk corpus. The default `data/risks.yaml` is a DTG instance, **not a universal risk list**; a new group must justify selected risks or maintain its own corpus.
4. Copy `review/examples/minimal-review.yaml` to a new review file outside generated `build/`. Assign a fresh assessment ID and a full immutable source revision. Author findings, associated risk identifiers, control planes and statuses. Preserve observation/source citations, inference and limitations in accompanying human-readable material because `rahp-spec-review/v1` does **not** permit extra arbitrary evidence fields.
5. Run the explicit validator, then the repeatability helper:
   ```sh
   python3 review/validate_spec_review.py /path/to/review.yaml --risks /path/to/risks.yaml
   python3 review/replay_check.py --review /path/to/review.yaml --risks /path/to/risks.yaml --source /path/to/retained-target.md --repeat 3 --output /path/to/replay-evidence.json
   ```
6. Change one input deliberately (an unknown risk, mutable revision or missing source); require a nonzero validation exit and capture the counterexample. Restore the original input and reproduce the accepted result.
7. On material source change, create a new review with a **different immutable revision**. Preserve earlier records; explicitly justify which findings are resolved, persistent or out of scope. Do not inherit a prior assurance conclusion.

### Quantitative, falsifiable reproducibility criteria

| Dimension | What is compared | Success condition | Does not establish |
| --- | --- | --- | --- |
| Input identity | SHA-256 digest of review, selected risk corpus, validator, schema, method vocabulary and optional retained source | Same bytes before and after the run | Authenticity of Git hosting or truth of source assertions |
| Mechanical repeatability | Exit code, stdout and stderr from 2–20 sequential validator executions | Byte-identical normalized inputs and **identical observed outputs** | Deterministic reviewer judgment |
| Negative controls | Intentionally corrupted/missing inputs | Invalid material must be rejected or reported invalid, never called PASS | Complete coverage of all failure modes |
| Documentary trace | Source passages, evidence, inferential steps, limitations and resolutions | A reviewer can inspect the argument and reproduce the checks | Independent authority or runtime effectiveness |
| Reassessment | Source revisions, prior records and finding transitions | New immutable source recorded; earlier evidence retained and unresolved findings visible | Automatic freshness/lineage controller |

The checker reports `validation_accepted` and `machine_results_identical` separately. A stable rejection is reproducible **failure**, not successful assessment. If an optional supplied source is passed, its bytes are hashed but this tool **does not validate that these bytes came from the review's claimed Git commit**. Use the upstream TRQP/VRC retained-source verification path when that stronger claim is required. Pin the environment and source checkout in retained provenance: dependence on a moving environment invalidates cross-machine reproducibility assumptions.

For scientific repeatability beyond mechanical checks, formulate explicit propositions, independent observations, a fixed test protocol, expected results, tolerances for nondeterministic observations, negative controls, review qualifications and a protocol for resolving disagreements. The current framework records interpretation; it does not make interpretative judgments automatically reproducible by computation.

## Capability sufficiency result

| Functional objective from #17 | Accepted upstream feature | Qualification |
| --- | --- | --- |
| Immutable target and corpus | `rahp-spec-review/v1` and explicit `--risks` | Supported, but Git authenticity requires independent verification |
| Source identity | `review/source_integrity.py` | Supported for retained-source manifest workflows, not arbitrary sources by default |
| Bounded examination | TRQP/VRC evaluators | Demonstrated for two subjects; third subject requires its own evidentiary propositions |
| Findings, evidence, reasoning | Review schema plus example-local evidence bindings/human-readable reasoning | Functional, but no normative generic evidence sidecar |
| Validation and repeatability | `validate_spec_review.py`, `validate_all.py` plus `replay_check.py` | Mechanical repeatability testable, not independent judgment reproducibility |
| Reassessment | Two immutable VRC revisions and retained historical records | Demonstrated; cross-run general lineage machinery not established |

**Decision:** The upstream system is **functionally sufficient for a human-led, source-pinned and reproducibly validated first specification review**, with a bounded evaluator developed for any target-specific automated observations. It is **not yet proven sufficient for fully automated arbitrary-specification examination**, and this capability is not implied by the issue objectives. Increment 7 should test first-use discoverability and an independent adopter's ability to follow the documented workflow without contributor assistance, including one deliberate negative control and reassessment.

**Governance:** No terminal assurance result, risk acceptance or independent review is inferred from successfully replayed validation. Contribution and method/corpus governance remain upstream; the downstream toolkit is not a runtime dependency. AI-assisted preparation, explicit test limits; reproducibility evidence becomes qualified only once full current-head CI and tests are verified.
