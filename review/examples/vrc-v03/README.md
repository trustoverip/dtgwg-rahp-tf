# Source-pinned VRC v0.3 examination and reassessment

This example is the second real-source examination in the #17 convergence sequence. It tests whether the retained-source, review and evidence foundations demonstrated with TRQP can be reused for a materially different specification without importing the downstream RAHP controller.

The target is the historical **Decentralized Trust Graph Credentials - Core Specification (Early Draft, v0.3)** from `trustoverip/dtgwg-cred-tf`.

## Source reconstruction

Historical RAHP PR #6, **Evaluation of VRC Spec 0.3 using RAHP Toolkit**, was created on 8 May 2026 at 06:55:52 UTC. That PR did not retain the specification bytes or an immutable source revision used in its AI-assisted session.

The authoritative task-force source can nevertheless be reconstructed for a new reproducible examination:

- PR `dtgwg-cred-tf#31` had merged on 30 April 2026 at commit `62bbd8a19d598078f50560948ca71ec0e034a6fc`.
- PR `dtgwg-cred-tf#33` later merged at 08:36:46 UTC on 8 May 2026.
- The #33 merge commit, `200acbaa47a422b173652ed2c3dc961c4fbc9e7a`, has `62bbd8a19d598078f50560948ca71ec0e034a6fc` as its parent.
- Therefore `62bbd8a19d598078f50560948ca71ec0e034a6fc` is the authoritative `main` revision immediately preceding the #33 source change and contemporaneous with the #6 assessment.

This establishes the source used by **this** examination. It does **not** prove that the unretained file uploaded in the historical #6 AI session was byte-for-byte identical. That historical input remains unavailable.

The reassessment uses the real changed-source revision `200acbaa47a422b173652ed2c3dc961c4fbc9e7a`; no synthetic replacement revision is constructed.

Both revisions are retained under `baseline/` and `reassessed/`. Each manifest binds repository, immutable commit, upstream path, Git blob SHA and SHA-256 digest. `review/source_integrity.py` verifies the retained bytes before any observations are accepted.

## Examination question

Two source-derived propositions are tested.

| Finding | Baseline observation | Reassessment | Risk |
| --- | --- | --- | --- |
| F-001 | The general VRC ZKP subsection requires an underlying VMC and a VMC from the same C-DID | PR #33 separates pairwise VRC proof from community-anchored proof and explicitly states that shared VTC membership is not a precondition | `RK-SC02` Credential Schema Ambiguity |
| F-002 | M-DID reuse is allowed during bootstrapping and migration to R-DIDs is recommended rather than normatively triggered | The same bootstrapping/migration text remains | `RK-ID05` M-DID Linkability Across VTCs |

The baseline record therefore keeps both findings open. The reassessment closes F-001 as a documentary specification change and keeps F-002 open.

The risk mapping is bounded. F-001 uses `RK-SC02` because inconsistent interpretation of VRC/VMC proof semantics is the relevant maintained ambiguity risk. F-002 uses `RK-ID05` because that risk already records the residual M-DID bootstrapping/linkability window. No new canonical risk is created.

## Evidence model

`baseline-evidence.json` and `reassessed-evidence.json` are **example-local** sidecars. They bind:

- immutable target identity;
- exact RAHP method revision;
- exact review bytes;
- exact canonical risk-corpus bytes;
- fresh source-derived observations;
- evidence propositions that must resolve in retained source;
- finding-level observation, inference, limitations, treatment and per-risk reasoning.

They are validated by `evaluate.py`. Successful validation emits `overall_assurance: review-required`; it never turns source reproduction into target assurance.

The evidence selectors used here are source section/proposition matches. They deliberately differ from the TRQP example's result pointers and fixture bindings. See [generality.md](generality.md) for the resulting abstraction decision.

## Reproduce

From the repository root after installing `requirements.txt`:

```sh
python3 review/examples/vrc-v03/evaluate.py
python3 review/validate_spec_review.py review/examples/vrc-v03/baseline-review.yaml
python3 review/validate_spec_review.py review/examples/vrc-v03/reassessed-review.yaml
python3 -m unittest tests.test_vrc_reassessment -v
python3 -m unittest discover -s tests -v
```

Expected bounded result:

- retained source identity verifies for both revisions;
- SR-201 and SR-202 validate against the existing review contract;
- fresh observations match retained evidence;
- F-001 transitions `open -> resolved`;
- F-002 remains `open -> open`;
- overall assurance remains `review-required`.

Negative tests reject altered source bytes, a reassessment that silently reuses the baseline revision, stale observations, missing finding evidence, incorrect risk reasoning and evidence propositions that do not resolve in retained source.

## Scope and limitations

This exercise does not:

- reproduce the historical #6 AI conversation or prove its uploaded bytes;
- validate a ZKP implementation or circuit;
- test live credential issuance, presentation, revocation or trust-registry behavior;
- establish that the specification as a whole is safe or conformant;
- accept residual risk;
- standardize the example-local evidence sidecar.

The findings are documentary assessments of two source propositions. Independent reviewer judgment remains required.
