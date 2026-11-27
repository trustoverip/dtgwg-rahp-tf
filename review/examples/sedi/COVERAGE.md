# Complete requirement coverage

The register is an index into documentary examination records, not a second copy of the source requirements. The retained archive and Annex A index define the exact universe (142 IDs). Every ID has one primary register entry. Additional source observations and case bindings may be many-to-many.

## Status and disposition

- `indexed`: only index identity established. No detailed examination reference or primary register disposition; the register identifies the outstanding assessment activity. A separate source-gap record can retain a reasoned clarification-required disposition without asserting detailed examination.
- `examined`: a substantive documentary record exists, with source page/digest, authority and actors, numbered objectives, method applicability, protection, risk relevance, dependencies and evidence limitations. Initial imported entries point to the previous thematic records; the derived view reconciles their analytical fields using the legacy limitation record, existing case and bounded review bindings and selected objective-control mappings. An explicit undeclared source method remains a gap, not N/A.
- `scenario-examined`: additionally bound to one or more relevant constructed scenarios with explicit risk and evidence propositions. Do not assign from a requirement ID match alone.
- Accountable review is a separate field; no author-side promotion to reviewed status.

Dispositions describe documentary conclusions, not governed RAHP finding status: addressed-in-design, partially-addressed, decision-dependent, evidence-required, clarification-required, gap-identified, indeterminate, out-of-scope (with explicit rationale). The imported 46 use conservative evidence-required because operational effectiveness is unestablished; this is not a statement that the guide lacks a protection. Indexed entries have no detailed-examination disposition in the primary register. IDP-08 has a separate source-gap disposition, which is not a promotion to examined status.

## Assessment domains

The register preserves historical planning identifiers for individual rights; programme governance, processing restrictions and enforcement; application and identity proofing; credential architecture and technical security; wallet, verifier and relying-party interactions; and organisational security. These identifiers are stable data references, not a measure of current assessment completion.

For each detailed requirement examination, retain the precise source reference, authority reference as stated in the guide, actors, objective numbers and substantive properties, AUTO/EXPT/ADMN applicability and limitations, relevant risks or reasoned non-applicability, existing protection, material dependencies and proposed evidence. Record an explicit disposition and rationale. Reuse cases where adequate; add cases only for a distinct material failure proposition. Do not infer a statutory conclusion or operational effectiveness.

## Mechanical checks

Run from repository root:

```sh
python3 review/examples/sedi/check_coverage.py
python3 review/examples/sedi/check_coverage.py --require-complete
python3 -m unittest discover -s tests -p 'test_sedi_coverage.py'
```

The first command checks exact index coverage and record references, and reports outstanding examination work. The second also derives the normalized analytical view and rejects indexed-only records and unresolved required fields. The integrated consumer supports the same strict gate with `consolidate.py /path/to/retained.zip --require-complete`. Current strict failures are IDP-08 (no detailed section) and INT-04 (ADMN undeclared). A valid documentary disposition may remain open pending operational evidence or review; strict completeness is not risk acceptance or an assurance verdict. Independent review of source interpretation and analytical judgment remains necessary.
