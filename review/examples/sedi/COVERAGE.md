# Complete requirement coverage

The register is an index into documentary examination records, not a second copy of the source requirements. The retained archive and Annex A index define the exact universe (142 IDs). Every ID has one primary register entry. Additional source observations and case bindings may be many-to-many.

## Status and disposition

- `indexed`: only index identity established. No examination reference or disposition; must name an outstanding work package.
- `examined`: a substantive documentary record exists, with source page/digest, authority and actors, numbered objectives, method applicability, protection, risk relevance, dependencies and evidence limitations. Initial imported entries point to the previous thematic records; gaps in their normalized fields must be reconciled during consolidation.
- `scenario-examined`: additionally bound to one or more relevant constructed scenarios with explicit risk and evidence propositions. Do not assign from a requirement ID match alone.
- Accountable review is a separate field; no author-side promotion to reviewed status.

Dispositions describe documentary conclusions, not governed RAHP finding status: addressed-in-design, partially-addressed, decision-dependent, evidence-required, clarification-required, gap-identified, indeterminate, out-of-scope (with explicit rationale). The imported 46 use conservative evidence-required because operational effectiveness is unestablished; this is not a statement that the guide lacks a protection. Indexed entries have no disposition.

## Work packages

WP-A: BOR (5 remaining); WP-B: PRG/GOV/PRC/ENF (17); WP-C: APP/IDP (16); WP-D: SDI/CRY/PRV/KMS (24); WP-E: WAL/VER/RPY (27); WP-F: ORG (organizational security, 7). Counts describe the initial outstanding set and remain stable as planning provenance.

For each newly examined requirement, retain the precise source reference, authority reference as stated in the guide, actors, objective numbers and substantive properties, AUTO/EXPT/ADMN applicability and limitations, relevant risks or reasoned non-applicability, existing protection, material dependencies and proposed evidence. Record an explicit disposition and rationale. Reuse cases where adequate; add cases only for a distinct material failure proposition. Do not infer a statutory conclusion or operational effectiveness.

## Mechanical checks

Run from repository root:

```sh
python3 review/examples/sedi/check_coverage.py
python3 review/examples/sedi/check_coverage.py --require-complete
python3 -m unittest discover -s tests -p 'test_sedi_coverage.py'
```

The first command checks exact index coverage and record references, and reports outstanding examination work. The second must fail while any indexed requirement remains. It is a documentary completeness gate, not an assurance verdict. It does not evaluate the truth or adequacy of author judgments. The final consolidation must normalize existing records and independently review coverage quality before declaring completion.
