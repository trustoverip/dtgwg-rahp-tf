# Reproducing the first SEDI documentary examination

This is a bounded upstream worked example, not a deployment audit or an approved RAHP review. Obtain the contributor-supplied ZIP through an authorized channel; it is not redistributed here. The publisher collections are listed in [archive-manifest.json](archive-manifest.json). Independently downloading the same titles may yield different bytes and does not reproduce this baseline.

## Run from the repository root

Install the repository requirements, then run:

```sh
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -p 'test_sedi*.py'
python3 review/examples/sedi/verify_archive.py "/path/to/SEDI RAHP Review Input.zip"
python3 review/examples/sedi/examine.py "/path/to/SEDI RAHP Review Input.zip"
```

The archive commands require the exact ZIP (SHA-256 in the manifest). A missing or modified input must fail; do not substitute a new digest to obtain success. Expected examination output includes 21 verified members, four candidate findings, seven scoped requirements, 32 mapped objectives, candidate_validation complete, formal_review not-established, overall_assurance review-required. This is expected output, not a publisher authenticity or service performance claim.

## Independently challenge the reasoning

1. Read Part 1 PDF pages 9–14 and 24–26 and Part 3 pages 61–63, 93–96 and 100–102 (one-based PDF pages, not printed page labels). Check the seven requirements and objective numbers in the inventories.
2. Compare [objective controls](objective-controls.json), [cases](cases.json) and [candidate findings](review-candidate.json). Check that source observations, proposed treatment, candidate guardrails and evidence-generating activities are not conflated. The mapping is grouped by requirement, not a claim that each individual objective has an independently proven treatment.
3. Inspect the role matrix and identify who is responsible for treatment. GOV-05 is an exemption from accepting SEDI, not authorization to compel SEDI. Examine whether the stated legal or feasibility grounds and remedies are adequate; the supplied toolkit statute is an extract.
4. Record agreement or challenge per finding with exact source references, identity of the accountable reviewer and rationale. Do not enter a reviewer into the candidate merely to make it a formal review. A non-Git representation needs Task Force agreement.
5. Reassess on source revision, rulemaking, material service workflow change, new evidence of disparity or complaint resolution, or change in RAHP method. Retain the previous baseline and record which findings are affected.

## Interpreting results

Structural validation establishes archive integrity and consistency of evidence references, not whether the referenced passages substantiate the conclusion. Constructed scenarios are not observed service events. No operational evidence, guardrail verification, risk acceptance or conformity conclusion is claimed. The remaining four thematic areas in #71 require their own scoped examination and independent review.
