# Acceptance evidence and reconciliation — 27 November 2026

AI-assisted assessment record. The final validation evidence and current acceptance decisions appear under [Consolidated assessment evidence](#consolidated-assessment-evidence). Earlier observations below are retained as historical evidence, not current status. Baseline 7a04d19861cff821afadcc430ac30886a68a0e6f: GitHub build, validation and DCO passed. Supplied repository snapshot executed locally with the retained ZIP: consolidate.py exit 0, 21 members verified, 141/142 requirements, 703 objectives, 47 normalization gaps including IDP-08, review-required. Focused unittest discovery: 28 tests passed. This is evidence for that snapshot, not subsequent commits or publisher authentication.

## Initial acceptance evidence (historical)

- Representative normal, adverse and failure-path scenarios documented: cases.json and thematic cases (equivalent-service, P-06, L-06, D-06 and adverse counterparts).
- Selected risks connected to harms and failure conditions: consolidated 31 local hypotheses, 47 cases and their risk references; no scoring.
- Representative cross-actor and cross-profile scenarios examined: C-01–06, EI-01–04, OS-01–03 and source-bound examination records; documentary only.
- Material cross-requirement interactions represented: synthesis now binds all 47 cases, with existing local risks retained rather than new cases invented.
- Applicability outside DTG evaluated: REVIEW-HANDOVER.md method applicability; no shared change proposed.
- Existing validation and reproduction mechanisms exercised: actual consolidated archive execution and focused regression suite on supplied snapshot.

At this earlier revision, the following remained open: persona/context justification across all risks; normalized risk/control and objective mappings; complete verification applicability and limits; all three full requirement coverage criteria; comprehensive independent source corroboration; formal findings source/interpretation/recommendation separation and treatment qualification; strict completeness and unresolved-metadata negative gate (not yet fully demonstrated); independent reproducibility of reasoning; reviewers, review objections and publication decisions. Existing checked criteria retained. IDP-08 remains a source dependency, not a successful examination.

## Initial source and analytical reconciliation (historical)

Reconciled 43 companion/thematic authority references and visible method applicability rows. Legacy objective coverage arrays retained for compatibility. Null/absent method applicability is unresolved, not N/A; no claim that all source fields or objective text are reconciled. All cases now linked to synthesis; consumer rejects omitted synthesis coverage. Subsequent execution is recorded below.

### Source correction

Reinspection of retained Parts 7 and 9 establishes ADMN Mandatory and EXPT N/A for KMS-04, LOY-04, LOY-05 and INT-01. KMS-04 and INT-01 AUTO Mandatory; LOY-04/05 AUTO N/A. Corrected exact objective coverage, including KMS-04 parameter checks. The earlier four conflicts originated in author-side metadata, not the source. EXPT limitations for KMS-04 and INT-01 still describe expert review. Other metadata requires systematic corroboration; the broader source reconciliation was not yet complete at that revision.

## Source reconciliation and commit-bound replay — 2026-11-27

The retained archive SHA-256 matches the manifest; all 21 extracted substantive source files were compared byte-for-byte with their ZIP members. Author-side detailed-section extraction located 141 of the 142 indexed requirements, containing 703 numbered objectives. Comparison against the original uploaded snapshot found no differences in the numbered objective sequences or explicit method-objective assignments. This is a structural comparison, not independent interpretation of the source. INT-04 has no declared ADMN applicability; null is not N/A. The heading references for SDI-24, ENF-03 and ENF-04 were distinguished from other citations in their preceding prose. The 43 legacy array records now reflect the extracted verification-method declarations, and LOY-03–05 retain the source's all-participant scope. Existing source page ranges still need full-span corroboration; no assertion of complete source reconciliation is made.

The synthesis now contains twelve open propositions with explicit recommendations, proposed treatment authorities, interpretation boundaries and requirement references. The consumer derives source bindings from normalized records and rejects missing or duplicate required references, invalid additional references and empty recommendations. The direct CRY-04/ORG-04 references in S-10 are separately justified rather than being represented as case-derived evidence. No observed implementation failure or independent acceptance is asserted.

### Executed validation

Execution baseline: `4c190963210c8c50b28c74820c9a1d053dbd447f`. Reconstructed the execution files from the supplied GitHub ZIP at `7a04d19861cff821afadcc430ac30886a68a0e6f`. The original snapshot's indexed review, tests, tools, method, data, context, site, docs and root guidance match the corresponding Git tree/blob identities. Its historical archive directory differs from the base Git tree; full repository-tree identity is not claimed. All nine changed execution/data/test files were reconstructed and individually matched the execution baseline's Git blob SHAs. The evidence-only Markdown file was not needed for execution.

- Actual retained-source `consolidate.py`: exit 0; 21 verified members; 141/142 examined; 703 objectives; 31 local hypotheses; 47 constructed cases; 12 synthesis propositions; 47 records with normalization gaps (including IDP-08); documentary coverage incomplete; normalization incomplete; review-required.
- Actual retained-source `examine.py`: exit 0; seven scoped requirements; 32 mapped objectives; four open findings; candidate validation complete; formal review not established.
- `python -m unittest discover -s tests -p 'test_sedi*.py' -v`: 28 tests passed, including new negative mutation subtests.
- `check_coverage.py --require-complete`: exit 1, expected rejection: one requirement remains indexed only.

The executable replay resolves the earlier repository retrieval obstacle. Missing analytical metadata, complete page-span verification, source interpretation, IDP-08 publisher clarification and independent review remain outstanding. The strict completeness gate currently rejects indexed-only coverage, not all unresolved analytical metadata; do not treat this as satisfying the full strict-completeness acceptance criterion. No canonical DTG changes, risk scoring, risk acceptance, legal determination or operational assurance.

## Consolidated assessment evidence

This section supersedes the historical outstanding work recorded above. Source-citation commit `4d40804b749fc8baba5c4f2432918f511d53b22e` and analytical implementation commit `5ba1c38a7fd042f2ed85a7e36febd0803310d937` were checked against the exact locally tested changed Git blobs (six source/candidate files and six analytical/data/test files). The evidence-only changes and the standalone coverage-test import adjustment follow that implementation.

### Source and analytical reconciliation

Reopened the retained Part 1–9 PDF bytes. Located all 141 detailed sections, checked the 703 objective numbers, explicit method-objective assignments, applicability declarations and parameter flags against the normalized records, and compared heading citations and roles. Parenthetical citations and equivalent range notation were checked separately from preceding statutory prose. Eight requirements omitted a page containing their detailed examination; citations were extended for SDI-03, SDI-04, GOV-02, WAL-12, LOY-04, ENF-03, PRV-01 and PRV-03. Existing conservative page sets were not narrowed on text-extraction heuristics. GOV-02's bounded review bindings now include Part 3 page 97. Chapter introductions and informative summaries are not treated as missing numbered requirements. This is author-side structural and documentary reconciliation, not independent review or legal verification.

Legacy reconciliation uses 43 requirement-specific limitation notes, three existing initial limitations, existing case evidence requests and the seven selected objective-control records. All 46 legacy requirements have explicit protection, relevance, limitation, evidence need, related requirements and disposition rationale in the derived view. Contextual risk associations do not claim that each objective independently mitigates the risk. The 95 later records retain their explicit requirement-level analytical mappings. Ten justified context groups cover 47/47 cases; 31/31 local risks have case and harm links. The 12 open synthesis propositions separate source observations, interpretations, existing design protections, treatment recommendations, proposed authorities and resolution evidence. Source citations are derived, including the five IDP-08 gap citations; direct additional sources for S-10 are explicitly reasoned. No new risk or case is introduced.

### Observed execution

- Actual ZIP SHA-256 matches pinned baseline; 21 substantive members verified. Normal consolidated replay exits 0: 142 indexed, 141 examined, 703 objectives, 31 risks, 47 cases, 12 synthesis propositions, ten context groups. Remaining normalization gaps: **two** (IDP-08 detailed section absent; INT-04 ADMN undeclared). Formal review not established; overall assurance review-required; documentary coverage and normalization incomplete.
- Actual bounded SEDI-01 replay exits 0: seven scoped requirements, 32 mapped objectives, four open findings; candidate validation complete, not independent review.
- Focused regression discovery: **32 tests passed**, including new context, limitation, selected-control, source-gap, risk, relation and synthesis negative mutations. Standalone coverage regression: two tests passed after ensuring its test imports use the same module directory as the consumer.
- Both actual strict CLI invocations exit 1, naming IDP-08 and INT-04. A separate negative fixture establishes that an analytical metadata gap is rejected even without an indexed-only record; missing and duplicate inventory rows are already rejected. Positive fixture permits complete metadata without implying operational assurance.
- Repository canonical validation: 0 errors, 32 retained warnings. CI is a separate repository check; do not attribute independent review or source authenticity to CI.

### Acceptance reconciliation

Evidence for the additional acceptance criteria satisfied by the consolidated assessment:

| Criterion | Evidence and closure boundary |
| --- | --- |
| Personas and affected contexts | Ten justified groups in legacy-analysis.json; every constructed case has exactly one group with a rationale. |
| Selected requirement/objective risk and control traceability | objective-controls.json and normalized view: seven requirements, 32 numbered objectives, explicit control, authority, proposed assurance test and guardrail, with source verification consistency. This is selected mapping, not 703 executed tests. |
| Applicable verification methods examined | Retained PDF method tables and all declared applicability/coverage compared; INT-04 undeclared and source tensions retained rather than invented. |
| Verification limits, decisions and unavailable evidence | Requirement-specific limitations and evidence requests, original documentary examination limitations, source-gap and synthesis records; operational evidence not acquired. |
| Strict completeness validation | Both actual strict consumers reject source gaps; missing, duplicate, unknown and blank analytical metadata, source and synthesis failures exercised by regressions. |
| Independently reviewable consolidated records | Exact archive manifest, normalized view, corrected citations, explicit source-gap records, contextual vs direct risk rationale and linked case/evidence records. Reviewability is not review performed. |
| Substantive findings supported by source/evidence | Twelve source-bound review propositions, cited case and additional direct requirement references, proposed resolution evidence; documentary, not observed failures. |
| Observation, interpretation and recommendation separation | Distinct synthesis fields with validation and explicit interpretation boundary. |
| Existing adequate protections alongside gaps | Design-protection field in synthesis identifies meaningful requirement-level protections and qualifies effectiveness; not an operational adequacy finding. |
| Appropriate treatment mechanism and authority | Explicit proposed control plane, treatment authority, recommendation and evidence in synthesis; not an acceptance authority. |
| Methodological changes justified | No shared method or canonical DTG change proposed. Example-local ZIP provenance is justified by the mismatch with Git revision semantics; future generalization is a separate Task Force decision. |
| Reproduce retained-source checks and reasoning | Actual archive execution with verified Git blob identities, precise commands, source references and review guidance in REVIEW-HANDOVER.md. Exact retained bytes must be obtained with appropriate permission. |

The requirement-level analytical disposition criterion is also satisfied: the IDP-08 source-gap record in [identity-proofing-examination.json](identity-proofing-examination.json) identifies its intended protection (independence of physical and digital identity systems), potential harm, EX-RK-HX01 risk reference, related requirements (IDP-09, BOR-03 and BOR-04), evidence needed and a reasoned clarification-required disposition. This is a qualified treatment of the available evidence, not a complete detailed source examination or a verified protection. INT-04 has a detailed analytical disposition with its undeclared ADMN applicability retained. Five criteria remain open: full indexed requirement examination (IDP-08 and INT-04 source clarification), accountable reviewers identified, Task Force review, disposition of material objections and limitations, and publication/communication disposition. The assessment is prepared for qualified independent review, subject to new evidence or objections. No canonical changes, release or external communication are warranted by author-side closure.
