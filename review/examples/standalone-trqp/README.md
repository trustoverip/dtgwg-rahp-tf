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
