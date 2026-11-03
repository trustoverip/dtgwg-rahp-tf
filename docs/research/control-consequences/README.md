# Control-induced harms and redistributed exposure: upstream research (#38)

**Status:** contributor engineering research and proposed Stage 2 clarification, **not** an adopted Task Force decision or target assurance. Source baseline: upstream `0481ab15dc6a926b024745b07674a5e130915d44`; supporting downstream method/example result: [PR #1108](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/pull/1108), merged as `f7f3902215782fb7eaaf91c265c4ef8419d09461`. Motivation: [HTX discussion #22](https://github.com/trustoverip/dtgwg-htx-tf/discussions/22). The cases in [cases.json](cases.json) are *hypotheses and catalogue mappings*, not field observations.

## Decision question and representation inventory

Does the portable method require a new control-side-effect relationship, or can it make the evaluation explicit using existing context, risks, findings and evidence?

| Upstream surface at pinned revision | What it already enables | What it does not establish |
| --- | --- | --- |
| `method/lifecycle.yaml`, STAGE-2-1/2/3 | Design decisions name affected personas; assessment checks whether a choice introduces risks; controls must be monitorable | The previous Control station did not explicitly examine harms caused by the *control itself* |
| `method/schema/rahp.schema.json`, `control` | `linked_risks`, guardrails, rationale and provenance | No `introduces_or_amplifies_risks` field; `linked_risks` refers to risks treated and must not silently be reused with opposite semantics |
| `data/instance.yaml` and `data/risks.yaml` | Stable DTG risk identifiers, relationships, personas, metrics, and reusable risk hypotheses | Risk presence alone does not prove a side effect or its magnitude in a new control context |
| `review/spec-review.schema.json` | Source-pinned findings with risk references, control-plane responsibility, status and structured closure | No dedicated affected-actor/trade-off fields or `INDETERMINATE` status; missing consequence evidence should be retained as an **open finding plus supporting evidence**, not invented as a new enum |
| `ADOPTION.md` and `docs/pressure-testing-a-spec.md` | Reuse-first practice, bounded review and human contextual judgment | No automated comparative optimization or policy authority |

The downstream implementation already uses `introduces_or_amplifies_risks`, `CTP-RISK-01`, `ATP-RISK-01` and `EVP-RISK-01`. **Those contracts do not exist upstream** and are not imported by this research. This repository is the authoritative upstream target.

## Cross-domain examination

The [four cases](cases.json) adapt downstream CCA-001, CCA-002, CCA-004 and CCA-005 to the upstream corpus, with distinct control types and explicit actors. Each records intended mitigation, separate exposures, *candidate* existing risk links, evidence state, disposition and assurance implication:

| Case | Benefit / burden | Risk reuse | Bounded disposition |
| --- | --- | --- | --- |
| UCCA-001 renewal | Relying-party freshness / holder proofing exclusion | RK-CR02, RK-NM01 | Context-specific residual; missing deployment evidence |
| UCCA-002 uniqueness | Integrity / applicant exclusion and correlation | RK-ID01, RK-ID02, RK-ID05 | Existing catalogue coverage of *hypotheses*, not implementation assurance |
| UCCA-003 revocation | Withdrawal enforcement / collateral cross-community impact | RK-AI02, RK-CR03 | Context-specific residual; verify propagation topology |
| UCCA-004 human checkpoint | Principal intent / accessibility and fatigue | RK-AI01, RK-HX04, RK-NM01 | **Insufficient evidence: indeterminate; control credit withheld** |

The fifth downstream case on contestability/retention remains relevant but is not needed to establish cross-domain variation. It can be examined if a reviewer identifies an actual representation gap.

## Portable assessment sequence (proposed)

1. **Identify mitigation:** the specific target risk and the actor for whom a benefit is expected.
2. **Look for control consequences:** introduced, transferred, amplified or redistributed harm, including exclusion, autonomy, privacy, security and operational effects.
3. **Separate actor interests:** never offset an affected person's exposure solely because another actor gains assurance.
4. **Reuse existing risks first:** cite applicable canonical risk mechanisms without changing their meanings or implying that linkage proves a particular deployment effect.
5. **Record disposition:** existing catalogue coverage; context-dependent residual/trade-off; candidate new reusable mechanism (with proof of insufficiency of existing coverage); or insufficient evidence.
6. **Retain evidence and non-findings:** put contextual reasoning and unverified consequences in accompanying review material. A material gap remains an open finding where appropriate; it cannot silently become PASS. No `INDETERMINATE` value is added to the upstream review schema.
7. **Reassess when context changes:** track relevant specification revisions, deployment policies, source evidence and the consequences of control modifications.

## Alternatives and recommendation

| Alternative | Result |
| --- | --- |
| No change | Existing Stage 2 wording partially covers new risks, but a reviewer may treat successful mitigation as the end of evaluating a control |
| Documentation only | Helpful for adopters but leaves the portable lifecycle's Control station ambiguous |
| **Small method clarification + assessment-local examples** | **Preferred:** explicit obligation without new record types; existing review and corpus structures remain authoritative |
| New relationship in `data/instance.yaml` | Not justified: no canonical instance records require a new relationship, and its semantics and migration would need governance |
| Portable schema/enum extension | Not justified by four hypothesis cases; would introduce validation, compatibility and migration obligations without demonstrated enforcement need |

The bounded proposal changes only the description of STAGE-2-3: a selected control's target mitigation is not an overall adequacy conclusion; material consequence and uncertainty must remain separately reviewable. It does not mandate a new ID for each effect or assert how conflicting interests should be governed.

**Limits:** The fixtures are constructed source-based analyses, not observed field effects. Their `evidence_state`, `disposition` and `assurance_implication` belong to an **example-local research format**; they are not shared RAHP schema members or validated risk-acceptance decisions. The four dispositions are analytical labels, not new controlled vocabulary. No risk scores, authority, policy optimization or conformance result is supplied.

## Reproduction and challenge

From the upstream repository root:

```sh
python3 -m unittest tests.test_control_consequences_research -v
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/validate.py
```

Read `cases.json` against the pinned `data/risks.yaml`, `method/lifecycle.yaml`, `review/spec-review.schema.json`, and downstream [CCA fixtures](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/f7f3902215782fb7eaaf91c265c4ef8419d09461/examples/control-consequence-assurance/cases.yaml). Challenge each actor attribution, existing-risk mapping and missing evidence. Automated tests check fixture coherence and fail-closed *example-local* state; they cannot verify the truth of harms, constitute independent methodological review, or certify an upstream governance decision.

## Disposition of issue #38

**Proposed:** current upstream records and review contracts suffice for explicitly documented control consequences; the portable lifecycle needs a small clarification, not new schema. An independent upstream reviewer should confirm the mapping and determine whether to merge the method clarification. If new counterexamples demonstrate a genuine expressiveness gap, open a separate scoped issue with enforcement and compatibility evidence rather than enlarging #38.
