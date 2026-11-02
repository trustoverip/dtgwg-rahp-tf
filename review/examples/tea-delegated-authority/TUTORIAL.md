# Hello RAHP: examine delegated authority in TEA

This walkthrough uses the retained-source
[TEA delegated-authority example](README.md) to show a second complete RAHP
specification examination. It is intentionally different from the TRQP example:
the subject is not a response schema but a chain of delegated authority.

Run commands from the repository root after:

```bash
python3 -m pip install -r requirements.txt
```

**Expected result:** dependency installation exits 0. Environment setup is not
assurance evidence.

## 1. Bound the assurance question

**Goal:** choose one source proposition that can be examined without claiming to
assess all of TEA.

Question:

> Can an invocation remain demonstrably within effective delegated authority
> without treating authentication, execution outcome or later accountability as
> equivalent to authorization?

Included:

- capability resource, ability and limitation;
- attenuation down a constructed delegation chain;
- authorization of a constructed Exercise;
- separation of post-gate obligation breach from prior authorization.

Excluded:

- TSP conformance and transport behavior;
- VID/key resolution and signatures;
- concrete TEA Container/ACDC validation;
- revocation registry behavior and freshness;
- MCP/A2A integration;
- live agents or services;
- full TEA conformance.

**Interpretation:** the narrow question makes the review reproducible.

**Do not infer:** that excluded TEA behavior is correct or safe.

## 2. Identify affected actors and plausible harm

A minimal scenario contains:

- a Principal or root authority;
- a Delegator;
- a Delegate or re-delegate;
- a service controlling the resource;
- a person or organization affected by an over-broad exercise.

Plausible harm arises when an authenticated agent is permitted to perform an action
it was never delegated, when a re-delegation broadens authority, or when later
accountability evidence is confused with the authorization decision made at the
gate.

These are hypotheses for the worked example, not observed incidents.

## 3. Pin the TEA source

The review target is:

```yaml
repository: trustoverip/aimwg-trust-enabled-agents
revision: 7a53ecf3300dd6fb1bd4d6bcfab967475866e082
version_label: v0.2 Draft source snapshot
```

[source-manifest.json](source-manifest.json) retains the source identity.

The pinned draft states, among other things:

- authority is `(resource, ability, limitation)`;
- authorization is computed only from capability;
- effective capability is the meet down a delegation chain;
- re-delegation must be strictly attenuating;
- each Exercise is checked against effective capability at exercise time;
- obligations do not enter authorization;
- non-performance does not invalidate authority already exercised.

**Boundary:** source digest agreement proves consistency with this retained bundle,
not publisher authenticity or later TEA revisions.

## 4. State example-local risk hypotheses

[risks.yaml](risks.yaml) defines three hypotheses:

- `RK-AU01`: authentication mistaken for delegated authorization;
- `RK-AU02`: re-delegation or invocation broadens authority;
- `RK-AC01`: later obligation breach is treated as retroactively invalidating
  authorization.

They are local to this example and do not modify `data/risks.yaml`.

## 5. Understand the tiny capability vocabulary

The example deliberately supplies only enough concrete semantics to exercise the
pinned source proposition.

```text
resource
  path hierarchy
  /accounts
      └── /accounts/123

ability
  finite set
  {read, write, transfer}

limitation
  max_amount
  bounded scalar; meet = minimum
```

This is a fixture-local namespace, not a TEA standard vocabulary.

The effective capability is calculated component-wise:

```text
parent capability
        ∩
child restriction
        =
effective capability
```

## 6. Replay the constructed cases

**Input:** retained TEA source, [cases.json](cases.json) and
[expected-replay.json](expected-replay.json).

**Command:**

```bash
python3 review/examples/tea-delegated-authority/replay.py
```

Representative observations:

```text
within-authority
  authorized: true
  effective abilities: [transfer]
  max_amount: 250

ability-not-delegated
  authorized: false
  reason: exceeds-capability

attempted-broadening
  restriction_conformant: false
  authorized: false
  reason: invalid-redelegation

authenticated-without-capability
  authorized: false
  reason: no-capability

authorized-then-obligation-breach
  authorized: true
  post_gate_breach: true
```

**Interpretation:** the replay reproduces bounded fixture observations against a
small capability model derived from the retained source propositions.

**What it does not establish:** that a TEA Container, namespace, VID, TSP endpoint or
live implementation conforms.

**Common failure:** changing retained source, fixture expectations or a source
proposition causes the replay to exit nonzero rather than silently accepting drift.

**Next step:** distinguish what each negative case means.

## 7. Read the adversarial cases carefully

### Authentication without authority

The constructed holder is marked authenticated but has no capability chain:

```text
authenticated = true
capability = absent
authorization = denied
```

The lesson is not that TSP authentication was tested. It was not.

The lesson is that **authentication is not promoted into delegated authority** by
the worked evaluator.

### Attempted broadening

A parent grants only `read`; a child restriction names `read` and `write`.

```text
parent abilities = {read}
child expression = {read, write}

restriction conformant = false
effective meet = {read}
write exercise = denied
```

