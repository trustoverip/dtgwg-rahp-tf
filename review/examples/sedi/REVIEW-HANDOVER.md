# SEDI review handover (author-side candidate)

## Scope and evidence

The retained ZIP identifies the source bytes, not a publisher-authenticated release. The coverage register accounts for all 142 Annex A identifiers. There are 141 detailed examinations and 703 numbered objectives. IDP-08 lacks its detailed section; INT-04 has no declared ADMN applicability. The 31 example-local hypotheses and 47 constructed cases are analytical instruments, not observed incidents. All original analytical normalization omissions have been addressed in the derived view; the two remaining normalization gaps are source-dependent. See [acceptance evidence](ACCEPTANCE-EVIDENCE.md) for the executed checks and acceptance boundaries.

## Examine and review

[Legacy analytical reconciliation](legacy-analysis.json) records requirement-specific limitations and ten justified affected-context groups covering all 47 cases. The normalized view retains explicit risk-relevance bases, harms, associated cases, related requirements, evidence needs and documentary dispositions. The seven [selected objective-control mappings](objective-controls.json) cover 32 objectives; the remaining objectives are inventoried and examined at requirement level, not represented as individually executed assurance tests. Case-derived risk associations are contextual; co-examination does not establish a normative dependency. The [synthesis](synthesis.json) separates twelve open documentary observations, interpretations, design protections, proposed treatment authorities, recommendations and resolution evidence. The consumer derives their source references. The original SEDI-01 candidate remains a bounded example using existing finding semantics. Do not treat the broader synthesis as an accepted formal review or the proposed treatment authorities as risk-acceptance authorities.

## Method applicability

The exercise demonstrates reuse of risk/harm reasoning, source-bound evidence, constructed scenarios, controls and guardrails, and existing validation and finding semantics. It exposes a source-contract mismatch: the Git-oriented review target requires commit and blob provenance; a ZIP digest establishes retained bytes but not publisher identity. The example-local representation preserves this distinction and avoids weakening the canonical contract. No shared method change is warranted by this bounded exercise; a general non-Git review target contract requires separate Task Force consideration. Per-component and per-method conformance cannot establish cross-actor protection; the existing method accommodates interaction cases and qualified evidence without changing canonical DTG records.

## Reproduce

From repository root, install repository requirements, obtain the exact contributor-supplied archive with appropriate permission, then run:

```sh
python3 review/examples/sedi/verify_archive.py '/path/to/retained.zip'
python3 review/examples/sedi/normalize_coverage.py
python3 review/examples/sedi/consolidate.py '/path/to/retained.zip'
python3 review/examples/sedi/examine.py '/path/to/retained.zip'
python3 -m unittest discover -s tests -p 'test_sedi*.py'
python3 review/examples/sedi/check_coverage.py --require-complete
python3 review/examples/sedi/consolidate.py '/path/to/retained.zip' --require-complete
```

The normal examination paths pass and retain review-required status. The last two commands intentionally exit nonzero on IDP-08 and INT-04. The strict gate also rejects missing analytical fields. CI exercises the regression suite; actual retained-source replay is separate and its evidence is recorded in the acceptance audit. Source bytes are not redistributed. A fresh capture is not interchangeable with this archive.

An independent reviewer can follow each normalized record to its primary examination and cited PDF pages, compare the heading, role, numbered objectives, method table and parameter coverage with the original, then examine risk relevance, linked cases, proposed evidence and synthesis. Reassess the substantive author interpretations rather than accepting a passing consumer as proof of their correctness.

## Remaining source and governance gates

- Obtain a publisher-qualified detailed IDP-08 section or formally retain the omission. Do not substitute APP-08 or invent objectives.
- Clarify the undeclared INT-04 ADMN method and the documented method/limitation tensions in INT-01, KMS-04, CRY-04 and ORG-04. Preserve the original declarations until qualified.
- Identify accountable reviewers and invite review of the scope, twelve propositions, existing protections, evidence needs, treatment planes and methodological conclusions. Resolve or retain objections and limitations.
- Agree publication and communication disposition, including whether and how to engage the SEDI programme. No engagement is implied by this assessment.
- Reassess after a changed source, governing rule, conformance profile, implementation or new evidence.

The author-side package is prepared for qualified independent review, not for unconditional documentary completeness or assurance. No operational evidence, legal conclusion, risk scoring, risk acceptance, publisher authenticity or accountable review is established.
