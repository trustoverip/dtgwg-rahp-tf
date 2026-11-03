# Contribution and integration governance — GAP-5.1 proposal

**Status: proposed for task-force approval.** This document defines a usable procedure and accountability questions, but does not confer decision rights. Accepted task-force governance and repository rules prevail. The task force must identify its decision authority before this protocol can be marked operational.

## Intake and routing

1. Submit an issue/PR describing the problem, affected target (method, DTG instance, exemplar, validator, tooling, documentation, or governance), evidence, version impact and reproduction commands. An issue may be used for a decision that does not require code. Stage-5 maintenance triggers, including periodic extreme-user review and reports raised outside GitHub, must enter the same triage record once the task force identifies an accessible intake route; absence of a GitHub account must not silently exclude a harm report.
2. Classify the change. Upstream owns method/schema/vocabulary and generic adoption requirements. The DTG instance corpus in `data/` has its own acceptance and risk-decision questions, tracked in the #43 decision worksheet; repository write access alone does not establish those authorities. A target's own working group owns its specification and risk decisions; downstream controllers, routing and deployment controls are not automatically upstream components.
3. Associate the contribution with a tracked issue, identify dependencies and distinguish accepted upstream contracts from proposals. Do not build on an unmerged branch without explicitly recording that dependency.
4. Include the proportional reviewability information requested by #30/#32. If #32 is not merged, its proposed PR template is **not** the operative template.

## Review and dispositions

The reviewer examines authoritative sources, scope, negative cases, provenance, compatibility, reproduction and limits. For substantially AI-assisted work, record what a person independently checked or reproduced; repeated model agreement is not independent review. Record review comments and disagreements publicly where feasible. Approval by a contributor of their own work is **not** independent review. CI PASS proves only execution of the checked tests.

### AI-assisted and agent-executed contributions

Material AI assistance must be disclosed in the PR or linked contribution record, identifying the affected work and the human contributor responsible for verifying it. Agent-executed repository actions must also identify the agent's role, the actions taken and the responsible human sponsor. Routine incidental assistance need not be itemized. Do not disclose private prompts, credentials or other sensitive material.

The responsible human must examine sources and substantive claims, reproduce consequential tests or observations where practical, and record what was actually checked and what remains unverified. AI-generated output, agent execution and repeated model agreement do not constitute independent review. The contribution follows the same independent review, provenance, DCO/CLA and acceptance requirements as other work; the existing `RAHP_AI_Assisted_Process.md` and `CONTRIBUTING.md` remain applicable. Neither a contributor nor an agent acquires decision authority through tool access or automation.

The person or body authorized under existing task-force governance selects one recorded disposition: `accepted`, `changes-requested`, `deferred`, `rejected` or `superseded`. Where decision authority has not been established, record `pending-authority` as an authority state, not as acceptance. Record the decision-maker's actual mandate/reference; where that mandate cannot be established, use `pending-authority` and do not claim adoption. If author and reviewer cannot resolve a substantive disagreement, preserve both positions in the PR or linked issue, defer the disputed decision and refer it to the RAHP Task Force for disposition. Any further escalation to the DTG Working Group follows its established governance; this proposal does not invent an appeal authority. Repository merge permissions are not a tie-breaker. Until that authority is recorded, the disposition remains `pending-authority`. The proposal does not decide who must approve changes or set quorum/consensus rules.

## Integration and publication

Before merge, establish approved scope, reviewed commit, applicable DCO/CLA requirements, current-head validation, relevant compatibility and evidence. The PR, reviews and CI results ordinarily constitute the record; do not require a separate worksheet for each routine change. Re-evaluate whenever head or base changes materially. A merged PR is a repository integration fact, not automatically a working-group endorsement of normative meaning. Release publication requires a separately recorded release authority and qualification evidence. Keep unsupported/experimental surfaces discoverable and distinguish generated output from canonical sources.

### AI-assisted and automated release engineering

AI assistants, agents and workflows may prepare version proposals, release notes, validation evidence and publication artifacts, or execute an authorized publication. Material assistance and agent-executed release actions must be traceable in the release PR or equivalent release record, including the accountable human maintainer, reviewed source revision, version/compatibility rationale, validation evidence, publication workflow and known limitations.

An identifiable human acting under documented upstream release authority must approve the release decision, including its scope and version impact. An automated workflow may carry out that decision against the qualified revision; successful execution does not independently establish authorization, methodological assurance or acceptance of normative changes. The responsible maintainer oversees failure handling and corrective action within their authority. This proposal does not itself confer release authority or mandate a particular release trigger.

## Precedent and reassessment

For substantive method/governance decisions, link the issue/PR and accepted decision record to an existing governance precedent or propose a new one. Do not mark historical `proposed` precedents ratified without task-force action. Reopen decisions if authoritative method contracts, upstream sources, safety evidence or adopter requirements materially change.

## Worked application and falsifiable controls

Current contribution examples and their changing repository state are tracked in #43 and the decision worksheet rather than frozen into this durable procedure.

- A method change with missing sign-off or no authority evidence must not be declared accepted.
- A corpus risk scoring change without provenance/competent review must be returned for further evidence.
- A validated working-group exemplar can be accepted as an example while making **no** target assurance or normative adoption claim.

## GAP-5.1 closure gate

Require (a) competent task-force confirmation of who has final method/corpus/release decision authority or explicit mapping to pre-existing rules, (b) documented intake/triage and rejection/escalation routes, (c) reviewable evidence and compatible integration criteria, and (d) a real contribution walked through those steps with recorded acceptance. Until then, the gap remains **blocking**, despite this proposed procedure. The existing #32 contribution should be dispositioned independently.
