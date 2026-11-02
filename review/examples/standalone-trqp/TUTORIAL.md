# Hello RAHP: examine a specification step by step

This tutorial shows how to complete one bounded RAHP specification examination from
start to finish using only the upstream repository. It uses the retained-source
[TRQP example](README.md), but the sequence is intended to teach the method rather
than TRQP itself.

The example is deliberately not an assurance certification. A successful run means
that the retained source, review record, selected risks and evidence bindings are
internally reproducible. It does **not** establish that a live TRQP deployment is
authorized, secure, conformant or acceptable.

Run every command from the repository root after installing the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

The retained files under this directory are the source of truth for the worked
example. Output excerpts below are representative and are mechanically checked
against the current example so that the tutorial does not silently drift.

## 1. State one bounded assurance question

**Goal:** decide exactly what is being examined before selecting risks or running
tools.

For this tutorial, the question is:

> What does a schema-valid TRQP authorization response establish, and what remains
> to be demonstrated before relying on authority or time?

The examination includes:

- authorization-response field requirements;
- the relationship between requested time and evaluated time in retained examples;
- a small set of constructed positive and negative response fixtures.

It excludes:

- live endpoints and service behavior;
- transport security and recognition chains;
- delegation and revocation behavior;
- systems-of-record design;
- full TRQP conformance;
- governance approval or residual-risk acceptance.

**Interpretation:** a bounded question prevents a successful schema or replay check
from being misrepresented as a broader assurance conclusion.

**Do not infer:** that an excluded behavior is safe merely because this examination
does not test it.

## 2. Identify affected people, contexts and plausible harm

**Goal:** identify why the question matters before choosing risk hypotheses.

Use a deliberately modest scenario. A relying party receives an authorization
response and may use it to decide whether an issuer is permitted to perform an
action now or at a requested historical time.

Ask:

1. Who relies on the response?
2. Who can be affected if the response is interpreted incorrectly?
3. What happens if stale or structurally valid evidence is treated as current
   authority?
4. Who is least able to detect or contest an incorrect decision?

For this example, plausible harm is a false trust decision: an action could be
allowed because a schema-valid response is treated as proof of authority that the
response structure itself does not establish.

This is a **hypothesis about a bounded scenario**, not evidence that such harm has
occurred in a deployment.

**Next step:** pin the exact specification bytes that will be examined.

## 3. Pin the target to an immutable source revision

**Goal:** make the assessment subject reproducible.

The review record identifies:

```yaml
target:
  repository: trustoverip/tswg-trust-registry-protocol
  revision: 6863733878f3657e05f70764bb474a9fb918de9a
  artifact: specification/v2-approved/core
  version_label: v2-approved source snapshot
```

The [source manifest](source-manifest.json) records the retained files, their
upstream paths, Git blob identifiers and SHA-256 digests.

Do not replace the full revision with a mutable branch such as `main`. A branch
name cannot identify the exact source state that was reviewed.

**What source integrity establishes:** the local retained bytes agree with the
manifest used by this example.

**What it does not establish:** publisher authenticity, current upstream state, or
the truth of any statement in those files.

## 4. Select bounded risk hypotheses

**Goal:** state what could be wrong without expanding the canonical DTG risk corpus.

This example uses two local hypotheses in [risks.yaml](risks.yaml):

- `RK-AU01`: structure can be mistaken for authority;
- `RK-TM01`: time semantics can be confused across requested and action time.

These identifiers belong to this example-local risk source. They are not additions
to the canonical `data/risks.yaml` corpus and do not represent accepted risk
scores or demonstrated incidents.

The hypotheses follow from the assurance question:

```text
schema-valid response
        |
        +--> does structure prove authority?       RK-AU01
        |
        +--> does a time-labelled response prove
             authority at the relevant moment?     RK-TM01
```

**Do not infer:** that every review must create new risks. Reuse an existing risk
when it already expresses the proposition accurately. Use a bounded local source
only when the review needs a hypothesis that is not part of the canonical instance.

## 5. Replay the retained observations

**Goal:** reproduce the source and fixture checks before reading the conclusions.

Run:

```bash
python3 review/examples/standalone-trqp/replay.py --check
```

Representative output:

