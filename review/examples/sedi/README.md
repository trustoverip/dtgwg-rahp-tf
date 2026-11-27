# SEDI documentary assessment using RAHP

Tracking issue: [#71](https://github.com/trustoverip/dtgwg-rahp-tf/issues/71), following the Task Force decision on 25 November 2026.

**Status: prepared for qualified independent review; source completeness and accountable review remain outstanding.**

This worked example examines how the SEDI draft's proposed protections address risks and harms across representative digital identity service interactions. It is separate from the canonical Decentralized Trust Graph (DTG) assessment and uses the RAHP repository's method and tooling.

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

## Detailed examination: physical and digital service equivalence

Question: Can a person who chooses a lawful physical identity format encounter material disadvantage despite a documented physical alternative?

The initial scope is one otherwise eligible individual accessing a government service, with identity format as the variable. The service entitlement, eligibility and transaction purpose are held constant. The Department, service operator and affected individual are the primary roles. The initial scope does not include service-specific obligations of relying parties and health care providers; these are considered in the broader assessment below.

| Requirement | Statutory reference | Initial design proposition |
| --- | --- | --- |
| SEDI-BOR-03 | 63A-20-101(3) | Physical issuance and acceptance remain available. |
| SEDI-BOR-04 | 63A-20-101(4) | The physical alternative is usable without digital enrollment. |
| SEDI-BOR-09 | 63A-20-101(9) | Format choice does not disadvantage the otherwise entitled person. |

Source: [Part 1](https://sedi.utah.gov/implementation-guide/part-1/). Relevant implementation decisions concern acceptance-point review frequency, pathway inventory and permissible channel distinctions. The draft identifies limitations of administrative review, automated platform checks and expert examination; documentary evidence alone cannot establish actual service access. These observations are now traceable to the retained Part 1 PDF (pages 9–14 and 24–26); the local archive manifest identifies its exact bytes.

The [initial requirement inventory](initial-requirements.json) records the three requirement IDs, roles, implementation decision references, objective numbers, verification coverage and evidence categories. The source inventory also records all 18 published requirement domains. Annex A and Annex E are now available. Annex A contains 142 unique requirement IDs, as independently extracted from the PDF. See the consolidated examination below for current coverage.

### Candidate constructed cases

| Case | Variation | Evidence question |
| --- | --- | --- |
| equivalent-service | Both paths provide equivalent access | What comparative evidence establishes equivalence? |
| unavailable-physical-path | A listed physical path is locally unavailable | Can the inventory and audit detect this? |
| digital-enrollment-condition | Staff require enrollment despite documented fallback | Can operational controls detect and remedy informal compulsion? |
| unequal-service | Physical format incurs a material delay or additional burden | How do permitted channel distinctions and operational measurements establish whether the burden is discriminatory? |
| evidence-missing | Policy claims parity but comparable service evidence is unavailable | Is the outcome explicitly indeterminate rather than success? |

These are constructed hypotheses, not reports of Utah operations. The affected contexts include people without a compatible device, people with accessibility needs, and individuals choosing physical identity irrespective of device ownership. The initial harm proposition is exclusion or indirect compulsion due to format-dependent service conditions. The case records document the consideration of existing RAHP risks and the rationale for assessment-local hypotheses.

## Evidence boundary

The proposed first examination needs the pinned source, relevant administrative rules (if available), pathway and acceptance-point inventories, service workflows, comparative service metrics, and complaint/remediation evidence. The latter are not available in this documentary exercise. Do not infer runtime compliance or noncompliance from their absence.

The assessment-local archive representation retains reproducible source identity without weakening the existing Git-based review contract. Formal representation of a non-Git review target remains a Task Force decision. No publisher authentication, redistribution permission, risk scoring, verified guardrail or assurance outcome is asserted.

No canonical DTG records or shared contracts are modified. This assessment was prepared with AI assistance and remains subject to accountable human review.

## Requirement inventory and initial case records

[Requirement index](requirement-index.json) enumerates all 142 Annex A identifiers and their PDF page locations. [Scoped role mappings](role-mappings.json) cross-check the three selected requirements against Annexes E and G. [Candidate cases](cases.json) records five constructed cases, affected contexts, corpus reuse reasoning and documentary dispositions with source bindings. These are author-prepared analytical records, not formal RAHP review findings. The full-text requirement inventory and ecosystem-wide role mapping are not claimed. A non-Git review representation and accountable review remain necessary; no operational assurance is asserted.

## Reproduce the local candidate

The four [companion requirements](companion-requirements.json) clarify non-enrollment, service parity, physical acceptance and the direction of SEDI acceptance exemptions. The [review candidate](review-candidate.json) uses the existing finding vocabulary and finding validation rules but explicitly does not claim the Git-based `rahp-spec-review/v1` contract. Its reviewer remains null until accountable review occurs. This is an example-local proposal, not a new normative method contract.

With the exact contributor-supplied ZIP outside the checkout and repository dependencies installed:

```sh
python3 review/examples/sedi/verify_archive.py '/path/to/SEDI RAHP Review Input.zip'
python3 review/examples/sedi/examine.py '/path/to/SEDI RAHP Review Input.zip'
```

The first command verifies exact archive and member bytes without extraction. The second additionally checks candidate findings against the existing finding schema and vocabulary and checks evidence references. Neither verifies the truth of the documentary interpretation or publisher authenticity. Independent reviewers must inspect the indicated pages, corroborate or challenge the four open candidate findings and agree how a non-Git review is represented. No source documents are redistributed. A different archive must fail, even if it contains similar documents.

The [tutorial](TUTORIAL.md) describes source verification and independent review. [Objective-control mappings](objective-controls.json) cover the seven scoped requirements and 32 numbered objectives at requirement-group level, including treatment owners and proposed evidence checks. They do not constitute verified guardrails or executed deployment assurance tests.

## Privacy and surveillance

[Privacy documentary examination](privacy-examination.json) records twelve selected requirements, their objective and verification coverage, six constructed cases, five local risk hypotheses, source bindings and evidence needs. It preserves the distinction between disclosure choice, protocol unlinkability, structural state anti-surveillance, downstream data handling and interoperability refusal. This examination is included in the consolidated assessment, not the bounded service-equivalence example. It is not an accepted formal review. No operational claims or scores are made.

## Credential lifecycle and continuity

[Lifecycle documentary examination](lifecycle-examination.json) examines nine requirements, including offline status freshness, accessible recovery, substantiation of revocation grounds, planned versus emergency key transitions, and wallet migration. Six constructed cases and five local hypotheses are bound to the archive. Part 3 page 54 explicitly identifies the offline/status tension. No separate suspension mechanism or operational outcomes are assumed. This examination is included in the consolidated assessment, outside the bounded service-equivalence example.

## Delegated authority and accountability

[Delegation documentary examination](delegation-examination.json) examines guardian consent, appointment and action scope, current authority, service parity and duty of loyalty. It distinguishes identity, legal relationship, action-specific authorization and best-interest judgment. Annex G p16 lists LOY-01–04 for guardians while Part 7 LOY-05 names all ecosystem participants; this is retained as an applicability question, not a legal conclusion. This examination is included in the consolidated assessment, outside the bounded service-equivalence example.

## Compositional conformance

[Conformance documentary examination](conformance-examination.json) distinguishes mandatory base requirements, profile-specific technology bindings, actor-level claims, Department rulemaking, paired interaction evidence and prospective certification. It retains explicit questions about Part 9 base coverage and INT-01 expert-review applicability, and links privacy, lifecycle and service-equivalence dependencies to earlier themes. No actual profile or certificate is assessed. See the consolidated examination and review handover below.

## Broader requirement-level examination

The assessment scope includes all 142 indexed requirements, with scenario depth proportionate to the risks examined. [Coverage conventions](COVERAGE.md) and [coverage register](requirement-coverage.json) track documentary examination and indexed-only requirements. The register links the documentary records without duplicating their contents. The complete-coverage gate must remain failing until all requirements have documentary examination records and required analytical metadata; no operational assurance is inferred.

### Rights, governance, processing restrictions and enforcement

[Rights and governance examination](rights-governance-examination.json) examines 22 requirements, source bindings, verification coverage, risk relevance, authority dependencies and evidence needs. PRC is processing restrictions, not procurement. Three constructed cases address discriminatory endorsement, coerced device surrender and cross-purpose processing. Existing thematic risks are reused where sufficient; two distinct local hypotheses supplement them. No independent review or operational assurance is asserted.

### Application and identity proofing

[Identity-proofing examination](identity-proofing-examination.json) records 15 detailed documentary requirement examinations, four constructed cases and three local hypotheses. IDP-08 is indexed and cross-referenced but lacks its standalone detailed section in the retained Part 3 PDF; its source gap is explicitly recorded and the register retains indexed status. The APP-01 age gate is examined alongside guardian pathways, and the informative NIST mapping is not treated as an adopted rule. No source objectives invented; no operational assurance asserted.

### Credential architecture and technical security

[Technical architecture examination](technical-architecture-examination.json) examines 24 requirements and four constructed cases covering authenticity, interoperability, predicate privacy, proofing validation, technological enforcement, infrastructure control, purpose/retention/disclosure, cryptographic agility and key ceremonies. Explicit method applicability and objective coverage are preserved separately. CRY-03 and CRY-04 provide cross-requirement clarification evidence. No operational assurance is asserted.

### Wallet, verifier and relying-party interactions

[Ecosystem interactions examination](ecosystem-interactions-examination.json) examines 27 requirements and four constructed cross-actor cases. Existing local hypotheses are reused. The examination distinguishes local four-condition gates from end-to-end binding, holder-only logs from provider telemetry, actor-specific data processing obligations, and permissive acceptance from specific institutional obligations. No operational assurance is asserted.

### Organizational security

[Organizational security examination](organizational-security-examination.json) covers all seven ORG requirements (Part 9 pp44–59), including access and personnel security, vulnerability management, privacy-preserving logging, incident response, delegated infrastructure and change control. ORG means organizational security, not organizational identity. Existing risk hypotheses suffice; three cross-actor cases extend them. Coverage is 141/142, with IDP-08 the sole indexed-only source dependency. No operational assurance is asserted.

## Consolidated documentary records

Run `python3 review/examples/sedi/normalize_coverage.py` to derive a consistent requirement view from the register and existing examination records. No generated duplicate is committed. Source bindings, objective sequences and method coverage are checked; missing authority, applicability, analytical fields and the IDP-08 source gap remain visible. The view is not a source transcription or independent assurance decision. The author-side reconciliation resolves the original analytical field omissions; the two remaining normalization gaps are IDP-08 (missing detailed section) and INT-04 (ADMN undeclared).

## Consolidated consumer and review handover

Run `python3 review/examples/sedi/consolidate.py /path/to/retained.zip` for the integrated retained-source and documentary consistency path. See [review handover](REVIEW-HANDOVER.md) for limitations and remaining gates. Candidate propositions are not formal findings; independent review is pending.

The [synthesis](synthesis.json) groups documentary observations into twelve open review propositions, including the IDP-08 dependency and method-applicability questions. The synthesis explicitly separates source observations, author interpretations, existing design protections, recommendations and proposed treatment authorities. Case IDs remain analytical instruments; the consumer rejects invented case-level control-plane assignments. Proposed treatment authorities are not acceptance authorities.

## Review readiness

[Acceptance evidence](ACCEPTANCE-EVIDENCE.md) records the source-field comparison, actual archive replay, strict completeness checks and criterion reconciliation. All 141 detailed requirements now have analytical fields and reviewable source bindings. Ten justified affected-context groups cover all 47 constructed cases. The 32 selected objectives have explicit requirement-group control mappings; the remaining objectives are not asserted to have been individually executed. All 46 earlier examination records are reconciled in the derived view. INT-04 administrative verification applicability remains undeclared. IDP-08 has a source-gap record identifying the intended protection, potential harm, risk reference, related requirements, missing evidence and reasoned clarification-required disposition; it does not have a complete detailed examination. See the [review handover](REVIEW-HANDOVER.md) for reproduction and the remaining publisher and Task Force decisions. No formal review or assurance is claimed.
