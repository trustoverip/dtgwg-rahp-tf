# Reproducing and reviewing the SEDI assessment

This is a worked documentary assessment, not a deployment audit or an approved RAHP review. Obtain the contributor-supplied ZIP through an authorized channel; it is not redistributed here. The publisher collections are listed in [archive-manifest.json](archive-manifest.json). Independently downloading the same titles may yield different bytes and does not reproduce this baseline.

## Run from the repository root

Install the repository requirements, then run:

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -p 'test_sedi*.py'
python3 review/examples/sedi/verify_archive.py "/path/to/SEDI RAHP Review Input.zip"
python3 review/examples/sedi/examine.py "/path/to/SEDI RAHP Review Input.zip"
python3 review/examples/sedi/consolidate.py "/path/to/SEDI RAHP Review Input.zip"
python3 review/examples/sedi/check_coverage.py --require-complete
python3 review/examples/sedi/consolidate.py "/path/to/SEDI RAHP Review Input.zip" --require-complete
```

The archive commands require the exact ZIP (SHA-256 in the manifest). A missing or modified input must fail; do not substitute a new digest to obtain success. Expected bounded service-equivalence examination output includes 21 verified members, four candidate findings, seven scoped requirements, 32 mapped objectives, candidate_validation complete, formal_review not-established, overall_assurance review-required. The consolidated examination reports 141 detailed examinations of 142 indexed requirements, 703 objectives, 31 local hypotheses, 47 constructed cases and twelve open review propositions. Both strict completeness commands intentionally reject IDP-08 (missing detailed section) and INT-04 (undeclared administrative verification applicability). These checks do not authenticate a publisher release or establish service performance.

## Independently challenge the service-equivalence reasoning

1. Read Part 1 PDF pages 9–14 and 24–26 and Part 3 pages 61–63, 93–97 and 100–102 (one-based PDF pages, not printed page labels). Check the seven requirements and objective numbers in the inventories.
2. Compare [objective controls](objective-controls.json), [cases](cases.json) and [candidate findings](review-candidate.json). Check that source observations, proposed treatment, candidate guardrails and evidence-generating activities are not conflated. The mapping is grouped by requirement, not a claim that each individual objective has an independently proven treatment.
3. Inspect the role matrix and identify who is responsible for treatment. GOV-05 is an exemption from accepting SEDI, not authorization to compel SEDI. Examine whether the stated legal or feasibility grounds and remedies are adequate; the supplied toolkit statute is an extract.
4. Record agreement or challenge per finding with exact source references, identity of the accountable reviewer and rationale. Do not enter a reviewer into the candidate merely to make it a formal review. A non-Git representation needs Task Force agreement.
5. Reassess on source revision, rulemaking, material service workflow change, new evidence of disparity or complaint resolution, or change in RAHP method. Retain the previous baseline and record which findings are affected.

## Interpreting results

Structural validation establishes archive integrity and consistency of evidence references, not whether the referenced passages substantiate the conclusion. Constructed scenarios are not observed service events. No operational evidence, guardrail verification, risk acceptance or conformity conclusion is claimed. For the broader assessment, follow the [review handover](REVIEW-HANDOVER.md), which explains how to examine all documentary records, source limitations and consolidated recommendations. Independent review of both the bounded example and broader assessment remains outstanding.
