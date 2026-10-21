# How RAHP Builds Assurance Incrementally

This note explains how the RAHP convergence work in issue #17 builds an assurance capability through small, reviewable increments. It is intended to help contributors, reviewers and adopting working groups understand where evidence preparation stops, where RAHP assessment begins, and why successful validation is not the same thing as assurance acceptance.

The note is explanatory. It does not replace the review schema, the method vocabularies, the risk corpus or task-force decisions. Where an increment uses experimental structures, such as an example-local evidence sidecar, those structures remain experimental until the task force accepts them as reusable contracts.

## RAHP purpose and scope

As defined in the repository README, the RAHP Toolkit is a method for embedding human harm prevention into the design of decentralised trust systems from the outset. Its core question is who gets hurt if a trust-system design is wrong.

This note focuses on how that harm-prevention method becomes reviewable: specifications and designs are examined using reproducible evidence, governed assessment criteria and accountable reviewer judgment.

Validation, replay and schema checks produce evidence for an assessment. They are not, by themselves, the assessment. A RAHP assessment interprets evidence against selected risks, controls, guardrails, limitations and accountable review judgment.

## Core separation of concerns

The upstream convergence work deliberately separates four concerns.

| Layer | Purpose | Typical outputs | What it does not establish |
|---|---|---|---|
| Source preparation | Identify and retain the specification material being examined | Source manifest, retained source bytes, attribution, digests | That the specification is correct or safe |
| Evidence generation | Execute bounded checks over the retained source | Replay output, observations, validation logs, extracted fixtures | That an observation is a RAHP finding |
| RAHP assessment | Interpret observations against risks, controls, evidence and limitations | Findings, risk mappings, evidence bindings, proposed treatment | Task-force acceptance or risk acceptance |
| Assurance interpretation | Decide what the assessment means for adoption, remediation or acceptance | Review outcome, residual risk position, decision records | That automated tooling alone has authority |

This separation is important because individual increments may establish one layer without claiming to complete the whole assurance lifecycle.

This is an assurance and evidence progression. It does not claim to be the only useful architectural decomposition of RAHP.

## Why Increment 1 is still part of RAHP

Increment 1 establishes a reproducible source-to-observation path. In the TRQP example, retained source material is verified, replayed and checked without depending on the downstream toolkit. That is not a complete RAHP assessment, but it is a necessary RAHP foundation.

The scope boundary should be explicit: Increment 1 proves that the material being examined and the observations derived from it can be reproduced. Increment 2 then connects those observations to review records, risks, evidence bindings and limitations.

Without this foundation, later review conclusions would rest on opaque or unstable evidence. With it, reviewers can inspect the source material, rerun the checks and decide whether the resulting observations support a RAHP finding.

## Observations before findings

RAHP should distinguish observed evidence from interpreted findings.

For example, the TRQP worked example records a mismatch between the API example query time and the returned `time_requested` value. That is a reproducible observation. It becomes a specification finding only after the relevant TRQP semantics are examined.

Possible interpretations include:

- the example contains an error;
- the specification is ambiguous about the relevant time fields;
- the mismatch is intentional but under-explained;
- the replay is testing the wrong proposition.

The useful RAHP behavior is therefore not simply "the tool found a bug". The useful behavior is that RAHP produced reproducible evidence that can be carried into a specification discussion without losing provenance, scope or limitations.

## Evidence before assurance success

Successful execution must not silently become assurance success.

A valid replay, passing schema check or complete evidence bundle can show that the review material is internally consistent. It does not prove that all relevant harms are addressed, that the risk treatment is acceptable, or that an accountable human reviewer has accepted the conclusion.

For that reason, the current convergence work should preserve outcomes such as `review-required`, `not-assessed` and explicit limitations. Missing authority, delegation, revocation or runtime-authorization evidence should remain visible rather than being inferred away.

## Reviewer judgment and accountability

