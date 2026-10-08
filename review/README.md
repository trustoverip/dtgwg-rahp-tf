# RAHP specification review records

This directory contains the first machine-verifiable contract for reproducible
specification pressure-testing.

- `spec-review.schema.json` defines the record format.
- `validate_spec_review.py` validates the schema, finding identifiers and RAHP risk references.
- `examples/minimal-review.yaml` is a small worked fixture.
- [Worked adoption](examples/worked-adoption/README.md) is a fictional two-version review with explicit evidence, disposition and reassessment boundaries.

Start with [`docs/pressure-testing-a-spec.md`](../docs/pressure-testing-a-spec.md)
for the review workflow.

This capability is intentionally bounded. It does not implement the downstream
RAHP assurance controller, specialist routing, terminal assurance state machine or
continuous reassessment machinery. A valid review record means that the review is
well-formed and reproducibly source-pinned; it does not mean that the target has
passed assurance.

## Evidence-linked retained-source example

[The standalone TRQP walkthrough](examples/standalone-trqp/README.md) adds an
offline real-source replay and an experimental example-local evidence sidecar.
`python3 review/examine.py` reruns that bounded evaluator and validates the
source/review/evidence bindings. It emits `validation: complete` only after all
checks succeed, while retaining `overall_assurance: review-required`.
The existing review schema and validator are unchanged. The sidecar is not a
standardized RAHP evidence contract and adds no members to existing review records.
