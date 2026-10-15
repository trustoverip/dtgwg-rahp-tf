# Retained-source TRQP examination

This bounded exercise asks: what does a schema-valid TRQP authorization response
establish, and what remains to be demonstrated before relying on authority or time?
It runs offline after dependency installation, using this repository alone.

## Source and method identity

Target: `trustoverip/tswg-trust-registry-protocol` at
`6863733878f3657e05f70764bb474a9fb918de9a`, v2-approved source snapshot.
[The manifest](source-manifest.json) retains immutable URLs, upstream paths,
Git blob identifiers and SHA-256 digests for six unmodified source files.
Digest agreement proves consistency with the supplied manifest, not source authenticity.
The source's API insertion path names `v2`; the manifest's supplementary
`insert_schema` entry records the downstream comparison with the same blob in
`v2-approved`. That supplementary assertion is not a locally replayed check.

Method baseline: `trustoverip/dtgwg-rahp-tf` at
`ab191485b48bca805ea2cc962c2ea9476a65db66`, specifically the existing review
schema and validator. The new helper/replay implementation is identified by the
contribution commit containing this example; record its Git SHA when retaining
execution evidence. Adapted from downstream `rahp-toolkit` at
`af58247e83d0aff4d47650d929bfc6280d9e41d3`,
`examples/standalone-trqp/replay.py`, fixtures and retained source.
Preparation and adaptation were AI-assisted.

## Reproduce

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 review/examples/standalone-trqp/replay.py --check
python3 -m unittest discover -s tests
```

The replay verifies source identity before extracting the first two authorization
HTTP blocks from the API and HTTPS documents. It validates constructed responses
against the unchanged response schema, including date-time format checking, and
compares query time with response `time_requested`. `--check` compares the complete
result with [expected-replay.json](expected-replay.json). A mismatch or execution
error exits nonzero. Successful reproduction is not target assurance success.
The retained schema has no dialect declaration; `jsonschema` selects its default
validator. This checks the exercised keywords, not full dialect conformance.

| Evidence | Expected observation | Interpretation boundary |
| --- | --- | --- |
| Minimal constructed response | Schema-valid | Required fields are present; their truth is untested |
| Constructed response without authority | Schema-invalid | Negative control for required fields |
| Constructed historical response without provenance | Schema-valid | Schema validity does not demonstrate authority history |
| API source example | Schema-valid, query-time mismatch | Semantic agreement needs a separate check |
| HTTPS source example | Schema-valid, query-time match | A contrasting source example, not service traffic |

All three [response fixtures](cases.json) are constructed teaching inputs.
The API and HTTPS examples come from the retained source. Source integrity,
schema validity, semantic observations and assurance conclusions are separate.
Runtime authorization and authority history remain `not-assessed`; overall
assurance remains `review-required`. Delegation and revocation behavior, live
endpoints, recognition chains, transport security, governance approval and full
TRQP conformance are outside this replay.

Tests deliberately falsify integrity and fixture assumptions: altered/missing
source, traversal, symlinks, duplicate entries, removed required entries,
malformed identity/digests/URLs, malformed HTTP blocks, wrong expected results,
and malformed/duplicate response cases.

## Attribution

Retained source is the Trust over IP Foundation's TRQP source at the revision
above. Original [license](source/LICENSE.md.txt) and
[copyright policy](source/COPYRIGHT_POLICY.md.txt) remain applicable.
The `.txt` suffix preserves source bytes without publishing its Markdown directives
as RAHP documentation. This examination implies no specification-owner endorsement.
See [review documentation](../../README.md) for the existing assessment contract.

## Bind observations to the assessment

Increment 2 uses the unchanged upstream [review schema](../../spec-review.schema.json)
and `validate_spec_review.py::validate_record`. The assessment lives in
[review.yaml](review.yaml); evidence and reasoning live separately in
[evidence.json](evidence.json), validated against [evidence.schema.json](evidence.schema.json).
No undocumented members are added to the review format.

```bash
python3 review/validate_spec_review.py review/examples/standalone-trqp/review.yaml --risks review/examples/standalone-trqp/risks.yaml
python3 review/examine.py
```

The adapter uses the installed TRQP evaluator, never code supplied by an input
bundle. `--example PATH` accepts another retained TRQP bundle in this same
experimental layout; it is not a general specification/plugin execution interface.
All paths resolve inside that bundle with traversal and symlinks rejected.

The result distinguishes `validation: complete` from
`overall_assurance: review-required`. Missing evidence, malformed records,
contradictory observations and execution failures produce a nonzero exit and no
success report. Authority, delegation, revocation and runtime authorization remain
explicitly `not-assessed`. Findings remain open, with independent review pending.

### Example-local binding contract

| Member | Meaning and check |
| --- | --- |
| `assessment_id`, `target`, `method_revision` | Must agree with review identity, retained target and explicit method baseline |
| `review_binding`, `risks_binding` | Relative paths and SHA-256 bind exact review bytes and selected corpus |
| `execution` | Must be complete and match a fresh replay and retained expected output |
| `evidence` | Unique IDs; file paths/digests and optional inclusive 1-based line ranges, or RFC 6901 pointers to fresh replay results with expected values |
| `findings` | Exactly one entry per review finding, nonempty evidence references, observation, inference, limitations, proposed treatment and reasoning for each selected risk |
| `unassessed` | Fixed explicit exclusions; cannot relabel absent runtime evidence as verified |

`source` evidence must belong to the verified manifest; `artifact` evidence binds
constructed inputs; `result` evidence selects an observation from fresh output.
Every finding must have resolvable references. These checks establish structural
coverage and consistency, not whether the cited evidence supports the inference.
Reviewers must challenge the reasoning itself. An attacker rewriting both retained
bytes and their manifests/digests can construct a consistent bundle; this adapter
does not authenticate the publisher or provide a trusted signature.

[risks.yaml](risks.yaml) contains **two example-local hypotheses**, selected via
the existing `--risks` interface. RK-AU01 examines structure mistaken for authority;
RK-TM01 examines time confusion. These identifiers are local to this example, not
additions to the canonical DTG corpus, scored risks, accepted risks or demonstrated
deployment incidents. The sidecar explains each mapping. No downstream CRK
identifiers, pressure-test statuses or controllers are imported.

F-001 requests deployment policy and authority/revocation evidence; it does not
infer that TRQP must prescribe storage or add response fields. F-002 requests
editor clarification of the retained API example at another immutable revision.
A successful replay cannot close either finding.

The sidecar deliberately remains example-local until a second examination tests
reuse. Alternatives were extending the strict review schema or importing the
downstream pressure-test contract; both would expand semantic and compatibility
scope prematurely. Existing review records and commands remain valid.

When source, review, selected risks or fixtures change, retain the earlier bundle
and reassess; do not silently reuse the old evidence. Updating digests is an
explicit new binding, not proof that old conclusions still apply. Capture the
implementation Git SHA and dependency versions with any exported execution result.
Increment 3 will consolidate vocabulary/validation; Increment 4 and pending CI
PR #14 will establish the supported repository CI path. This example adds no
duplicate workflow and claims no independent adopter qualification.
