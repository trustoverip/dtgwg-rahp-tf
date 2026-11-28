# Can RAHP assess a fiduciary-agent assurance proposition over time?

This research addresses [issue #39](https://github.com/trustoverip/dtgwg-rahp-tf/issues/39). It examines whether the Risk Assessment and Harms Prevention (RAHP) method can represent the Fiduciary Agent Threat and Assurance Matrix's assessment requirements and reconsider findings after a relevant change. It does not propose replacing RAHP or making it specific to fiduciary agents.

## Findings

The Matrix explicitly derives its assurance-register foundation from RAHP. Shared constructs are expected and do not establish independent interoperability. The Matrix and RAHP share a useful distinction between a risk, a proposed control, observations, and the judgment those observations support. The Matrix also defines campaign-level conditions for accepting an assessment outcome, including explicit context, coverage, applicable evidence, and review. Those conditions cannot be translated directly into the RAHP v1 specification-review contract without preserving additional information.

The [worked assessment](worked-assessment.md) takes a real catalogue proposition, `A01-P5` (revocation of derived authority within a declared deadline), and examines it in a constructed reference subject. It preserves before/after observations when the parent grant is revoked. The nominal protocol succeeds; four mutation configurations challenge the oracle, including delayed revocation propagation. This demonstrates reproducible reference experiments and a way to represent their findings, not live-system revocation enforcement or a completed Matrix campaign.

## Semantic crosswalk

The [source lock](source-lock.json) identifies the inspected RAHP revisions, Matrix README, contributor-supplied workbook and Warranted Lifecycle Alignment (WLA) paper. The workbook copy is content-addressed; its equivalence to the current publisher edition and permission to redistribute it have not been established. The following mappings are bounded to the inspected sources and selected proposition. Tabs without workbook locators in the source lock are described at README level only, not verified at workbook-row level.

| Matrix construct (workbook tab) | RAHP analogue | Classification and limit |
|---|---|---|
| Threat, affected interests (`Threats`) | Risk and harm | Compatible specialization; duties and risk scores do not transfer automatically. |
| Required proposition, criteria, retest triggers (`Propositions`) | Review finding, linked risk, evidence proposition | Partial mapping; finding treatment status is not a proposition's outcome. Keep acceptance criteria and retest conditions separately. |
| Positive/negative/adversarial scenario (`Scenarios`) | Example-local fixture, assurance-test design | Partial mapping; scenario intent is not evidence of coverage or an executed test. |
| Campaign and run (`Campaigns`, `Assessment Runs`) | Source-pinned review with example-local observations | Implementation gap for native interchange; context matching, approval, raw/effective outcomes and time are not represented directly in review v1. |
| Planned control and relationships (`Controls`, `Relationships`) | Control/guardrail and risk links | Partial mapping; control design and measured effects differ. Do not infer implementation or guardrail satisfaction from the link. |
| Coverage and evidence closure (`Coverage`, `Evidence Registry`) | Evidence sidecars and tested-path descriptions | Partial mapping; the presence of an artifact is not evidence adequacy, independence or current applicability. |
| Dependencies and repair (`Assurance Dependencies`, `Changes and Repairs`) | Historical review and reassessment, e.g. VRC example | Existing manual/example-local approach; automatic dependency traversal and applicability adjudication are not demonstrated. |
| Subject, embedding, duties and relationship (`Assurance Subjects`, `Duty Profiles`, `Relationship State`) | Review target plus external context | Domain-specific and external; RAHP can examine a requirement, not determine legitimate fiduciary duties or authority. |
| Reliance and operational decisions (`Operational Decisions`, `Peer Inspections`) | Findings and recommendations; external governance | Intentional non-mapping for authorization/enforcement; peer evidence can inform but not replace accountable judgment. |

The source formulas reinforce this distinction. In `Assessment Runs!R82:R84`, absence of a raw outcome is not assessed, a recorded failure takes precedence, and an unresolved contradiction requires review. A raw PASS cannot become an effective PASS without matching approved context, current evidence, coverage and closure review, and other specified inputs. Scenario and proposition formula cells (`Scenarios!D19:D21`, `Propositions!D11`) retain adverse or unresolved results rather than treating counts as evidence adequacy. These are inspected formula semantics, not a full spreadsheet recalculation or implementation of its outcome engine. See the worked assessment for the resulting transformation losses.

The Matrix's PASS and FAIL have analogous local meanings in the fixture; INDETERMINATE is represented, but REVIEW REQUIRED is not a separate trial outcome. NOT APPLICABLE and NOT ASSESSED have no trial-level equivalent. None maps directly to a RAHP finding treatment status.

## Recommendation

Use existing RAHP specification-review records and example-local evidence to examine the proposition and preserve the two contexts. Keep fiduciary duty, delegation, relationship state, and operational authorization external. A common evidence applicability or dependency representation may be useful across domains, but this single reference example does not establish that a new core contract or runtime capability is required. The [comparative assessment](comparative-assessment.md) examines TRQP, VRC, TEA and downstream freshness, impact and comparison mechanisms. It recommends no core change on the present evidence, subject to independent review. A native adapter is not warranted without a demonstrated consumer need.

No canonical corpus, method, schema, risk scoring or release change is proposed. All findings remain draft and subject to independent human review. Prepared with AI assistance; no task-force approval or risk acceptance is implied.

The local risk IDs EX-RK-MX01 and EX-RK-MX02 replace the earlier AU identifiers in this example only; their meanings are unchanged. This avoids confusion with the TRQP example. Findings and source revisions are unchanged. The evidence-applicability result informs #81 and #80; source binding informs #75. Upstream portability and freshness support remain open under #77 and #81.