```json
{
  "source_integrity": "verified",
  "cases": [
    {
      "id": "minimal-required-fields",
      "schema_valid": true
    },
    {
      "id": "missing-authority-negative-control",
      "schema_valid": false
    },
    {
      "id": "historical-response-without-provenance",
      "schema_valid": true
    }
  ],
  "api_example": {
    "requested_time_matches": false,
    "schema_valid": true
  },
  "https_example": {
    "requested_time_matches": true,
    "schema_valid": true
  },
  "runtime_authorization": "not-assessed",
  "authority_history": "not-assessed",
  "overall_assurance": "review-required"
}
```

The complete retained result is
[expected-replay.json](expected-replay.json). `--check` fails if fresh execution
differs from that file.

### Read the observations, not just the exit code

| Observation | What it establishes | What it does not establish |
| --- | --- | --- |
| Minimal response is schema-valid | Required structure is sufficient for this schema check | The values are true or authoritative |
| Response without `authority_id` is invalid | The negative control exercises a required-field boundary | All authority semantics are enforced |
| Historical response without provenance is valid | Schema validity does not require authority-history provenance | TRQP is defective or a deployment lacks such provenance |
| API example is valid but requested time differs from query | Schema validity and query/response semantic agreement are separate | A live service behaves this way |
| HTTPS example preserves requested time | One retained source example preserves the comparison | All examples or deployments do |

The third case is intentionally important: a **PASS at the schema layer** can still
leave the assurance proposition unresolved.

## 6. Inspect the real source observation

**Goal:** connect machine output back to retained specification text.

The replay extracts the first authorization query and response examples from the
retained API and HTTPS documents. It observes:

```text
API example
query time:              2025-06-19T11:30:00Z
response time_requested: 2025-06-25T00:42:00Z
schema valid:             true
requested time matches:  false

HTTPS example
schema valid:             true
requested time matches:  true
```

The reasoning chain is:

```text
retained source
     |
     v
machine observation
     |
     v
reviewer inference
     |
     v
finding
     |
     v
proposed control plane
```

The machine observation is not itself the finding. It is evidence available to a
reviewer.

## 7. Read the review record

**Goal:** see how the bounded findings are represented in the upstream review
contract.

Open [review.yaml](review.yaml). The two findings are:

```yaml
- id: F-001
  summary: Schema-valid authorization does not demonstrate authority history or current permission.
  risks:
  - RK-AU01
  - RK-TM01
  control_plane: implementation-guidance
  status: open

- id: F-002
  summary: The retained API authorization example does not preserve the queried historical time.
  risks:
  - RK-TM01
  control_plane: specification
  status: open
```

Three distinctions matter.

### Finding status is not the control plane

`status: open` says treatment is still owed.

`control_plane` says where treatment belongs. F-001 does not automatically become
a TRQP specification requirement merely because the review found an evidentiary
gap. F-002, by contrast, concerns a retained specification example and therefore
points to the specification control plane.

### A finding is not a governance decision

The review can propose treatment. It cannot grant authority to change TRQP or accept
residual risk.

### A valid review is not target assurance

The review contract makes the assessment reproducible. It does not turn an open
finding into a PASS.

## 8. Bind evidence to each finding

**Goal:** preserve which observations support which reviewer inference.

Open [evidence.json](evidence.json). It is an example-local sidecar, not a general
RAHP evidence standard.

For F-002, the sidecar links:

```text
F-002
 |
 +--> E-002  retained response schema
 +--> E-003  retained API source
 +--> E-004  retained HTTPS source
 +--> E-007  replay result: API requested time mismatch
 +--> E-008  replay result: API response schema-valid
 +--> E-009  replay result: HTTPS requested time match
```

The same record then keeps four human-review concepts separate:

- **observation:** what the retained source or replay shows;
- **inference:** what the reviewer concludes from it;
- **limitations:** what was not examined or cannot be established;
- **treatment:** what evidence or action should come next.

This separation is central to RAHP. Evidence can be intact while an inference is
wrong. A competent reviewer must be able to challenge the inference without losing
the underlying observation.

## 9. Validate the review record

**Goal:** verify that the review is structurally valid and that its selected risk
references resolve in the intended local source.

Run:

