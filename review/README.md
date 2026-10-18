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


## Combined validation (Increment 3; proposed)

Use `python3 tools/validate_all.py` for corpus integrity and vocabulary
consistency. A review is **not** implicitly selected: add `--review` once per
record you want checked:

```sh
python3 tools/validate_all.py --review review/examples/minimal-review.yaml
python3 tools/validate_all.py --review review/examples/standalone-trqp/review.yaml --risks review/examples/standalone-trqp/risks.yaml
python3 tools/validate_all.py --strict
python3 -m unittest discover -s tests
```

The default risk corpus for review references is `--data/risks.yaml`.
`--strict` retains the existing corpus validator's warning policy.
An absent review means that no review record was validated; it is not
evidence of a successful examination. Review records, risk IDs and the
existing standalone `tools/validate.py` and `review/validate_spec_review.py`
commands remain supported.

Review vocabulary authority is now in `method/vocabularies.yaml` (#27).
This composed validator checks all defined vocabulary lists for structural
validity and duplicate values. The dedicated review validator enforces
schema parity for each explicitly selected review. The lifecycle and
risk-acceptance semantics in #26 remain separate follow-up work.

Corpus warnings, review schema failures and unresolved risk references are
reported by their existing validators; a failure of either component produces
a nonzero exit status. This is repository validation, not target assurance.
