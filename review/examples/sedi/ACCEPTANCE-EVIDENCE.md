# Acceptance evidence audit — 2026-11-27

AI-assisted author-side record. Baseline 7a04d19861cff821afadcc430ac30886a68a0e6f: GitHub build, validation and DCO passed. Supplied repository snapshot executed locally with the retained ZIP: consolidate.py exit 0, 21 members verified, 141/142 requirements, 703 objectives, 47 normalization gaps including IDP-08, review-required. Focused unittest discovery: 28 tests passed. This is evidence for that snapshot, not subsequent commits or publisher authentication.

## Closure decisions

- Representative normal, adverse and failure-path scenarios documented: cases.json and thematic cases (equivalent-service, P-06, L-06, D-06 and adverse counterparts).
- Selected risks connected to harms and failure conditions: consolidated 31 local hypotheses, 47 cases and their risk references; no scoring.
- Representative cross-actor and cross-profile scenarios examined: C-01–06, EI-01–04, OS-01–03 and source-bound examination records; documentary only.
- Material cross-requirement interactions represented: synthesis now binds all 47 cases, with existing local risks retained rather than new cases invented.
- Applicability outside DTG evaluated: REVIEW-HANDOVER.md method applicability; no shared change proposed.
- Existing validation and reproduction mechanisms exercised: actual consolidated archive execution and focused regression suite on supplied snapshot.

Keep open: persona/context justification across all risks; normalized risk/control and objective mappings; complete verification applicability and limits; all three full requirement coverage criteria; comprehensive independent source corroboration; formal findings source/interpretation/recommendation separation and treatment qualification; strict completeness and unresolved-metadata negative gate (not yet fully demonstrated); independent reproducibility of reasoning; reviewers, review objections and publication decisions. Existing checked criteria retained. IDP-08 remains a source dependency, not a successful examination.

## CP2–CP4 changes

Reconciled 43 companion/thematic authority references and visible method applicability rows. Legacy objective coverage arrays retained for compatibility. Null/absent method applicability is unresolved, not N/A; no claim that all source fields or objective text are reconciled. All cases now linked to synthesis; consumer rejects omitted synthesis coverage. Repeat actual archive replay after this commit, not just baseline execution.

### Source correction

Reinspection of retained Parts 7 and 9 establishes ADMN Mandatory and EXPT N/A for KMS-04, LOY-04, LOY-05 and INT-01. KMS-04 and INT-01 AUTO Mandatory; LOY-04/05 AUTO N/A. Corrected exact objective coverage, including KMS-04 parameter checks. The earlier four conflicts originated in author-side metadata, not the source. EXPT limitations for KMS-04 and INT-01 still describe expert review. Other metadata requires systematic corroboration; no claim of completed CP2.

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
