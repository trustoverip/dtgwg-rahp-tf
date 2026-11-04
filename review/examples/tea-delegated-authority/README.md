# Worked example: TEA delegated authority and invocation

This example applies upstream RAHP to one bounded question in the **Trust-Enabled
Agents (TEA) v0.2 Draft**:

> Can an invocation be shown to remain within the effective authority delegated
> through a TEA capability chain, without confusing authenticated identity,
> successful execution, or post-action accountability with authorization?

The target is `trustoverip/aimwg-trust-enabled-agents` at immutable commit
`7a53ecf3300dd6fb1bd4d6bcfab967475866e082`. The retained source describes
capability authority as `(resource, ability, limitation)`, effective capability as
a meet down a delegation chain, strict attenuation for re-delegation, per-exercise
authorization checks, and obligations as post-gate policy.

This is a **worked RAHP examination**, not a TEA conformance suite. It does not
execute TSP, resolve VIDs, validate TEA Containers, test revocation, contact a live
service or assess the whole TEA specification.

For the sequential first-use walkthrough, start with
[the tutorial](TUTORIAL.md).

## What is retained

- [source-manifest.json](source-manifest.json) pins six unmodified TEA source files
  by immutable URL, Git blob identifier and SHA-256.
- [cases.json](cases.json) defines six constructed teaching fixtures using a tiny
  example-local resource hierarchy, ability vocabulary and one bounded-scalar
  limitation.
- [expected-replay.json](expected-replay.json) retains deterministic observations.
- [risks.yaml](risks.yaml) contains three example-local hypotheses; they are not
  canonical DTG risks.
- [review.yaml](review.yaml) uses the existing upstream
  `rahp-spec-review/v1` contract.
- [evidence.json](evidence.json) binds source, fixture and replay evidence to the
  findings using an example-local schema.
- [replay.py](replay.py) evaluates only the bounded constructed capability model.
- [examine.py](examine.py) composes retained-source verification, fresh replay,
  review validation and evidence binding.

## Reproduce

From the repository root after installing `requirements.txt`:

```bash
python3 review/examples/tea-delegated-authority/replay.py
python3 review/validate_spec_review.py review/examples/tea-delegated-authority/review.yaml --risks review/examples/tea-delegated-authority/risks.yaml
python3 review/examples/tea-delegated-authority/examine.py
```

A successful composed examination reports `validation: complete` and
`overall_assurance: review-required`. Those states describe different things:
the example package is reproducible while live TEA behavior remains unassessed.

## Constructed cases

| Case | Expected bounded observation |
| --- | --- |
| `within-authority` | exercise is within the attenuated capability |
| `ability-not-delegated` | authenticated holder is denied an undelegated ability |
| `attenuated-redelegation` | child resource/ability/amount narrow the parent |
| `attempted-broadening` | restriction is nonconformant and undelegated ability is not acquired |
| `authenticated-without-capability` | authentication alone does not establish delegated authority |
| `authorized-then-obligation-breach` | exercise remains authorized; unmet obligation is recorded post-gate |

The evaluator is intentionally smaller than TEA. Resource ordering is represented by
a path hierarchy, abilities by set intersection and one `max_amount` limitation by
minimum. Those choices are constructed examples of the source's meet semantics, not
a general namespace implementation.

## Findings and assurance boundary

The contributor's review records three source propositions as already addressed
in the pinned draft, citing specific retained source sections:

1. authentication does not replace capability-chain authorization;
2. delegated authority is strictly attenuating; and
3. obligation non-performance does not retroactively invalidate authority already
   exercised.

These are source-based author judgments, not independently accepted assurance.
The retained clause locations are shown in the [tutorial](TUTORIAL.md);
a person who did not prepare the assessment must corroborate or challenge
the conclusions and record that judgment before this example supports
evidence claims in #35.

A fourth finding remains open because runtime enforcement, holder binding,
revocation and accountability evidence are not examined.

The example therefore establishes neither TEA conformance nor deployment assurance.

## Attribution

Retained files reproduce Trust over IP Foundation TEA source at the immutable
revision above. The original [license](source/LICENSE.md.txt) remains applicable.
The `.txt` suffix preserves source bytes without publishing upstream Markdown as
RAHP documentation. This examination implies no TEA specification-owner
endorsement.

Preparation of the RAHP example was AI-assisted and remains subject to independent
human review under the repository contribution process.
