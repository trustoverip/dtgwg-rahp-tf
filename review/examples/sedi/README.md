# SEDI worked exemplar: foundation

Tracking issue: [#71](https://github.com/trustoverip/dtgwg-rahp-tf/issues/71), following the Task Force decision on 25 November 2026.

**Status: local assessment input baseline established; examination not yet executed.**

This upstream-only exemplar examines whether the SEDI draft's protections remain effective across representative digital identity service interactions. It is separate from the canonical DTG instance and does not depend on downstream tooling.

## Source boundary

See [source inventory](source-inventory.json). The guide describes itself as a working draft interpreting Utah Code Title 63A, Chapter 20; official implementation standards are the Department's responsibility. The inventory identifies 19 guide pages from the overview navigation plus the statutory chapter. The original web discovery inventory is historical. On 27 November 2026 a contributor supplied a locally assembled archive from the [SEDI toolkit](https://sedi.utah.gov/bring-sedi-to-your-state/#kit) and [Implementation Guide](https://sedi.utah.gov/implementation-guide/), in the absence of a formally downloadable publisher payload. See [archive manifest](archive-manifest.json) for exact archive and member digests. All 18 guide PDFs and three toolkit DOCX files were readable. The overview and complete official statutory text are not included. The statutory language DOCX explicitly contains extracts.

The guide labels its build as `08495a8`, dated 22 May 2026, while the introduction's version history dates the initial draft to 19 June 2026. Preserve both labels; do not reconcile them by assumption.

The RAHP baseline used to scope this work is [8f6be0638fc1932abe5713263e26fee3929be147](https://github.com/trustoverip/dtgwg-rahp-tf/commit/8f6be0638fc1932abe5713263e26fee3929be147). The existing `rahp-spec-review/v1` target revision is a full Git commit identity. The existing `review/source_integrity.py` verifies commit-qualified GitHub URLs, blob identity and SHA-256. A short build label or SHA-256 of a web page is not a substitute.

The archive digest identifies the exact assessment input, not a publisher Git revision. Before creating a conforming review record, agree a bounded non-Git target representation with Task Force review or obtain an authoritative Git revision. Retain exact acquired bytes and retrieval metadata where permissible. If redistribution is not permitted, keep source bytes outside the public repository and document the independently obtainable inputs and integrity boundary. A fresh capture cannot be assumed identical to the draft observed on 26 November.

## Local source acquisition

The [source acquisition helper](capture_sources.py) downloads only the inventory's explicitly listed public HTTPS sources to a new directory outside the checkout. It writes a manifest of response-byte SHA-256 digests, URL, media type, size and retrieval time; it rejects redirects, unexpected media types and empty or oversized responses. It does not publish source bytes or claim that a capture corresponds to the historical build. Use a network-enabled workstation with permission to retain the documents:

```sh
python3 review/examples/sedi/capture_sources.py /tmp/sedi-capture
```

The capture is an acquisition record, not a valid `rahp-spec-review/v1` target. Before using it for an assessment, review its content and establish the publisher/version relationship and a suitable upstream source identity contract. Do not commit captured files without confirmed redistribution rights. A repeat acquisition is a distinct observation.

## Initial vertical examination

Question: Can a person who chooses a lawful physical identity format encounter material disadvantage despite a documented physical alternative?

The initial scope is one otherwise eligible individual accessing a government service, with identity format as the variable. The service entitlement, eligibility and transaction purpose are held constant. The Department, service operator and affected individual are the primary roles. Relying parties and health care providers are relevant to BOR-09 but their service-specific obligations and interactions are deferred.

| Requirement | Statutory reference | Initial design proposition |
| --- | --- | --- |
| SEDI-BOR-03 | 63A-20-101(3) | Physical issuance and acceptance remain available. |
| SEDI-BOR-04 | 63A-20-101(4) | The physical alternative is usable without digital enrollment. |
| SEDI-BOR-09 | 63A-20-101(9) | Format choice does not disadvantage the otherwise entitled person. |

Source: [Part 1](https://sedi.utah.gov/implementation-guide/part-1/). Relevant implementation decisions concern acceptance-point review frequency, pathway inventory and permissible channel distinctions. The draft identifies limitations of administrative review, automated platform checks and expert examination; documentary evidence alone cannot establish actual service access. These observations are now traceable to the retained Part 1 PDF (pages 9–14 and 24–26); the local archive manifest identifies its exact bytes.

The [initial requirement inventory](initial-requirements.json) records the three requirement IDs, roles, implementation decision references, objective numbers, verification coverage and evidence categories. The source inventory also records all 18 published requirement domains. Annex A and Annex E are now available. Annex A contains 142 unique requirement IDs, as independently extracted from the PDF. Full role and objective mapping is not yet complete.

### Candidate constructed cases

| Case | Variation | Evidence question |
| --- | --- | --- |
| equivalent-service | Both paths provide equivalent access | What comparative evidence establishes equivalence? |
| unavailable-physical-path | A listed physical path is locally unavailable | Can the inventory and audit detect this? |
| digital-enrollment-condition | Staff require enrollment despite documented fallback | Can operational controls detect and remedy informal compulsion? |
| unequal-service | Physical format incurs a material delay or additional burden | How do permitted channel distinctions and operational measurements establish whether the burden is discriminatory? |
| evidence-missing | Policy claims parity but comparable service evidence is unavailable | Is the outcome explicitly indeterminate rather than success? |

These are constructed hypotheses, not reports of Utah operations. The affected contexts include people without a compatible device, people with accessibility needs, and individuals choosing physical identity irrespective of device ownership. The initial harm proposition is exclusion or indirect compulsion due to format-dependent service conditions. Existing RAHP corpus risks must be examined before assigning canonical or example-local risk IDs.

## Evidence boundary and next gate

The proposed first examination needs the pinned source, relevant administrative rules (if available), pathway and acceptance-point inventories, service workflows, comparative service metrics, and complaint/remediation evidence. The latter are not available in this documentary exercise. Do not infer runtime compliance or noncompliance from their absence.

The next increment must qualify the local archive representation for the review contract without weakening existing Git checks. The archive is available for documentary examination; no publisher authenticity or redistribution claim is made. Only then introduce example-local risks, cases, review and evidence bindings and reproducible checks. No risk scores, guardrail results, findings or assurance outcomes are asserted here.

No canonical DTG records or shared contracts are modified. This foundation was prepared with AI assistance and remains subject to accountable human review.
