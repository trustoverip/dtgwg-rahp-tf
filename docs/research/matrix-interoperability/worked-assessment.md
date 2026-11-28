# Worked assessment: withdrawal of delegated authority

## Research question

Can RAHP preserve the distinction between a past successful authorization, present authority, and evidence of enforcement after revocation? The Matrix proposition `A01-P5` (under threat `Authority-01`, incremental authority accumulation) is a useful test because a parent grant can become unusable while descendant and partial grants still exist. The three source scenario IDs are `A01-P5-POS`, `A01-P5-NEG`, and `A01-P5-ADV`. The proposed control `CTRL-09` remains planned in the supplied workbook. The source's `CAMP-001` is not approved and its three corresponding run rows have no raw outcome. We do not modify those records or assert that a Matrix campaign ran.

The source's scenarios are draft designs rather than executable protocols. For this experiment we instantiate them as an explicitly authorized booking through a two-level delegation, an attempted commitment assembled from separately limited permissions, and attempts to use cached approval, fallback, or recombination after revocation. The reference uses one ancestry check for these labels, not independent cache, fallback or composition mechanisms. This is a specialization of the source designs, not a lossless import or a claim that all requirements of the source scenarios were exercised. See [source lock](source-lock.json) for exact source locations and digests; WLA §§2.1–2.4, 9.1, 10.2, 11.1, 19.1, 20.1 and 39–41 explain the relevant assurance and lifecycle distinctions.

## Subject, context and protocol

The reference subject is a small deterministic Python fixture, not a deployed agent or an implementation of the Matrix. A root grant authorizes booking, with a child and grandchild limited to the same operation. Calendar, messaging, purchasing and account permissions are separate and do not jointly authorize a booking. An independent read grant is unaffected. A gate examines grant ancestry; a separate mock actuator ledger records effects. The oracle is a declared expected result for each request, not the gate's output. The ledger and gate are implemented in the same fixture, so separate observations are not independent external verification.

The baseline is at logical tick 9. The sole material change is revocation of the root booking grant at tick 10; the declared experimental deadline is tick 12, inclusive. The code and grant topology are unchanged. The reference denies revocation-dependent requests immediately; the trial protocol observes the boundary and later tick, not propagation through a distributed deployment. This deadline, scope and grant graph are research assumptions, not source-approved thresholds or duties. No real payments, identities, credentials, relationship state or external services are involved.

| Source scenario / research trial | Baseline or reassessed observation |
|---|---|
| POS (B1) | At tick 9, the authorized grandchild booking reaches the mock ledger. |
| NEG / ADV (B2, B3) | At tick 9, separately limited grants cannot authorize a combined commitment. |
| POS (B4, R6) | Independent read succeeds before and after revocation. |
| NEG (R1, R2) | At tick 12, the descendant and unreviewed combined commitment are denied; no booking effect. |
| ADV (R3, R5) | At tick 12, the cached-labelled descendant and recombination-labelled partial grants are denied; no booking effect. |
| ADV (R4) / NEG (R7) | At tick 13, fallback-labelled and direct requests repeat the ancestry check; no booking effect. |

## Observations and interpretation

[Retained evidence](lifecycle-evidence.json) contains the actual replayed reference traces: source proposition ID, context/subject/protocol bindings, logical timestamps, offered grants, current revocation record, gate decision and mock actuator effects. The protocol results are separately derived from those traces. Four baseline and seven reassessed reference trials are defined; R7 repeats the direct request after the deadline. A baseline protocol PASS does not establish revocation effectiveness before revocation occurs.

Three mutation configurations deliberately introduce incorrect outputs to challenge the oracle. They share the same implementation digest; the variant and protocol context distinguish the runs. The reference has no independent cache, fallback or composition mechanism. The following counterexamples are injected faults, not observed failures of those mechanisms:

| Challenge | Observed discrepancy | Trial |
|---|---|---|
| Cached authority | Gate accepts the descendant despite revocation; booking effect occurs. | R3 |
| Fallback bypass | Gate denies; booking effect nevertheless occurs. | R4 |
| Recombined permission | Partial grants are treated as authority for booking after revocation; booking effect occurs. | R5 |

A fourth mutation delays propagation until tick 13. At deadline 12 the mutation must fail, while the later direct trial succeeds in rejecting the request. Moving the deadline to tick 13 changes the expected observation schedule. Missing, duplicate, wrong-context or incomplete observations cannot establish a PASS. A correctly bound contradictory observation remains a failure even if other required evidence is absent. These are checks on the example's evidence handling, not an implementation of all Matrix formula semantics.

