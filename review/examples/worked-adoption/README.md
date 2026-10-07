# Worked adoption: a bounded membership lifecycle review

This is a fictional training exercise using the existing `rahp-spec-review/v1` contract. It demonstrates how to apply RAHP; it is not an assessment of DTG, an implemented service or real governance. All participant contexts and judgments are synthetic and contributor-authored. No interviews, independent human review, actual governance adoption or remedy are claimed.

## Question and scope

**Does the target document state revocation safeguards and renewal behavior clearly enough to identify actionable gaps?**

The target is two small membership-lifecycle documents. Review documentary coverage of revocation and expiry only. Cryptographic algorithms, issuer eligibility, deployment effectiveness and actual fairness are outside scope. A valid signed revocation may still exclude a member without adequate governance; expiry rejection may be technically correct while leaving a member without a usable renewal path.

Member, operator and reviewer contexts are declared in the target. They are contextual descriptions, not new canonical persona records or empirical evidence. Reuse existing risks: `RK-CR01` (revocation without due process) and `RK-CR02` (expiry without a renewal path). Their meanings remain owned by the maintained corpus.

## Immutable inputs

| Input | Exact pin |
|---|---|
| Training version 1 | [target-v1.md](https://github.com/trustoverip/dtgwg-rahp-tf/blob/62c52b3f5b1768dcfc1f6fab598c8021f72e057c/review/examples/worked-adoption/target-v1.md), commit `62c52b3f5b1768dcfc1f6fab598c8021f72e057c` |
| Training version 2 | [target-v2.md](https://github.com/trustoverip/dtgwg-rahp-tf/blob/9ab60bc285adeeeb8e2e743bda5b609736ad56b6/review/examples/worked-adoption/target-v2.md), commit `9ab60bc285adeeeb8e2e743bda5b609736ad56b6` |
| RAHP method/corpus context | `v0.3-dev` at `e3ad6648ebc8c1a9a625dbdbefc8ba68b5bbd1e0`, including `risks.yaml` and `review/spec-review.schema.json` |

The two source documents were committed before these review records. The target repository is this repository because it hosts the fictional exercise, not because its toolkit implementation is the subject of the findings.

The review schema stores a method version label, not a separate immutable corpus revision. This companion packet preserves the exact corpus pin without adding fields to the contract. When repeating the exercise, use that corpus or explicitly record changed RAHP context; do not silently substitute current risks.

## First review: SR-101

Read [target-v1.md](target-v1.md), then inspect [baseline-review.yaml](baseline-review.yaml).

| Finding | Source evidence | Interpretation and harm | Control plane / status |
|---|---|---|---|
| F-001 / RK-CR01 | T1 requires authenticated revocation and timestamp/identifier recording, and explicitly omits notice, rationale, appeal and restoration | A member may be excluded without a usable challenge path. An issuer signature proves neither a legitimate decision nor due process | governance / open |
| F-002 / RK-CR02 | T2 requires expiry rejection and explicitly omits a renewal interface, renewal window and pending-request behavior | A member may lose access through an unresolved lifecycle gap even when expiry verification is correct | specification / open |

These findings are bounded observations about the training text. An omitted safeguard in this document is not proof that an external organization lacks one. The exercise explicitly excludes external policy and implementation evidence.

Treatment belongs at different layers. F-001 needs a governed decision and challenge procedure; adding more cryptography does not supply that procedure. F-002 needs a defined lifecycle interface/behavior and cannot be closed merely by adding an appeal policy. The source author and actual target authority would normally decide the treatment; this exercise invents neither real mandate nor accepted residual risk.

## Changed source and reassessment: SR-102

Version 2 adds T3's fictional companion governance procedure, while leaving T2's renewal gap open. This material source change triggers a new review.

Read [target-v2.md](target-v2.md), then inspect [reassessed-review.yaml](reassessed-review.yaml). Preserve SR-101 unchanged.

| Finding | New evidence | Disposition and limit |
|---|---|---|
| F-001 | T3 states notice/reasons, emergency exception limits, accessible review, separation from the original decision maker and recorded restoration | governance / resolved **for the documentary gap only**. Structured resolution cites the pinned source. Procedure enactment, reviewer independence, successful notice and effective restoration remain unassessed |
| F-002 | T2 remains without a renewal interface or pending-request behavior | specification / open. A governance change does not discharge this separate obligation |

F-001's control plane remains `governance` when its status changes. F-002 stays visible rather than being swept into a favorable summary. No `risk_accepted` record is manufactured.

The repeated finding labels are paired manually within this exercise. The schema requires uniqueness within each review, not global finding identity or an automatic cross-run lineage engine. SR-101 and SR-102 are different review identities tied to different immutable subjects.

## Reproduce

From a checkout containing this packet, install `requirements.txt`, then run:

```bash
python3 review/validate_spec_review.py review/examples/worked-adoption/baseline-review.yaml
python3 review/validate_spec_review.py review/examples/worked-adoption/reassessed-review.yaml
python3 -m unittest discover -s tests -v
```

For a cold reading, write down each finding's source passage, inference, control plane, disposition and residual before reading the review YAML. Compare your judgment with the preserved authored example; disagreements are useful and should remain attributable in a real review.

Expected validation: both records are schema-valid, target revisions have immutable-SHA syntax, finding IDs are unique within each record, referenced risks exist and the resolved finding has structured resolution metadata.

The validator **does not** fetch the target commit, prove the evidence supports the judgment, verify decision authority, or establish effectiveness. A 40-hex placeholder can satisfy syntax; this packet uses actual accessible commits and separately binds the artifact paths. Human/source inspection remains necessary.

## Next cycle

Reassess when renewal behavior changes, T3 changes, the participant/context assumptions materially change, or the selected RAHP risks/method change. Pin the new subject and create a new review identity. Preserve previous reviews and explain which findings changed, remained open or became unsupported.

A valid packet leaves another reader able to challenge the scope, evidence, inference and disposition. It does not turn schema validity or a closed documentary finding into whole-target assurance.
