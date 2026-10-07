## What changed

<!-- One or two sentences. -->

## Artefact IDs affected

<!-- e.g. RK-ID07 (new), CT-67 (new), GR-07 (updated), M-12 (updated) -->

## Provenance — what triggered this change?

<!-- Spec section, discussion thread, practitioner report, threat intelligence,
     review session. Every new or materially changed record needs a provenance
     block in the YAML as well. -->

## Validation output

<!-- Paste the output of: python3 tools/validate.py --summary -->

```
```

## Checklist

- [ ] `python3 tools/validate.py` exits 0
- [ ] Every new/changed record has a `provenance` block
- [ ] New guardrails have an assurance test; new controls reach a metric
- [ ] No generated file under `build/` was edited by hand
- [ ] If a risk score changed, the evidence for the change is stated above
