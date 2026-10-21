# Adopting RAHP

RAHP can be adopted incrementally. A Working Group, specification project, implementation team, or independent reviewer does not need to reproduce the complete DTG corpus before using the method.

This guide describes a small, portable starting point for applying RAHP to another bounded target. It is an adoption guide, not a replacement for the repository's schemas, controlled vocabularies, or contribution rules.

## Start with a bounded assurance question

Begin with one target and one review question that can be stated precisely.

A useful starting target is:

- one specification or change set;
- one implementation or deployment boundary; or
- one defined workflow or interaction.

Record the exact source revision being reviewed. A branch name such as `main` is not an immutable review boundary.

For specification review, use [Pressure-testing a specification](docs/pressure-testing-a-spec.md). The review record defined under `review/` pins the target revision and records findings against the RAHP risk corpus.

## Minimum viable adoption

A first RAHP exercise does not require every artefact type in the DTG instance.

A practical initial scope is:

- one bounded target;
- a small set of affected personas or participant contexts;
- a small set of relevant risk hypotheses;
- controls where they are needed to reduce likelihood or impact;
- guardrails only where progression must stop unless a condition is satisfied; and
- recommendations or findings that can be acted on.

The objective is to produce a reviewable assurance argument, not to populate a database for its own sake.

The numbers needed will vary by target. Completeness should be judged against the review question and evidence, not against the size of the existing DTG corpus.

## Reuse before inventing

Before adding a new risk, control, guardrail, assurance test, persona, scenario, or recommendation, inspect the existing corpus.

Relevant current source files include:

- `data/risks.yaml`
- `data/controls.yaml`
- `data/guardrails.yaml`
- `data/assurance-tests.yaml`
- `data/personas.yaml`
- `data/scenarios.yaml`
- `data/recommendations.yaml`
- `data/governance-precedents.yaml`

Reuse an existing record when its proposition remains valid for the new target. Add a new record only when the existing corpus does not express the required risk, harm, control, or evidence proposition accurately.

Do not change the meaning of an existing identifier merely to make it fit a new assessment.

## Separate the method from the worked DTG instance

This repository contains both reusable RAHP method material and a worked DTG-focused corpus.

When adopting RAHP elsewhere, distinguish:

**Portable method concepts**

- lifecycle and review discipline;
- controlled terminology;
- evidence and provenance expectations;
- risk, control, guardrail, and assurance-test relationships;
- reproducible pressure-test records.

**Worked DTG content**

- DTG-specific personas;
- scenarios;
- risks and harms;
- controls and guardrails;
- recommendations;
- governance precedents.

A new adopter may reuse DTG records where they genuinely apply, but should not treat DTG-specific content as universal RAHP requirements.

The repository's current physical layout is not itself the authority boundary. Use the machine-readable schemas, controlled vocabularies, record definitions, and contribution guidance to determine what a record means.

## Choose an adoption path

### Review a specification

Use [Pressure-testing a specification](docs/pressure-testing-a-spec.md).

A review should:

1. identify the exact target revision;
2. identify affected personas and contexts;
3. test the target against relevant existing risks;
4. add new findings only where the existing corpus is insufficient;
5. identify the appropriate control plane for each finding;
6. record finding status separately from where remediation belongs; and
7. preserve resolution evidence when a finding is closed or accepted.

A valid review record is reproducible review metadata. It is not, by itself, an assurance PASS.

### Extend the RAHP corpus

Use [CONTRIBUTING.md](CONTRIBUTING.md).

New or materially changed records should carry provenance sufficient for another reviewer to understand what evidence or review activity caused the change.

Run the repository's validation process before submitting corpus changes.

### Explore the worked instance

Start with the human-readable repository entry points in [README.md](README.md), then inspect the canonical YAML records relevant to the question you are studying.

Generated views can help navigation, but generated output should not silently become the source of authority for a record.

## A small adoption workflow

A useful first cycle is:

```text
1. Define the target and immutable source revision
2. Identify affected people, roles, and contexts
3. Reuse relevant RAHP risks before creating new ones
4. Record findings and evidence
5. Determine the correct control plane
6. Produce actionable recommendations or remediation
7. Re-run the review when the target materially changes
```

This keeps adoption proportional to the assurance question.

## Control plane is not finding status

A valid finding does not imply that every mitigation belongs in the specification under review.

The pressure-test record separates:

- **control plane**: where the risk should be controlled; and
- **status**: what has happened to the finding.

For example, a finding may require governance action rather than a normative protocol change. A finding may also be resolved, risk-accepted, superseded, or remain open without changing the location where control belongs.

Preserving these dimensions avoids turning RAHP into a mechanism for pushing every identified risk into a technical specification.

## Evidence and source pinning

Assurance claims should be traceable to evidence and to the source state that was actually reviewed.

At minimum:

- pin the target to an immutable revision;
- identify the RAHP records used in the assessment;
- preserve finding identifiers;
- preserve references that justify resolution or risk acceptance;
- distinguish observed evidence from reviewer interpretation.

If the target changes materially, treat the earlier review as evidence about the earlier source state. Do not silently carry its conclusion forward.

## What a first successful adoption looks like

A first adoption is successful when another reviewer can answer:

1. What exact target was assessed?
2. Which people or contexts could be harmed?
3. Which RAHP risks were considered?
4. What findings were produced?
5. What evidence supports those findings?
6. Where does remediation belong?
7. What remains open, accepted, superseded, or out of scope?
8. What would cause the assessment to be run again?

If those questions cannot be answered from the records, the assessment is not yet sufficiently reproducible.

## Try a worked review

The [bounded membership-lifecycle exercise](review/examples/worked-adoption/README.md) shows two immutable fictional source versions, reused RAHP risks, evidence and interpretation, different control planes, structured resolution and a separately retained open finding. It uses the existing review contract and does not claim real-world assurance.

## Contribution and governance boundary

RAHP can structure findings, evidence, and proposed treatment. It does not by itself grant authority to change another specification, accept residual risk, or make a governance decision.

Those decisions remain with the authority responsible for the target system or specification.

When contributing back to this repository, follow [CONTRIBUTING.md](CONTRIBUTING.md). Anything drafted with AI assistance follows the same review path as any other contribution.

## Next steps

- To review a specification: [Pressure-testing a specification](docs/pressure-testing-a-spec.md)
- To understand the review-record format: [review/README.md](review/README.md)
- To contribute risks, controls, evidence, or related records: [CONTRIBUTING.md](CONTRIBUTING.md)
- To explore the toolkit and worked DTG instance: [README.md](README.md)

## Replay a retained real specification

After the constructed worked example, use the
[bounded TRQP examination](review/examples/standalone-trqp/README.md) to verify
retained specification bytes, reproduce positive and negative observations, and
inspect an evidence-linked review through the existing review contract.
It runs without a downstream checkout or live service. The evidence sidecar is
experimental; execution success does not establish target assurance.
