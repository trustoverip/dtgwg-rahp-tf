# DTG RAHP Toolkit

**Risk Assessment & Harms Prevention Task Force · Decentralised Trust Graph Working Group**
Working Draft · toolkit v0.3-dev · CC-BY 4.0

---

The RAHP Toolkit is a method for embedding human harm prevention into the design of
decentralised trust systems from the outset, plus a worked instance of that method
applied to the DTG Credential Specification.

The core argument: a standard designed without systematically asking *who gets hurt
if this is wrong* will produce a system that fails the people most exposed to its
failures. The toolkit provides the structured method for asking that question and
turning the answers into requirements a standards body can act on.

## What changed in v0.3

Everything that used to live in spreadsheets, Word documents and hand-maintained
HTML now lives in versioned YAML at the repository root. The maintained YAML is canonical. Existing workbook files are historical migration inputs; newly built exports and website pages are generated views. There is one place to change a fact, and a
validator that fails the build when the artefacts contradict each other.

The first run of that validator on the migrated v5/v6 content found 31 asymmetric
cross-references and 3 orphaned controls that no manual review had caught.

## Method and instance

The method and the worked instance are conceptually separate. Both currently live at the repository root:

| | |
|---|---|
| **Method contracts** | `lifecycle.yaml`, `vocabularies.yaml`, `rahp.schema.json` and `rahp.jsonld`. |
| **DTG instance** | `instance.yaml` and the record files it names, including `risks.yaml`, `controls.yaml` and `personas.yaml`. |

For incremental adoption, start with [ADOPTION.md](ADOPTION.md). Directory separation remains a proposed architecture, not the current physical layout.

## Quick start

```bash
pip install -r requirements.txt
python3 validate.py      # integrity check — exits 0 on a clean repo
python3 build.py         # regenerate the site, JSON-LD and exports
python3 -m unittest discover -s tests -v
# Open build/site/index.html in a browser after building.
```

## What is in the DTG instance

| Prefix | Type | Count |
|---|---|---|
| `RK-xx` | Risk | 43 risks |
| `CT-xx` | Control | 66 controls |
| `GR-xx` | Guardrail | 21 guardrails |
| `AT-xx` | Assurance test | 21 assurance tests |
| `M-xx` | Trust metric | 37 metrics |
| `US-xx` | User story | 36 user stories |
| `SC-xx` | Scenario | 33 scenarios |
| `EPIC-xx` | Capability cluster | 21 EPICs |
| `D/M/B/EC` | Persona | 16 personas |
| `REC-x` | Standards recommendation | 9 recommendations |
| `RA-xxx` | Risk acceptance | 3 risk acceptances (all `pending`) |
| `GP-xxx` | Governance precedent | 3 governance precedents |

`validate.py` checks these counts locally. The root `validate.yml` is an inactive workflow template; it is not installed under `.github/workflows/`. Do not infer automated PR validation from its presence.

## Three distinctions that matter

These terms are routinely conflated and should not be:

**Controls (`CT-xx`)** are continuous risk-reducing measures. They lower probability
or impact but do not gate phase progression.

**Guardrails (`GR-xx`)** are binary phase-gate pre-conditions. They must be satisfied
before a VTC progresses to the next bootstrapping phase. Failure is a hard stop, not
a risk-acceptance opportunity.

**Assurance tests (`AT-xx`)** are the evidence that a guardrail has been met. Each is
binary and linked to exactly one guardrail. They are the audit criterion for
conformance claims.

A fourth distinction was added in v0.3: **`Critical` severity** is not "very High". It
marks a risk whose non-zero incidence is unacceptable — legal, criminal or safeguarding
consequence. Critical risks carry no numeric score, must be gated by a guardrail, and
may not be risk-accepted. One risk currently carries it: `RK-EX04`, child safety
non-compliance / age assurance failure.

## What do you want to do?

**Adopt RAHP for another project or Working Group** — `ADOPTION.md`. Start with one bounded target and a proportionate review; you do not need to reproduce the full DTG corpus.


**New to the toolkit** — `build/site/index.html`. The persona cards are the entry
point; every other artefact connects through them.

**Reviewing a specification** — `build/site/risks.html`, sorted by score, then
`build/normative.md` for the action set.

**Deciding what goes into the spec** — `build/site/normative.html`. It shows the
recommendations and, more usefully, the 87 controls and guardrails still awaiting a
`standards_status` decision.

**Running a working group session** — `build/site/lifecycle.html`. Five stages, what
the toolkit provides at each, what it receives back, and every known gap as a tracked
record rather than a paragraph.

**Building tooling on top** — `build/rahp.json` or `build/jsonld/`. Identifiers
resolve under `https://trustoverip.github.io/dtgwg-rahp-tf/id/`.

**Using an AI assistant** — `RAHP_AI_Assisted_Process.md`, and the provenance rules
in `CONTRIBUTING.md`.

**Pressure-testing a specification** — `docs/pressure-testing-a-spec.md`. Reviews
are pinned to immutable source revisions, findings reference the RAHP risk corpus,
and control-plane classification is kept separate from finding status and resolution.
A valid review record is reproducible review metadata; it is not an assurance PASS.

## Known gaps

Gaps are tracked as records in `lifecycle.yaml` and rendered on the lifecycle
page, so they can be counted and closed rather than merely acknowledged. The two
marked `blocking`:

- **`GAP-3.1` — no formal risk acceptance workflow.** No decision on who may accept a
  risk, under what authority, for how long, with what documentation. This blocks
  `AT-17` from ever passing and blocks every record in `risk-acceptances.yaml`
  from moving beyond `pending`.
- **`GAP-5.1` — no contribution and integration governance.** No triage process and no
  defined authority for deciding what enters the next toolkit version.

Additional gaps of method severity cover community inquiry sufficiency, extreme user
completeness criteria, control adequacy thresholds, implementation guidance, and
operational intake. The runtime governance layer — metric thresholds, triage
workflows, revocation SLAs — is scoped for v0.4 and deliberately unpopulated: every
metric carries a `monitoring: null` hook.

## Contributing

See `CONTRIBUTING.md`. In short: the root YAML is canonical, `build/` is generated, every
record needs provenance, and `python3 validate.py` must exit 0.

---

*Maintained by the Risk Assessment & Harms Prevention Task Force, DTGWG.*
*CC-BY 4.0 — reuse with attribution.*