```bash
python3 review/validate_spec_review.py review/examples/standalone-trqp/review.yaml --risks review/examples/standalone-trqp/risks.yaml
```

Expected output:

```text
PASS: review/examples/standalone-trqp/review.yaml
```

A PASS here means that the review satisfies the current upstream record contract,
uses an immutable target revision, and resolves its risk references in the supplied
risk source.

It does **not** mean that the findings are correct or resolved.

## 10. Validate the composed examination

**Goal:** rerun the retained observations and validate their bindings to the review
and evidence sidecar.

Run:

```bash
python3 review/examine.py
```

Expected result:

```json
{
  "assessment_id": "SR-001",
  "validation": "complete",
  "scope": "retained source and constructed response fixtures only",
  "overall_assurance": "review-required",
  "unassessed": {
    "authority": "not-assessed",
    "delegation": "not-assessed",
    "revocation": "not-assessed",
    "runtime_authorization": "not-assessed"
  },
  "findings": 2
}
```

Read the two status fields separately:

```text
validation: complete
overall_assurance: review-required
```

That is not contradictory. The first describes the integrity of this bounded
examination package. The second says the target assurance question still has open
findings and unassessed behavior.

## 11. Exercise a fail-closed case

**Goal:** see what rejection looks like rather than learning only the successful
path.

The repository retains an intentionally invalid review whose target revision is
`main` instead of an immutable commit.

Run:

```bash
python3 review/validate_spec_review.py review/examples/invalid-mutable-revision.yaml
```

Expected result:

```text
ERROR: schema target.revision: 'main' does not match '^[0-9a-fA-F]{40}$'
FAIL: 1 problem(s)
```

The nonzero result is expected. The validator does not silently reinterpret a
mutable branch as an acceptable review target.

Other failures in this example are also fail-closed: missing retained source,
digest disagreement, malformed evidence bindings, unresolved selected risks or a
fresh replay that differs from the retained expected output all prevent a successful
examination result.

## 12. Interpret the completed exercise

At this point the mechanically established state is:

```text
retained source identity:        reproduced
fixture/schema observations:     reproduced
review record:                   valid
risk references:                 resolved in selected local source
evidence bindings:               valid
findings:                        2 open
runtime authorization:           not assessed
authority history:               not assessed
overall assurance:               review-required
```

This is a successful RAHP exercise because uncertainty remains explicit.

Do not rewrite the conclusion as:

```text
TRQP passed RAHP
```

or:

```text
TRQP failed RAHP
```

Neither statement is supported by the bounded evidence.

## 13. Reassess after material change

**Goal:** preserve historical evidence instead of silently moving the assessment
boundary.

If the TRQP source changes materially:

1. pin the new immutable target revision;
2. retain this examination as evidence about the old revision;
3. create a new review record for the new revision;
4. rerun the relevant observations;
5. reassess each finding;
6. record whether a finding persists, is resolved, is superseded or requires new
   treatment.

Conceptually:

```text
TRQP revision A
      |
      v
    SR-001
   /      \
F-001    F-002
 open     open

TRQP revision B
      |
      v
    SR-002
   /      \
F-001    F-002
 open    resolved or superseded
```

Do not edit SR-001 so that it appears to have reviewed revision B.

For a second retained-source example of this pattern, see the
[VRC v0.3 examination](../vrc-v03/README.md).

## What to carry into your own assessment

When replacing TRQP with another target, preserve the sequence:

```text
1. bound the assurance question
2. identify affected people, contexts and plausible harm
3. pin the exact source state
4. select justified risk hypotheses
5. produce observations
6. separate observation from inference
7. record findings and control planes
8. bind evidence
9. validate structure and references
10. exercise important failure behavior
11. interpret what remains unknown
12. reassess after material change
```

The objective is not to maximize the number of RAHP records. It is to make a
bounded assurance argument reproducible, falsifiable and reviewable.

## Continue

- [Technical reference for this retained TRQP example](README.md)
- [Specification pressure-testing workflow](../../../docs/pressure-testing-a-spec.md)
- [Review-record contract](../../README.md)
- [Adopting RAHP](../../../ADOPTION.md)

AI-assisted documentation preparation. The commands and retained outputs are
mechanically checked; methodological interpretation and acceptance remain subject
to independent human review.
