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

## Second real-source examination: VRC v0.3

[The VRC v0.3 examination](examples/vrc-v03/README.md) retains the authoritative
task-force source contemporaneous with historical review #6 and a real subsequent
source revision. It demonstrates source-pinned reassessment: one documentary finding
closes after the source changes while a separate residual finding remains open.

The VRC evidence sidecar is also example-local. The
[TRQP × VRC generality checkpoint](examples/vrc-v03/generality.md) identifies the
common evidence-envelope invariants demonstrated by both examples and records why a
shared sidecar schema is still deferred rather than inferred from example mechanics.


## Combined validation (Increment 3)

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

Review vocabulary authority is in `method/vocabularies.yaml`. The composed
validator checks method vocabulary structure; the dedicated review validator
enforces schema parity for explicitly selected review records. Semantic changes
remain deliberate contract changes rather than implementation-side inference.
Corpus warnings, review schema failures and unresolved risk references are
reported by their existing validators; a failure of either component produces
a nonzero exit status. This is repository validation, not target assurance.

## Fail-closed schema dependency (Increment 4)

The corpus validator now stops with a nonzero exit code if `jsonschema` is not
installed. Skipping required schema validation is not a successful integrity
check. Install `requirements.txt` and rerun the full validation suite.
A dedicated negative regression test uses an isolated interpreter to simulate
that missing dependency. This change does not alter the warning policy for
ordinary corpus content or provide any target assurance conclusion.

The repository's accepted validation workflow from #14 owns CI execution
provenance and retained artifacts. It runs the negative regression suite, the
composed corpus/review path and the retained-source TRQP examination. The workflow
summary keeps repository integrity, review validation and target assurance
separate, and the evidence artifact retains the corresponding logs.
