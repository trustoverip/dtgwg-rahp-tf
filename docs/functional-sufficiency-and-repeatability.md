# Upstream RAHP functional sufficiency and repeatability assessment

Tracking: upstream convergence issue #17. **Contributor engineering assessment**, not a task-force decision and not Increment 7's unfamiliar-adopter trial.

## Proposition and current assessment

The accepted upstream baseline has a coherent **bounded specification-review** workflow: an immutable review target, explicitly selected risks, review schema and vocabulary, validation, and TRQP/VRC example-local source/evidence examination and reassessment. Another group may author its own RAHP review record using these contracts without the downstream toolkit.

**Important limitation:** It does **not** supply a general evaluator that automatically extracts harms from arbitrary specifications or certifies the truth of reviewer judgments. TRQP and VRC evaluators are specific to those subjects. For a third specification, the reusable generic path is **documentary review, risk mapping and schema validation**; any machine-observable proposition requires separately described, target-specific checks. Do not present validation-only operation as a full automated examination.

## First-use protocol (no downstream checkout)

1. Install `requirements.txt` in a fresh Python environment. The replay report records the running Python version and the versions of the two validator dependencies (PyYAML and jsonschema); retain a separate environment lock if cross-machine reproduction matters.
2. Select a bounded question and immutable target Git commit. Record the exact reviewed artifact and how the bytes were obtained. Retain source bytes where rights permit, and hash them.
3. Identify who may be affected by the target specification, including people or communities least able to object or obtain remedy, and state what plausible harms or adverse consequences the review is intended to examine. Use the participant and harm-scoping guidance in `ADOPTION.md` rather than treating risk selection as a purely technical exercise.
4. Choose an explicit risk corpus. The default `data/risks.yaml` is a DTG instance, **not a universal risk list**; a new group must justify selected risks or maintain its own corpus.
5. Copy `review/examples/minimal-review.yaml` to a new review file outside generated `build/`. Replace the illustrative `reviewer: example-reviewer` with the actual accountable reviewer identity (do not imply an independent review occurred). Assign a fresh assessment ID and a full immutable source revision. Author findings, associated risk identifiers, control planes and statuses. Preserve observation/source citations, inference and limitations in accompanying human-readable material because `rahp-spec-review/v1` does **not** permit extra arbitrary evidence fields.
6. Run the explicit validator, then the repeatability helper:
   ```sh
   python3 review/validate_spec_review.py /path/to/review.yaml --risks /path/to/risks.yaml
   python3 review/replay_check.py --review /path/to/review.yaml --risks /path/to/risks.yaml --source /path/to/retained-target.md --repeat 3 --output /path/to/replay-evidence.json
   ```
7. Change one input deliberately (an unknown risk, mutable revision or missing source); require a nonzero validation exit and capture the counterexample. Restore the original input and reproduce the accepted result.
8. Ask a competent reviewer who did not author the assessment to read the findings against the source and record material disagreement, missing harms or unsupported inferences. Independent review does not convert a review record into risk-acceptance authority.
9. On material source change, create a new review with a **different immutable revision**. Preserve earlier records; explicitly justify which findings are resolved, persistent or out of scope. Do not inherit a prior assurance conclusion.

### Bounded mechanical repeatability checks

| Dimension | What is compared | Success condition | Does not establish |
| --- | --- | --- | --- |
| Input identity | SHA-256 digest of review, selected risk corpus, canonical risk-acceptance corpus, validator, schema, method vocabulary and optional retained source | Same bytes before and after the run | Authenticity of Git hosting or truth of source assertions |
| Mechanical repeatability | Exit code, stdout and stderr from 2–20 sequential validator executions | Identical hashed input bytes and identical raw exit code/stdout/stderr across sequential runs on the same machine | Deterministic reviewer judgment |
| Negative controls | Intentionally corrupted/missing inputs | Invalid material must be rejected or reported invalid, never called PASS | Complete coverage of all failure modes |
| Documentary trace | Source passages, evidence, inferential steps, limitations and resolutions | A reviewer can inspect the argument and reproduce the checks | Independent authority or runtime effectiveness |
| Reassessment | Source revisions, prior records and finding transitions | New immutable source recorded; earlier evidence retained and unresolved findings visible | Automatic freshness/lineage controller |

The checker reports `validation_accepted` and `machine_results_identical` separately. Equality is evaluated on the **raw** execution observations before publication redaction. The output contract is `rahp-review-replay-check/v2`: `observed_result.stdout` and `.stderr` are redacted, while `observed_result_raw_sha256` records hashes of the original streams; `environment` records the Python implementation/version and PyYAML/jsonschema versions. Consumers expecting unsanitized stdout/stderr from v1 must migrate. Redaction is a bounded privacy safeguard, not proof that arbitrary validator text is safe to publish. A stable rejection is reproducible **failure**, not successful assessment. If an optional supplied source is passed, its bytes are hashed but this tool **does not validate that these bytes came from the review's claimed Git commit**. Use the upstream TRQP/VRC retained-source verification path when that stronger claim is required. Pin the environment and source checkout in retained provenance: one-machine repeatability does not establish cross-machine reproducibility, and recorded versions alone do not guarantee equivalent environments.

For scientific repeatability beyond mechanical checks, formulate explicit propositions, independent observations, a fixed test protocol, expected results, tolerances for nondeterministic observations, negative controls, review qualifications and a protocol for resolving disagreements. The current framework records interpretation; it does not make interpretative judgments automatically reproducible by computation.

## Capability assessment

| Functional objective from #17 | Accepted upstream feature | Qualification |
| --- | --- | --- |
| Immutable target and corpus | `rahp-spec-review/v1` and explicit `--risks` | Supported, but Git authenticity requires independent verification |
| Source identity | `review/source_integrity.py` | Supported for retained-source manifest workflows, not arbitrary sources by default |
| Bounded examination | TRQP/VRC evaluators | Demonstrated for two subjects; third subject requires its own evidentiary propositions |
| Findings, evidence, reasoning | Review schema plus example-local evidence bindings/human-readable reasoning | Functional, but no normative generic evidence sidecar |
| Validation and repeatability | `validate_spec_review.py`, `validate_all.py` plus `replay_check.py` | Mechanical repeatability testable, not independent judgment reproducibility |
| Reassessment | Two immutable VRC revisions and retained historical records | Demonstrated; cross-run general lineage machinery not established |

**Contributor assessment:** The current upstream system appears **functionally sufficient for a human-led, source-pinned and reproducibly validated first specification review**, with a bounded evaluator developed for any target-specific automated observations. This is an engineering judgment based on the repository evidence inspected here; the task force has not adopted it as a governance decision and an unfamiliar-adopter trial remains outstanding. It is **not yet proven sufficient for fully automated arbitrary-specification examination**, and this capability is not implied by the issue objectives. Increment 7 should test first-use discoverability and an independent adopter's ability to follow the documented workflow without contributor assistance, including one deliberate negative control and reassessment.

**Governance:** No terminal assurance result, risk acceptance or independent review is inferred from successfully replayed validation. Contribution and method/corpus governance remain upstream; the downstream toolkit is not a runtime dependency. Preparation was AI-assisted. The evidence has explicit test limits, and repository CI provides engineering validation, not independent review, task-force endorsement or source/target assurance.
