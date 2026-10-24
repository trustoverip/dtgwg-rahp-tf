# Contribution and integration governance — GAP-5.1 proposal

**Status: proposed for task-force approval.** This document defines a usable procedure and accountability questions, but does not confer decision rights. Accepted task-force governance and repository rules prevail. The task force must identify its decision authority before this protocol can be marked operational.

## Intake and routing

1. Submit an issue/PR describing the problem, affected target (method, DTG instance, exemplar, validator, tooling, documentation, or governance), evidence, version impact and reproduction commands. An issue may be used for a decision that does not require code.
2. Classify the change. Upstream owns method/schema/vocabulary and generic adoption requirements; a target's own working group owns its specification and risk decisions; downstream controllers, routing and deployment controls are not automatically upstream components.
3. Associate the contribution with a tracked issue, identify dependencies and distinguish accepted upstream contracts from proposals. Do not build on an unmerged branch without explicitly recording that dependency.
4. Include the proportional reviewability information requested by #30/#32. If #32 is not merged, its proposed PR template is **not** the operative template.

## Review and dispositions

The reviewer examines authoritative sources, scope, negative cases, provenance, compatibility, reproduction and limits. Record review comments and disagreements publicly where feasible. Approval by a contributor of their own work is **not** independent review. CI PASS proves only execution of the checked tests.

The competent maintainer or the body authorized under existing task-force governance selects one recorded disposition: `accepted`, `changes-requested`, `deferred`, `rejected` or `superseded`. Record the decision-maker's actual mandate/reference; where that mandate cannot be established, use `pending-authority` and do not claim adoption. The proposal does not decide who must approve changes or set quorum/consensus rules.

## Integration and publication

Before merge, record approved scope, reviewed commit, DCO/CLA requirements, current-head validation, source/target compatibility and retained evidence. Re-evaluate whenever head or base changes materially. A merged PR is a repository integration fact, not automatically a working-group endorsement of normative meaning. Release publication requires a separately recorded release authority and qualification evidence. Keep unsupported/experimental surfaces discoverable and distinguish generated output from canonical sources.

## Precedent and reassessment

For substantive method/governance decisions, link the issue/PR and accepted decision record to an existing governance precedent or propose a new one. Do not mark historical `proposed` precedents ratified without task-force action. Reopen decisions if authoritative method contracts, upstream sources, safety evidence or adopter requirements materially change.

## Worked application and falsifiable controls

- PR #32/#30: reviewability prepared with successful CI; approval/merge not inferred until verified.
- PR #22/#17: fail-closed validation prepared but unmerged; must not be treated as accepted main.
- A method change with missing sign-off or no authority evidence must not be declared accepted.
- A corpus risk scoring change without provenance/competent review must be returned for further evidence.
- A validated working-group exemplar can be accepted as an example while making **no** target assurance or normative adoption claim.

## GAP-5.1 closure gate

Require (a) competent task-force confirmation of who has final method/corpus/release decision authority or explicit mapping to pre-existing rules, (b) documented intake/triage and rejection/escalation routes, (c) reviewable evidence and compatible integration criteria, and (d) a real contribution walked through those steps with recorded acceptance. Until then, the gap remains **blocking**, despite this proposed procedure. The existing #32 contribution should be dispositioned independently.
