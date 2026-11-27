# Comparative assessment and architectural recommendation

## Research conclusion

RAHP can represent the findings of a bounded, source-derived contextual reassessment without changing its specification-review contract. The constructed experiment illustrates the case for preserving assessment context and evidence applicability, but does not establish a need for a new core contract. Existing downstream mechanisms already address substantial parts of the problem. This is a contributor's research recommendation, not task-force acceptance.

## Evidence and comparison boundary

The upstream comparison uses the [TRQP examination](https://github.com/trustoverip/dtgwg-rahp-tf/blob/cfecfeb053eb0bde2a4397ce02c6d194b0cf8ae1/review/examples/standalone-trqp/README.md), [VRC examination](https://github.com/trustoverip/dtgwg-rahp-tf/blob/cfecfeb053eb0bde2a4397ce02c6d194b0cf8ae1/review/examples/vrc-v03/README.md), [TRQP/VRC generality assessment](https://github.com/trustoverip/dtgwg-rahp-tf/blob/cfecfeb053eb0bde2a4397ce02c6d194b0cf8ae1/review/examples/vrc-v03/generality.md), and [TEA examination](https://github.com/trustoverip/dtgwg-rahp-tf/blob/cfecfeb053eb0bde2a4397ce02c6d194b0cf8ae1/review/examples/tea-delegated-authority/README.md) at commit `cfecfeb053eb0bde2a4397ce02c6d194b0cf8ae1`. The Matrix comparison uses the [worked assessment](worked-assessment.md) at `db20fcf1684b4dd6415f27bd72a694a5fbafbebc`. Downstream implementation references use the v2.10.0 qualified candidate `16a2fdca4d2856083d44a11ad18cc6c008aaa5dc`, not an assumed equivalence between upstream and downstream contracts. See [release evidence](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/method/v2.10-release-evidence.json).

This is a documentary and code-level comparison of existing evidence, not a newly executed cross-engine integration. In the table, demonstrated means exercised in the bounded example; supported means an implementation or contract was inspected, not independently qualified here.

| Concern | TRQP | VRC | TEA | Matrix | Downstream |
|---|---|---|---|---|---|
| Source identity | Retained source | Two retained revisions | Retained source | README pinned; workbook copy digest only | Source/evidence contracts |
| Evidence-linked findings | Replay and source | Source propositions | Source and constructed invocation | Reference traces and draft reviews | Normalized results |
| Material change | Not exercised | Actual source revision | Not exercised | Same code; changed grant state | Freshness and impact mechanisms |
| Historical context | Retained bundle | Both reviews retained | Bounded original context | Both contexts retained | Lineage and freshness |
| Evidence applicability | Time consistency; not historical truth | Revision-bound | Capability scope | Authored contextual dispositions; not computed | Freshness; optional temporal profile |
| Dependency selection | Not exercised | Example-specific | Constructed delegation chain | Authored grant-lineage selection | Directed graph reachability |
| Comparative judgment | Not exercised | Finding transition | Not exercised | Protocol results, not comparative release judgment | Profile-bound digest |

## Findings and dispositions

### 1. Evidence identity is not current applicability

TRQP distinguishes schema validity from truth and query-time agreement; VRC demonstrates a real revised source resolving one finding while another remains open. TEA distinguishes effective delegated capability from identity and post-action obligations. Matrix extends the comparison by changing a condition without changing subject code: a historically accurate grant snapshot no longer supports a claim of present booking authority.

The downstream [freshness schema](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/method/schema/assurance-freshness.schema.json) and [freshness evaluator](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/tools/assurance_state.py) already distinguish current, potentially stale, stale, retest-required, superseded and indeterminate states based on declared effects. The [optional temporal profile](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/docs/temporal-provenance.md) distinguishes target time, knowledge cutoff, observed and recorded times, claimed effective intervals and evaluation time. It explicitly does not authenticate authority or establish historical truth.

These mechanisms are relevant but not equivalent to the Matrix's evidence-level dispositions. In particular, a contradicted observation is not merely stale, and a fresh observation can be irrelevant to the claim. Applicability must be scoped to a proposition and context. **Disposition:** existing implementation and experimental profile; no new core semantics justified. A future consumer may evaluate their composition using authoritative inputs.

### 2. Impact selection is not proof of complete coverage

The author uses the constructed grant ancestry to select requests for re-examination; no dependency selection engine is exercised. The unaffected read path is actually re-exercised, not inferred from absence of a dependency. Downstream [impact analysis](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/tools/impact.py) traverses declared directed relationships and reports affected assessments and unresolved changed nodes. Its [regression tests](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/tests/test_assurance_graph_impact.py) examine directionality, unresolved changes and incomplete graphs. A missing edge is not proof of no impact.

Reachability does not itself determine evidence sufficiency, materiality or the legality of authority. **Disposition:** existing downstream tooling is a relevant implementation reference; automatic selection is not demonstrated in upstream review v1. Keep dependency modeling example-local here. No new Matrix-specific graph or runtime monitoring is warranted.

### 3. Reassessment is not comparative acceptance

VRC records a change in finding treatment after an actual specification revision; Matrix retains observations and open draft findings in changed contexts. Neither is a universal comparative score. The downstream [comparative digest implementation](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/tools/comparative_assurance.py) and [CLI regression tests](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/blob/16a2fdca4d2856083d44a11ad18cc6c008aaa5dc/tests/test_comparative_assurance_cli.py) implement profile-bound compatibility, scope, finding matching, evidence deltas and bounded comparative judgments. [The merged comparison PR](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/pull/978) records a partially comparable release pair with improved assessment capability but indeterminate overall assurance.

No Matrix-to-digest transformation was executed. Comparable inputs require declared identity, semantics, coverage and policy; no direct equivalence between Matrix effective outcomes, RAHP finding status and comparative judgments is established. **Disposition:** existing implementation, optional future adapter only on demonstrated consumer need. No new aggregation policy or numerical score.

### 4. A shared evidence envelope is plausible, not yet warranted

The four examples recur on source/method identity, evidence references, observations distinct from inference, finding coverage, explicit limitations and preserved review history. But evidence selectors, source authentication, time semantics and applicability conditions vary. Matrix adds campaign approval, contextual binding and coverage/closure conditions not expressible natively in review v1. Its local sidecar is not a universal contract. The earlier TRQP/VRC generality assessment already recommended deferring standardization.

**Disposition:** documentation improvement now; defer any normative evidence envelope until independent consumers demonstrate stable semantics, a concrete interoperability need and compatibility tests. No native spreadsheet round-trip or full Matrix outcome engine is proposed.

## Compatibility, adoption and governance

Retain the upstream review schema, validator, canonical DTG corpus and method unchanged. Existing review consumers need no migration. A practitioner can inspect the worked example without installing the downstream controller or Registry. A future adapter must preserve source identity, explicit information loss, missing/conflicting evidence and external decision authority, and must be separately reviewed. Downstream stable engine contracts are implementation references, not automatically accepted upstream authority.

RAHP may assess evidence about a delegated grant, record changed conditions, recommend reassessment and preserve history. The legitimate authority remains responsible for issuing/revoking grants, defining duties, resolving contested state and authorizing reliance or restoration. Neither a protocol PASS, a review finding nor a comparative digest authorizes execution. Reviewers must challenge the adequacy of the selected scenarios and dependencies, not merely reproduce outputs.

## Recommendation and review boundary

No change to RAHP core, review schema, canonical vocabulary, scoring, runtime enforcement or release is recommended on the present evidence. Retain the worked assessment and crosswalk as research documentation. Broader applicability was assessed, but no extension meets the justification threshold. Any future convergence of freshness, dependency or evidence contracts belongs to a separately scoped method decision, supported by independent consumer evidence rather than this example alone.

Outstanding: confirm publisher provenance and permitted source handling for the Matrix/WLA copies, obtain independent methodological review of the crosswalk and reference experiment, and verify final contribution checks. The workbook's draft campaign was not executed; no live deployment assurance, native interchange or task-force endorsement is claimed. Prepared with AI assistance.
