# TRQP × VRC generality checkpoint

Increment 5 is the first point at which the #17 convergence work has two real-source examinations to compare. The purpose of this note is to identify demonstrated reuse without promoting a first-example implementation detail into method authority.

## Observed common structure

Both the TRQP and VRC examinations require the following information to make an assessment independently reproducible:

| Concern | TRQP | VRC | Generality judgment |
| --- | --- | --- | --- |
| Immutable target repository and revision | yes | yes | reusable invariant |
| Retained source integrity with Git blob + SHA-256 | yes | yes | reusable invariant |
| Explicit RAHP method identity | yes | yes | reusable invariant |
| Existing `rahp-spec-review/v1` record | yes | yes | reusable upstream contract |
| Exact review binding | yes | yes | reusable invariant |
| Explicit risk-corpus binding | yes | yes | reusable invariant |
| Fresh execution state separate from assurance | yes | yes | reusable invariant |
| Finding-to-evidence references | yes | yes | reusable invariant |
| Observation distinct from inference | yes | yes | reusable invariant |
| Finding limitations and proposed treatment | yes | yes | reusable invariant |
| Per-risk mapping rationale | yes | yes | reusable invariant |
| Failure on stale/missing/contradictory evidence | yes | yes | reusable invariant |

This is stronger evidence for a **minimal evidence envelope** than the TRQP example alone provided.

## What does not generalize cleanly

The following remain subject-specific:

- **Observation vocabulary.** TRQP observes replay/schema/query-response behavior; VRC observes source propositions and source-change deltas.
- **Evidence selectors.** TRQP uses result pointers, retained fixtures and source files. VRC uses source sections and proposition matches.
- **Evaluator logic.** TRQP executes protocol-shaped examples. VRC performs deterministic documentary checks over two specification revisions.
- **Unassessed dimensions.** The TRQP example explicitly tracks authority, delegation, revocation and runtime authorization. Those fixed dimensions are not a universal evidence-envelope requirement for every specification review.
- **Reassessment semantics.** VRC demonstrates a real changed-source transition; not every examination has a suitable second revision.

These differences are material. A shared schema that hard-codes TRQP result pointers, VRC section matching, or a fixed list of unassessed dimensions would encode example mechanics as method.

## Decision

**Do not standardize either complete example-local sidecar as the shared RAHP evidence contract in Increment 5.**

The two examples now justify a narrower proposition: a future shared evidence contract may define the common envelope for target/method identity, review and corpus bindings, execution state, evidence identifiers, finding coverage, reasoning and limitations, while leaving evidence selector types and observation payloads extensible or profiled.

That proposition should be taken as a separate method decision after the current review-contract changes settle. Increment 5 does not need a new schema or abstraction to prove generality, and adding one now would increase compatibility surface before the task force has reviewed the second case.

## Consequence for downstream alignment

Increment 6 should align downstream only to **accepted** upstream contracts:

- retained-source integrity behavior;
- the existing review contract;
- governed vocabulary/validation behavior;
- any later evidence-envelope contract that is actually accepted.

The downstream toolkit should not treat either `trqp-example-evidence/v1` or `vrc-example-evidence/v1` as canonical upstream method simply because both exist.
