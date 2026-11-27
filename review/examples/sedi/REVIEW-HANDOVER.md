# SEDI review handover (author-side candidate)

## Scope and evidence

The retained ZIP is the source baseline, not a publisher-authenticated release. 141 of 142 requirements have documentary records (703 numbered objectives); IDP-08 lacks its detailed section. The 31 local hypotheses and 47 constructed cases are analytical instruments, not observed incidents. The original 46 records still have explicit normalization gaps. Source interpretation has not been independently corroborated.

## Consolidated examination

The consumer derives candidate propositions from each constructed case, not new independently established findings. It retains source record, requirement references, risk, evidence request and available authority. Operational evidence is absent. The original SEDI-01 review candidate remains a separate bounded example using existing finding semantics. Do not promote the broader candidate index into a formal review record.

## Method applicability

The exercise demonstrates author-side reuse of risk/harm reasoning, constructed cases, source-bound evidence, and separation of controls and guardrails. It exposes a source-contract mismatch: the existing Git-oriented target requires a commit and blob provenance; a local ZIP digest establishes retained bytes but not publisher identity. Retain the example-local contract; a shared non-Git contract requires Task Force decision. A second limitation is that per-component and per-method conformance cannot substitute for cross-actor evidence. No canonical DTG changes are warranted.

## Reproduce

From repository root, install repository requirements, then run:

```sh
python3 review/examples/sedi/consolidate.py /path/to/retained.zip
python3 review/examples/sedi/check_coverage.py --require-complete
python3 -m unittest discover -s tests -p 'test_sedi*.py'
```

The strict completeness command must fail for IDP-08. The composed result must remain review-required. CI tests use a fixture for the archive boundary; actual archive execution is separate. Obtain the exact archive from its contributor with appropriate permission; do not assume public redistribution is authorized.

## Remaining gates

- Reconcile missing metadata and source interpretation, including original 46 records.
- Resolve or explicitly retain IDP-08 through publisher clarification and Task Force disposition.
- Qualify candidate treatment authorities and control planes and consolidate substantive findings; do not equate all constructed cases with findings.
- Execute exact archive consumer and negative cases; retain actual evidence.
- Identify independent reviewers, record objections and disposition, agree publication/communication.
- Reassess after changes to retained source, governing rules, profile or implementation, or new evidence.

No operational assurance, risk scoring, risk acceptance, legal conclusion or independent review is asserted.
