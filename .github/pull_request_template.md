## What changed

<!-- One or two sentences describing the proposition and the resulting change. -->

## Why

<!-- Issue, task-force decision, defect, evidence, adoption need or other trigger. -->

## Scope

<!-- Identify the affected surfaces: method, data, review contract, tooling, docs, governance, CI, examples. State important non-goals. -->

## Evidence and reproduction

<!-- List the exact commands, tests, fixtures or inspection steps an independent reviewer should use. Do not report a PASS that was not actually observed. -->

```sh
# example
python3 -m unittest discover -s tests
```

## Assurance / review questions

<!-- Answer proportionately for substantive method, review, tooling or convergence changes. Use "not applicable" only when genuinely irrelevant. -->

1. Which assurance layer or repository responsibility does this change affect?
2. What evidence does it produce, consume or validate?
3. What RAHP judgment does it enable?
4. What judgment does it deliberately avoid making?
5. Which risks, controls, vocabularies, review records or governance rules are affected?
6. What remains experimental, example-local, unresolved or subject to task-force decision?
7. What should an independent reviewer rerun or inspect to reproduce the claim?

## Compatibility and limitations

<!-- State schema/API/semantic compatibility, migration requirements, known limitations, residual risk or evidence gaps. -->

## Corpus changes, if applicable

<!-- Complete this section only when canonical records under data/ are added or materially changed. -->

**Artefact IDs affected:**  
<!-- e.g. RK-ID07 (new), CT-67 (new), GR-07 (updated), M-12 (updated) -->

**Provenance:**  
<!-- Spec section, discussion thread, practitioner report, threat intelligence or review session. Every new or materially changed canonical record needs a provenance block in the YAML as well. -->

## Checklist

- [ ] The PR explains why the change exists and what remains outside scope.
- [ ] Reproduction or validation steps are sufficient for a reviewer who did not author the change.
- [ ] Reported validation results were actually observed; missing evidence remains visible.
- [ ] Compatibility or migration impact is stated when semantics or contracts change.
- [ ] No generated file under `build/` was edited by hand.
- [ ] If canonical corpus records changed, every new/materially changed record has provenance.
- [ ] If a new guardrail or control was added, its assurance-test/metric relationships are valid.
- [ ] If a risk score changed, the evidence for the change is stated above.
