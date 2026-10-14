# Contributing to the RAHP Toolkit

The toolkit improves through use. This document tells you where things live, how
to change them safely, and what a reviewable contribution looks like.

## The one rule

**`data/` is canonical. Everything in `build/` is generated.**

If a fact is wrong on the website, in the JSON-LD, or in a spreadsheet export,
the fix goes in `data/` and you re-run `python3 tools/build.py`. Never edit a
generated file — your change will be silently destroyed by the next build.

## Repository layout

```
method/            The RAHP method. Portable. Another working group keeps this.
  lifecycle.yaml     Five lifecycle stages, their evidence requirements, and every known gap
  vocabularies.yaml  Controlled vocabularies (severity, standards status, persona type, …)
  schema/            JSON Schema for every record type
data/              The DTG instance. Another working group replaces this.
  instance.yaml      Namespaces, cross-reference edges, invariants — drives the validator
  risks.yaml  controls.yaml  guardrails.yaml  assurance-tests.yaml
  metrics.yaml  user-stories.yaml  scenarios.yaml  epics.yaml  personas.yaml
  recommendations.yaml  risk-acceptances.yaml  governance-precedents.yaml
tools/             validate.py · build.py · import_xlsx.py · verify_migration.py (migration only)
context/           JSON-LD context
review/            Specification-review record schema, validator and examples
docs/              Data model and pressure-testing guide
tests/             Regression tests (python3 -m unittest discover -s tests)
archive/           Historical spreadsheets, documents and builds. Read-only.
build/             Generated. Not committed except on tagged releases.
```

## Setup

```bash
pip install -r requirements.txt
python3 tools/validate.py     # must exit 0 before you start
```

The [RAHP validation workflow](.github/workflows/validate.yml) runs corpus, regression, specification-review and build checks. See [validation evidence](docs/validation.md) for retained reports and limits.

## Making a change

1. Edit the relevant file in `data/`.
2. Add a `provenance` block to every record you add or materially change:

   ```yaml
   provenance:
     source: "DTG Credential Spec v0.4 §5.2"   # what you were reading
     triggered_by: "spec-review-2026-09"        # the activity that surfaced it
     contributor: "your name or handle"
     imported: 2026-09-14
   ```

   Provenance is not bureaucracy. It is how a reader in two years works out
   whether a risk score reflects evidence or someone's Tuesday afternoon.

3. Run `python3 tools/validate.py`. Fix errors. Read the warnings — most of them
   are telling you something true.
4. Run `python3 tools/build.py` if you want to see the change in the site.
5. Open a PR using the template. Paste the validator summary line into it:

   ```
   python3 tools/validate.py --summary
   ```

## Adding each record type

**A risk (`RK-xx`)** needs: a category, a lifecycle phase, a description that
says what goes wrong, a harm description that says who is hurt, severity and
likelihood, and at least one metric that would move if it happened. A risk you
cannot measure is an opinion.

**A control (`CT-xx`)** reduces probability or impact. It must link to at least
one risk, and — transitively, through that risk — reach at least one metric. The
validator enforces this: a control that reaches no metric is unmonitorable.

**A guardrail (`GR-xx`)** is a binary phase-gate pre-condition. It must have at
least one assurance test. Guardrails are hard stops, not aspirations. If you find
yourself wanting to write "should", you are describing a control.

**An assurance test (`AT-xx`)** is binary pass/fail evidence for exactly one
guardrail. State the pass criterion so precisely that two people testing
independently would agree on the result.

**A metric (`M-xx`)** is a measurement instrument. It belongs to the shared
identifier space that links every artefact — never reuse an M number.

**A persona** is an analytical instrument, not a marketing profile. Give it
realistic context, documented objectives and vulnerabilities, and cite evidence
with a resolvable URL. Do not write cross-references into `personas.yaml` — they
are computed at build time from the records that reference the persona.

**A recommendation (`REC-xx`)** proposes a change to the target specification.
Set `class` to `normative`, `recommended` or `process`, and `status` truthfully.

**A risk acceptance (`RA-xxx`)** — read the header of `data/risk-acceptances.yaml`
before adding one. There is currently no agreed acceptance authority, so every
record is `pending`. Do not invent one.

**A governance precedent (`GP-xxx`)** records *why* a decision was made, so a
future contributor does not silently reverse it. Add one whenever a working group
decision changes the shape of the toolkit.

## Severity and Critical

`Critical` is not "very High". It marks a risk whose non-zero incidence is
unacceptable — legal, criminal or safeguarding consequence. Critical risks have
no numeric score, must be gated by a guardrail, and **may not be risk-accepted**.
The validator enforces this.

## Naming conventions

- Files in `data/` and `method/`: lowercase, hyphenated, `.yaml`.
- No version numbers in filenames. Git tags carry versions; `CHANGELOG.md`
  explains them. (The old `_v3`/`_v4`/`(1)` filenames are exactly what this rule
  is here to prevent.)
- Identifiers never change meaning. If a risk is superseded, retire the ID and
  record why — do not reuse it.

## Using an AI assistant

`RAHP_AI_Assisted_Process.md` covers this in detail. Two rules apply here:

- Anything an assistant drafts enters the repository through the same PR review
  as anything else. There is no fast path.
- Set `provenance.contributor` to `"<your name> (AI-assisted)"` when a record was
  substantially drafted by an assistant. This is not a warning label; it lets a
  reviewer calibrate how much independent verification the record needs. Risk
  scoring, guardrail verification and governance decisions are not assistant work.

## Review expectations

A PR is ready when: `validate.py` exits 0, every new record has provenance, and
the description says what triggered the change. A PR that changes a risk score
should say what evidence moved it.