RAHP reviews may be supported by automated tooling and AI-assisted workflows. Those tools can help execute checks, surface inconsistencies, compare records and prepare candidate findings.

They do not replace accountable review judgment.

At the RAHP Task Force meeting on 14 October 2026, the task force agreed that review records should identify the reviewer. A review record should therefore preserve enough information to distinguish:

- the evidence generated by tools;
- the inference drawn from that evidence;
- the person or role accountable for the assessment;
- the authority responsible for accepting, rejecting or deferring the risk treatment.

Reviewer identity does not by itself establish risk-acceptance authority.

This distinction becomes especially important for statuses such as `risk_accepted`. PR #28 proposes validator enforcement that a `risk_accepted` finding references a real accepted record in `data/risk-acceptances.yaml`; that enforcement remains under review until #28 is merged.

## Vocabulary as method, not implementation detail

Review vocabulary shapes how findings are interpreted. Terms such as `control_plane`, finding status and resolution type are therefore part of the RAHP method rather than incidental validator implementation.

The task force agreed this direction on 14 October 2026. PR #27 subsequently moved the review vocabularies and their definitions into `method/vocabularies.yaml`, and PR #21 removed the duplicated hard-coded review-enum copy from the combined validation path. The repository now has one governed source for these definitions and validation checks that detect schema drift.

PR #28, currently under review, adds further semantic checks derived from those definitions. Until it is merged, those proposed checks should not be treated as current repository behavior.

## Local hypotheses, corpus risks and examples

The task force agreed on 14 October 2026 that examples should cite risks properly and must not use example-only identifiers that can be mistaken for canonical corpus risk IDs.

Where a worked example genuinely needs a local hypothesis before the corpus contains a suitable canonical risk, that hypothesis must be visibly distinct from corpus records. A separate namespace or prefix is one way to preserve that distinction.

Each risk reference used by an example should make clear whether it is:

- a canonical corpus risk;
- an example-local hypothesis;
- a candidate risk requiring corpus triage;
- a deliberately constructed teaching fixture.

The goal is to let examples teach the method without accidentally expanding or impersonating the authoritative corpus.

## Increment sequence

The #17 sequence can be read as a staged assurance build-out.

| Increment | Assurance role |
|---|---|
| Increment 1: retained-source integrity and TRQP replay | Establishes reproducible source preparation and observation generation |
| Increment 2: evidence-linked assessment | Connects observations to review records, risk references, evidence bindings and limitations |
| Increment 3: vocabulary and validation consolidation | Makes review semantics and validation behavior consistent and reusable |
| Increment 4: validation hardening and CI evidence | Ensures repository checks prove that required validation actually occurred |
| Increment 5: VRC examination and reassessment | Demonstrates reuse beyond TRQP and tests reassessment behavior across source changes |
| Increment 6: downstream compatibility alignment | Keeps accepted upstream contracts and downstream extensions coherent |
| Increment 7: adoption qualification and release | Tests whether another working group can use the baseline without contributor assistance |

The sequence should remain small enough for independent review, but each increment should state what layer it implements, what it deliberately does not implement, and what evidence is required before the next increment relies on it.

## Guidance for future pull requests

Each convergence pull request should answer the following questions in its description or associated documentation.

1. Which assurance layer does this increment implement?
2. What evidence does it produce or validate?
3. What RAHP judgment does it enable?
4. What judgment does it deliberately avoid making?
5. Which risks, controls, vocabularies or review records are affected?
6. What remains experimental, example-local or subject to task-force decision?
7. What should an independent reviewer rerun to reproduce the claim?

Answering these questions should make future reviews easier for human reviewers, tool-assisted reviewers and adopting working groups.

These questions also expose a broader contribution-governance need: the repository pull-request template should support method, tooling and convergence changes rather than only corpus-record changes. That change belongs in a separate GAP-5.1 contribution-governance tranche so that the repository-wide merge policy can be reviewed independently.