The draft [baseline review](baseline-review.json) and [reassessed review](reassessed-review.json) use the existing `rahp-spec-review/v1` contract against the pinned Matrix README. The immutable Git target is documentary; the supplied workbook digest and constructed subject context are carried in separate evidence, not misrepresented as Git revisions. The accountable draft owner is identified in the records; neither record asserts independent human adjudication. Both now retain the same documentary findings about translation and proposed enforcement evidence; neither asserts a finding about execution of the fixture. The earlier mixed findings remain inspectable in Git history. The source proposition is identified by the workbook digest and Propositions!11 locator in the source lock; the separate experimental record binds the subject, configuration, protocol and observations. The evidence binds both reviews and the local risk register to the source lock. The fixture's protocol results are not finding treatment statuses, effective Matrix outcomes or an assurance certificate.

## Affected people and potential harms

The principal withdrawing the booking grant bears the immediate exposure: an unauthorized commitment could create financial loss, unwanted travel or disclosure of plans, and a burden of cancellation or dispute. A person experiencing changing capacity or coercive pressure may have less ability to detect, contest or reverse such an effect. A delegate and relying service may also face conflicting instructions and dispute costs. These are contextual harm hypotheses, not observed human outcomes; the mock ledger demonstrates only the declared effect. Affected-person input and actual deployment evidence are absent. The analysis informs [#59](https://github.com/trustoverip/dtgwg-rahp-tf/issues/59) (who bears risk) and [#76](https://github.com/trustoverip/dtgwg-rahp-tf/issues/76) (interacting components).

## Reassessment after change

The affected dependency is the root grant's current validity, through its child and grandchild, to direct/cached/fallback booking decisions and observable effects. The reference checks each offered grant individually and cannot compose partial grants. The recombination mutation tests detection of an injected allow decision, not a composition mechanism. Dependency selection and the following dispositions are authored interpretations, not computed outputs. The independent read grant has a separate lineage; its continued success is observed rather than presumed. The following dispositions concern the applicability of evidence to a stated claim, not changes to historical bytes.

| Disposition | Evidence and rationale |
|---|---|
| Retained | Baseline source/protocol and grant topology remain identifiable; baseline traces still establish what occurred at tick 9. The independent read path is also re-exercised. |
| Stale | The tick-9 authority snapshot cannot answer a tick-12 current-authority question. Obtain the new snapshot. |
| Weakened | Earlier direct-path success alone offers less support after revocation. Cache and fallback labels repeat the ancestry check; actual cache and fallback behavior remains untested. |
| Invalid | Using the old booking approval as authority for a new execution after parent revocation breaks a necessary assumption, irrespective of the historic trace's integrity. |
| Contradicted | In the separate fallback challenge, a recorded gate denial is contradicted as evidence of containment by the observed mock booking effect. The counterexample is retained; no nominal baseline observation is rewritten. |
| Unresolved | Real propagation, concurrent or undisclosed paths, deployment identity, reviewer independence, and duty/relationship obligations are not established. Missing dependency edges are not evidence of unaffected claims. |

The focused reassessment thus retains the earlier review, context and observations, while testing the specific changed condition. An accountable system could use the bounded findings to consider restrictions on booking while retaining unrelated read access. RAHP itself does not make or enforce that decision; reassessment cannot restore a revoked grant.

## Transformation limits and review questions

- Review v1 represents the two findings, the documentary target revision and their treatment plane. It does not natively express the workbook's campaign identity and approval, six outcome states, trial coverage/closure review, subject embedding, time, or evidence dependency graph. The sidecar preserves the selected experimental information; source campaign/run records remain unassessed. No round-trip conversion is claimed.
- Tested coverage is limited to the declared observations, ticks, grant graph and effect ledger. The deadline parameter determines the observation schedule, including a direct request after the boundary. Distinct path labels do not demonstrate distinct mechanisms. No statistical generalization, real authority evidence, distributed timing, concurrent operation, end-to-end deployment, or human outcome is tested. An independent reviewer should challenge whether the selected protocol adequately instantiates the source proposition and whether the dependency reasoning is complete within the fixture.
- No core extension is justified by this result alone. Existing RAHP review records plus an example-local sidecar suffice for this bounded demonstration; general evidence applicability and dependency representation remain research questions.

## Reproduce

From repository root after installing `requirements.txt`:

```sh
python3 docs/research/matrix-interoperability/lifecycle.py
python3 -m unittest discover -s tests -p 'test_matrix39_lifecycle.py' -v
```

The default replay compares fresh observations and evidence bindings to the retained file. It reports PASS for the two reference protocol runs, FAIL for the four challenge variants, `matrix_campaign: not-executed`, `overall_assurance: review-required`, and `source_bytes: not-reverified`. To independently recheck the exact source copies, obtain them from the contributor or publisher with appropriate access, then add `--workbook PATH --wla PATH`; mismatching bytes fail. Source bytes are not redistributed in this repository. Matching digests establish copy identity, not publisher authenticity, online equivalence, or endorsement. Inspect the workbook cells and WLA sections listed in the source lock separately.

The repository's ordinary regression discovery validates the three example-local RAHP review records using the existing validator and exercises the reference and adverse evidence cases. No generated files or canonical DTG records are changed. Prepared with AI assistance under the contribution process; independent methodological review and contribution checks remain required.
