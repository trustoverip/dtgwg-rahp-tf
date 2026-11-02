# Risk acceptance governance protocol — GAP-3.1 proposal

**Status: proposed for adoption. No risk is accepted by this document.** RAHP can constrain the completeness and provenance of an acceptance record; it cannot designate itself or a GitHub contributor as a risk owner. A competent authority must be established by the adopting working group's own mandate.

## Preconditions and accountable decision

1. Identify the subject, immutable version, affected people/communities, risk ID, initial and residual exposure, applicable controls/guardrails and evidence. Record uncertainties and missing evidence. An absent assessment is not a low risk.
2. Verify that the risk is **eligible**. A `Critical` risk under the current upstream method is **not acceptably waived**; it remains governed by protective guardrails and escalation. Never infer that a passing CI test is risk acceptance.
3. Identify the actual accepting body and its delegated mandate, named decision participants, conflicts of interest, and the independently reviewable decision record. A named role alone is not evidence of delegation.
4. Evaluate alternatives: mitigate, avoid, transfer under demonstrable authority, reject the proposed exception, defer for evidence, or formally accept eligible residual risk. Specify the treatment scope, conditions, monitoring/notification expectations and review trigger.
5. The authorized body records its disposition and cited evidence, effective date, expiration/review date and rationale. If the authority, evidence or effective dates are missing, record `pending` or `deferred`, **never `accepted`**.
6. Reassess at the earlier of review date, material source/corpus change, exposure change, failed safeguards, new affected-party evidence or governance authority change. Retain historical decisions; do not rewrite a past acceptance to imply continuous authority.

## Contract boundary

The current upstream `data/risk-acceptances.yaml` holds RA-001 to RA-003 as `pending`; they **must remain pending** until actual authorized decisions. The existing schema is structural and does not establish who may accept risk. This proposal adds a **standalone advisory gate** for proposed decision records. It does not extend canonical method/schema, grant authority, modify severity rules or turn an upstream review's `risk_accepted` status into evidence of a valid underlying authority decision.

For the **advisory decision packet used by this proposal**, at minimum require: `risk_id`, decision, `authority`, `authority_reference`, `decided_by`, `decision_date`, `review_date`, `rationale`, `residual_risk`, `affected_people`, `alternatives_considered`, explicit `conflicts_of_interest`, and a non-empty `evidence` reference. This packet is not the canonical `risk_acceptance` schema: fields such as `authority_reference` and the advisory `deferred` disposition are proposal-local until the task force decides whether and how they map into the canonical contract. The helper checks local documentary shape only; a competent reviewer must authenticate the mandate and determine whether the cited evidence actually resolves and is adequate.

## Negative controls

- No authority reference or decision participants: not acceptance-ready.
- No evidence or review expiry: not acceptance-ready.
- Proposed Critical-risk acceptance: prohibited under the current method.
- Existing pending RA-001, RA-002, RA-003: remain unchanged and ineligible for being reported accepted.
- A review finding with `risk_accepted` but no separate recorded competent decision cannot by itself prove accepted residual risk.

## Decision needed from the task force

Confirm which body can authorize residual-risk acceptance for the *DTG instance*, whether any risk types are strictly non-waivable beyond Critical, and how decisions are publicly documented, challenged and reauthorized. Other adopting groups establish equivalent authority under their own mandates.

### GAP-3.1 closure threshold

After competent task-force adoption, validate the agreed authority model against a real decision workflow (including a rejection or deferral), document the reviewer and decision record, and demonstrate the gate fails closed. Only then change `method/lifecycle.yaml` from **blocking** to a resolved disposition. Until then GAP-3.1 remains open and existing pending acceptances are not altered.

## Advisory check execution

The check operates on a single proposed decision packet **outside the canonical risk-acceptances corpus** and derives severity from the risk corpus supplied with `--risks`, rather than from a severity value inside the decision packet. The checker does **not** authenticate that the selected corpus is authoritative; that selection must be established by the review/governance context. Passing an altered corpus can therefore change the result and must not be represented as protection against a malicious caller-controlled corpus.

```sh
python3 review/check_risk_acceptance_documentation.py proposed-decision.yaml --risks data/risks.yaml
python3 -m unittest discover -s tests -p 'test_risk_acceptance_documentation.py' -v
```

A `documentary_ready: true` result is only local field/syntax readiness and **never** authenticated authorization. An unresolved `risk_id`, absent risk corpus, missing mandate reference, missing participants, missing affected-people/alternatives context, absent evidence text, invalid date syntax, or a review date that does not follow the decision date prevents documentary readiness. The helper does not determine whether a review date has expired relative to today's date and does not resolve external evidence references. The gate does not silently convert a pending decision into an acceptance. The proposal is advisory until its semantics are approved under competent upstream governance.