The source itself requires restriction-only re-delegation. The fixture therefore
records both facts: the constructed child restriction is nonconformant, and the
effective meet does not gain `write`.

### Obligation breach after an authorized exercise

The final case grants `transfer` and attaches a `report-result` obligation.

```text
exercise within capability = true
report-result obligation = unmet

authorization = true
post-gate breach = true
```

This reproduces the source distinction that obligation non-performance is an
accountability event and does not retroactively invalidate authority already
exercised.

## 8. Read the RAHP review record

Open [review.yaml](review.yaml).

It uses the existing upstream `rahp-spec-review/v1` contract. No TEA-specific
members were added.

The first three findings are `resolved` with
`resolution.type: already-addressed`, because the pinned source explicitly
addresses the bounded hypotheses. The fourth finding remains `open`:

```yaml
control_plane: runtime-control
status: open
```

That open finding records the missing implementation evidence rather than inventing
a source defect.

This demonstrates that a worked RAHP examination does not need to manufacture a
problem in the target specification.

## 9. Validate the review

**Input:** `review.yaml`, the upstream review contract and the explicit local risk
source.

**Command:**

```bash
python3 review/validate_spec_review.py review/examples/tea-delegated-authority/review.yaml --risks review/examples/tea-delegated-authority/risks.yaml
```

**Expected output:**

```text
PASS: review/examples/tea-delegated-authority/review.yaml
```

**Interpretation:** structure, immutable target identity, finding semantics and risk
references are valid.

**What it does not establish:** correctness of the reviewer inference or TEA
conformance.

## 10. Bind evidence to the findings

[evidence.json](evidence.json) is explicitly example-local.

It links:

```text
retained TEA clauses
constructed cases
fresh replay observations
        ↓
observation
        ↓
reviewer inference
        ↓
limitations
        ↓
treatment
```

For the attempted-broadening finding, the evidence combines the retained attenuation
text, constructed fixture, nonconformant-restriction observation and retained
strict-attenuation proposition.

For the obligation finding, the evidence combines retained source definitions with
the observation that authorization remains true while `post_gate_breach` is true.

The sidecar does not standardize a universal RAHP evidence schema.

## 11. Validate the composed examination

**Input:** retained source, fixtures, expected replay, review, local risks and
example-local evidence sidecar.

**Command:**

```bash
python3 review/examples/tea-delegated-authority/examine.py
```

**Expected result:**

```json
{
  "assessment_id": "SR-003",
  "validation": "complete",
  "scope": "retained TEA v0.2 Draft source and constructed capability fixtures only",
  "overall_assurance": "review-required",
  "unassessed": {
    "tsp_transport": "not-assessed",
    "vid_resolution": "not-assessed",
    "revocation": "not-assessed",
    "live_service": "not-assessed",
    "full_tea_conformance": "not-assessed"
  },
  "findings": 4,
  "open_findings": 1
}
```

Read these independently:

```text
validation: complete
overall_assurance: review-required
```

The package is reproducible. The target has not been certified.

## 12. Observe fail-closed behavior

The `attempted-broadening` case is the domain-level negative control:

```text
restriction_conformant: false
authorized: false
reason: invalid-redelegation
```

Repository regressions also mutate retained source, fixture expectations and
evidence observations. Each mutation must make the composed examination fail
nonzero.

**Interpretation:** neither authority escalation nor evidence drift is converted
into a successful result.

## 13. Interpret the completed exercise

Mechanically established:

```text
retained TEA source identity:       reproduced
bounded source propositions:        present
constructed capability cases:       reproduced
upstream review record:             valid
local risk references:              resolved
evidence bindings:                  valid
resolved findings:                  3
open runtime-evidence findings:     1
overall assurance:                  review-required
```

Not established:

```text
TSP conformance
VID/key correctness
TEA Container conformance
revocation behavior
live authorization enforcement
obligation discharge
full TEA conformance
deployment assurance
```

## 14. Reassess when TEA changes

TEA is a v0.2 Draft. A later material revision should produce a new source-pinned
review rather than editing this one to point at a moving target.

```text
TEA revision A
      ↓
    SR-003
      ↓
bounded findings

TEA revision B
      ↓
new assessment
      ↓
re-evaluate each proposition
```

If later source changes the capability lattice, attenuation rules, invocation
checks or post-gate semantics, retain this assessment as evidence about revision A
and create a new record.

## 15. What this example says about RAHP

This example uses the same upstream review contract as the retained TRQP and VRC
work while examining a different assurance shape: delegated authority rather than
response structure or historical reassessment.

If a future refinement is needed, it should be justified by a concrete inability
demonstrated by this example. The example itself does not require a RAHP core
semantic change.

## Continue

- [Technical summary](README.md)
- [RAHP specification review records](../../README.md)
- [Specification pressure-testing workflow](../../../docs/pressure-testing-a-spec.md)
- [Retained-source TRQP example](../standalone-trqp/README.md)
- [VRC reassessment example](../vrc-v03/README.md)

AI-assisted example preparation. Risk scoring, governance decisions and target
assurance remain human responsibilities.
