# RAHP specification review records

This directory contains the first machine-verifiable contract for reproducible
specification pressure-testing.

- `spec-review.schema.json` defines the record format.
- `validate_spec_review.py` validates the schema, finding identifiers and RAHP risk references.
- `examples/minimal-review.yaml` is a small worked fixture.

Start with [`docs/pressure-testing-a-spec.md`](../docs/pressure-testing-a-spec.md)
for the review workflow.

This capability is intentionally bounded. It does not implement the downstream
RAHP assurance controller, specialist routing, terminal assurance state machine or
continuous reassessment machinery. A valid review record means that the review is
well-formed and reproducibly source-pinned; it does not mean that the target has
passed assurance.
