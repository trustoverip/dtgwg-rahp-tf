# Pressure-testing a specification with RAHP

This guide defines a small, reproducible workflow for reviewing a specification or
change set against RAHP risks and recording actionable findings.

The review record is deliberately narrower than a full assurance controller. It
answers four questions:

1. **What exact source revision was reviewed?**
2. **Which RAHP risks are implicated by each finding?**
3. **Where should the finding be controlled?**
4. **What is the current disposition of the finding?**

A completed review is not, by itself, an assurance PASS. Missing evidence and
unresolved findings remain visible.

## 1. Pin the review target

Review an immutable source revision. For Git repositories, `target.revision` MUST
be a full 40-hex commit SHA. Branch names such as `main` are intentionally rejected
because they do not identify a reproducible assessment subject.

```yaml
target:
  repository: https://github.com/example/specification
  revision: 0123456789abcdef0123456789abcdef01234567
```

A human-readable release or working-draft label may be added as `version_label`,
but it does not replace the immutable revision.

## 2. Establish the RAHP context

Record the RAHP method/toolkit version used for the review:

```yaml
rahp_version: v0.3-dev
```

The version identifies the risk corpus and method context against which the target
was assessed. A later review against a changed target or changed RAHP context should
use a new review record while preserving the prior record as historical evidence.

## 3. Reuse risks before creating new ones

Start from the current RAHP risk corpus. Each finding MUST reference at least one
existing `RK-*` identifier. The validator rejects unknown risk references.

The purpose is to keep specification review connected to the maintained risks and
harms model rather than creating an ungoverned parallel issue vocabulary.

## 4. Record findings

Each finding has a stable identifier and a concise summary:

```yaml
- id: F-001
  summary: The specification does not define the required authority check.
  risks: [RK-EX04]
```

Finding identifiers are unique within the review record. Duplicate IDs are rejected.

## 5. Separate control plane from finding status

A finding has two distinct dimensions.

`control_plane` answers **where the risk should be controlled**:

- `specification`
- `companion-specification`
- `governance`
- `implementation-guidance`
- `runtime-control`
- `operational-policy`
- `none`

`status` answers **what has happened to the finding**:

- `open`
- `in_progress`
- `resolved`
- `risk_accepted`
- `out_of_scope`
- `superseded`

These are intentionally separate. For example, a finding may belong in governance
and still be open, or belong in the specification and already be resolved.

## 6. Record resolution evidence

Terminal dispositions require a structured `resolution` object. A resolved finding
must explain what closed it. A risk-accepted finding must reference the authority
record that accepted the residual risk.

```yaml
status: resolved
resolution:
  type: specification-change
  reference: https://github.com/example/specification/pull/42
  rationale: The merged change adds the required normative authority check.
```

The allowed resolution types are:

- `specification-change`
- `companion-specification-change`
- `governance-action`
- `implementation-guidance`
- `runtime-control`
- `operational-policy`
- `risk-acceptance`
- `already-addressed`
- `no-action`
- `superseded`

A `risk_accepted` status specifically requires `resolution.type: risk-acceptance`
and a non-empty reference.

## 7. Validate the review

Install the existing repository dependencies and run:

```bash
python3 review/validate_spec_review.py review/examples/minimal-review.yaml
python3 -m unittest discover -s tests -p 'test_*.py'
```

The validator checks the JSON Schema, immutable source pinning, finding identifier
uniqueness and resolution of risk references against `data/risks.yaml`.

## 8. Reassess after material change

When the target specification materially changes, create a new source-pinned review
rather than editing the old review to point at the new source. Findings may be
re-evaluated, resolved, superseded or retained, but the prior review remains evidence
of what was assessed at that earlier revision.

This first contract does not prescribe a complete cross-run lineage model. It
establishes the minimum data needed for later reassessment to be reproducible.

## Minimal record

See [`review/examples/minimal-review.yaml`](../review/examples/minimal-review.yaml).

The record deliberately demonstrates both an open specification finding and a
resolved governance finding. It is an example of the contract, not an assurance
conclusion about the DTG Credential Specification.
