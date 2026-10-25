# Issue #39 research: Matrix interoperability

Status: exploratory; not a canonical RAHP method, native Matrix adapter or target assurance outcome. Source investigation and a constructed deterministic experiment were prepared separately. No changes to method/, data/, review/ or build/.

## Inspected source baselines

- RAHP: trustoverip/dtgwg-rahp-tf at 448e2ff4ca7f747ca899e0e845adfe45f750f094, review/spec-review.schema.json, review/README.md and existing TRQP/VRC examples.
- Matrix: trustoverip/aimwg-agent-fiduciary-duties at 140b558791bab5bacdbe5245df0aada93d2b27bd, Assurance Matrix/README.md.
- Research tracker: https://github.com/trustoverip/dtgwg-rahp-tf/issues/39

A full Matrix workbook row-level examination, WLA source inspection and full source-tree digest verification remain unperformed. Source identities are not proof of independent authentication.

## Crosswalk and boundaries

| Matrix construct | Existing RAHP analogue | Classification | Loss / authority boundary |
|---|---|---|---|
| Threat | Risk and harm | compatible specialization | No automatic parity of risk scores, affected subjects or fiduciary duties |
| Proposition | Review finding and selected risk | partial mapping | No native proposition-specific evidence closure contract in inspected review v1 |
| Scenario | Example-local examination fixture | partial mapping | Positive/negative/adversarial intent is not in the canonical review schema |
| Campaign and run | Source-pinned review | partial mapping | Campaign coverage, adjudication and scheduling are external |
| Controls | RAHP controls/guardrails | partial mapping | Matrix control-versus-outcome distinction must be preserved |
| Evidence registry and closure | Existing example-local sidecars | partial mapping | Evidence integrity does not imply sufficiency or applicability |
| Coverage | Local tested paths | implementation gap not yet generalized | No demonstrated general Matrix campaign coverage contract |
| Dependencies and repair | VRC baseline/reassessment records | partial mapping | Automatic proposition-level dependency invalidation not demonstrated |
| Operational decision | Review recommendations | intentional non-mapping | Accountable external authority makes/enforces permission decisions |
| Relationship and fiduciary duty | External contextual authority | intentional non-mapping | Must not become RAHP core obligations by inference |

## Experimental interpretation

A hypothetical paid-booking agent with permission withdrawn before execution provides a useful test proposition: execution after revocation is a violation even if a policy gate logs denial. Cached approval and fallback retries are important adversarial cases. Missing authority evidence cannot establish PASS. An immutable historic grant remains inspectable but is stale as current permission evidence.

This is a conceptual/example-local experiment, **not** observed operational behavior. No claims of live enforcement, fiduciary assurance, adequate coverage, independent review, or native workbook conversion are made.

## Disposition

1. **Supported already:** source-pinned assessment records and historical reassessment (VRC example).
2. **Documentation opportunity:** explanatory worked permission-withdrawal assessment with explicit external authority boundary.
3. **Optional adapter:** potentially useful only after actual workbook rows and transformation-loss cases can be validated.
4. **Possible general gap:** evidence applicability, coverage and proposition-dependency lineage; insufficient evidence for a core change.
5. **Intentionally external:** fiduciary duties, operative grants, relationship state, runtime policy and human outcomes.
6. **Missing evidence:** executable real-source RAHP review of a versioned Matrix proposition, source-retained execution traces, WLA full-text check, workbook formula verification, independent interpretation and integrated CI.

**Recommendation:** no RAHP core API, schema or method modification. Do not merge this branch as a completed #39 research package. Develop and validate a real, source-pinned vertical slice first. The local constructed fixture package is separate from this tracked preliminary crosswalk.

AI-assisted research preparation; human review required. GitHub merge and validation do not grant governance authority.
