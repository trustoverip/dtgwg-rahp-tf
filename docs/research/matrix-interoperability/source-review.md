# Source-derived RAHP review (limited)

This review exercises the existing `rahp-spec-review/v1` contract against the **pinned Matrix README**, not the Matrix spreadsheet or a deployed fiduciary agent. This is a source/documentary examination and should not be represented as a completed Matrix campaign or interoperable workbook translation.

## Reproduce

From upstream repository root (dependencies installed):

```sh
python3 review/validate_spec_review.py docs/research/matrix-interoperability/matrix-source-review.yaml --risks docs/research/matrix-interoperability/risks.yaml
```

The review asks two questions supported by exact source statements:

- **F-001**: The Matrix README states that the workbook does not claim validated native RAHP schema compatibility or execution by a RAHP engine. Therefore this research cannot claim native interchange, and a real workbook row-level conversion remains necessary.
- **F-002**: The README's section “Example: Permission Is Withdrawn Before Execution” gives positive, negative and adversarial examples and explicitly distinguishes documented gate refusal from independent evidence of booking execution. This is a scenario design, not tested behavior of a deployed target.

Assessment `SR-390` identifies the Matrix repository revision and two *example-local* research hypotheses. Successful RAHP schema validation checks structural representation only. It does not verify source publisher authenticity, workbook semantics, completeness of evidence, adequate review, or operational enforcement. The findings remain **open**.

The local `evaluate.py` exercise in this directory is a separate synthetic scenario experiment. Its PASS and FAIL outcomes are not findings about the real Matrix, RAHP implementation, or any actual booking system.

## Scope of lifecycle experiment

The synthetic baseline has permission active; a material change revokes that permission. The baseline permission record remains historically relevant but is stale for new execution; cached approvals contradicted by later revocation must not authorize new actions. A complete RAHP reassessment needs separate source- and time-bound historical and reassessed review records. These do not yet exist; it would be misleading to fabricate a deployment revision or an observed execution trace.

## Source traceability

Pinned Matrix reference: https://github.com/trustoverip/aimwg-agent-fiduciary-duties/blob/140b558791bab5bacdbe5245df0aada93d2b27bd/Assurance%20Matrix/README.md

Relevant headings: **Purpose**, **Turn Draft Scenarios into Executable Tests**, **Record Complete Evidence and Adjudicate the Result**, **Example: Permission Is Withdrawn Before Execution**, **Reassessment, Repair, and History**.

The linked live spreadsheet and full WLA paper remain unverified inputs. This is not a substitute for their inspection.
