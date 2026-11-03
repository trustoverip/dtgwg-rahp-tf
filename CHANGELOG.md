# Changelog

All notable changes to the RAHP Toolkit. Versions are toolkit versions; the
specification version each one was assessed against is recorded in
`data/instance.yaml`.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses a single toolkit version rather than per-artefact versions —
the previous scheme (User Stories Framework v6, Risk Register v5, HTML site
unversioned) made it impossible to say which state of the toolkit a given
review was based on.

## [Unreleased] — v0.3-dev

### Added

- **Canonical YAML data model** under `data/`. Nine artefact types migrated from
  `DTG_RAHP_Risk_Register_v5.xlsx` and `DTG_RAHP_User_Stories_Framework_v6.xlsx`
  with no content loss: 43 risks, 66 controls, 21 guardrails, 21 assurance tests,
  37 metrics, 36 user stories, 33 scenarios, 21 EPICs, 16 personas.
- **Three new record types**, extracting content that previously existed only as
  prose inside single spreadsheet cells:
  - `data/recommendations.yaml` — REC-1 to REC-9, from the Analysis & Conclusions sheet
  - `data/risk-acceptances.yaml` — RA-001 to RA-003, all `pending` (see GAP-3.1)
  - `data/governance-precedents.yaml` — GP-001 to GP-003, all `proposed`
- **`method/` directory** separating the portable RAHP method from the DTG
  instance, so another working group can adopt the method without inheriting DTG
  content.
- **`method/lifecycle.yaml`** — the five-stage standards lifecycle converted from
  hand-maintained HTML to data, with every gap callout as a tracked record
  (`GAP-1.1` … `GAP-5.5`) carrying a severity.
- **`method/vocabularies.yaml`** — controlled vocabularies for severity,
  likelihood, standards priority, standards status, normative language, control
  type, persona type and acceptance decision.
- **`tools/validate.py`** — schema, vocabulary, identifier, referential
  integrity, symmetry, invariant, orphan and README count checks. Configuration
  is read from `data/instance.yaml`; no working-group-specific logic is
  hard-coded.
- **`tools/build.py`** — generates the HTML site, JSON-LD, a JSON bundle, derived
  cross-references and `build/normative.md` from `data/`.
- **JSON-LD context** at `context/rahp.jsonld`, giving every RAHP identifier a
  resolvable IRI under `https://trustoverip.github.io/dtgwg-rahp-tf/id/`.
- **`standards_status` and `normative_language` fields** on every control and
  guardrail. All 87 are deliberately `unassigned` — assigning them is a task force
  decision, and the importer records the gap rather than guessing.
- **`monitoring` hook** on every metric, `null` pending the v0.4 runtime layer.
- **CI workflow, issue templates, PR template, CONTRIBUTING.md, this file.**
- **Two new generated views**: a standards pipeline page showing what is awaiting
  triage, and a governance page showing acceptances and precedents.
- **Review vocabularies in `method/vocabularies.yaml`.** `control_plane`,
  `finding_status` and `resolution_type`, used by specification review records
  under `review/`, now live with the other method vocabularies, and every value
  has a definition. The values are unchanged, so existing review records still
  validate. `review/validate_spec_review.py` fails if the enums in
  `review/spec-review.schema.json` drift from the vocabulary file. This was
  agreed at the RAHP TF meeting on 14 Oct 2026.

### Changed

- **Specification review accountability and example-local identifiers.** Review records now require a non-empty `reviewer` identity. This is an accountability field, not risk-acceptance authority. Example-local risk hypotheses use `EX-RK-*` identifiers so they cannot be mistaken for canonical `RK-*` corpus records. Existing repository review examples have been migrated. This is a compatibility-significant change for consumers validating review records without `reviewer`.
- **`Critical` is now a distinct severity class**, not a higher number. Critical
  risks carry no numeric score, must be gated by a guardrail, and may not be
  risk-accepted. Enforced by invariant `INV-3`. Affects `RK-EX04`.
- **Persona cross-references are now computed**, not stored. `data/personas.yaml`
  carries narrative and evidence only; links to user stories, scenarios, EPICs,
  metrics and risks are derived at build time.
- **Filenames no longer carry version numbers.** Git tags carry versions.

### Fixed

- **Metric namespace desynchronisation.** The Risk Register v5 defined M-01–M-18
  and M-31–M-37 while the User Stories Framework v6 defined M-01–M-37. The two
  workbooks disagreed about the shared identifier space they were supposed to
  share. The union is now a single file.
- **Persona cross-reference column shift.** Rows D2, D3, D5, M2 and B1 of the v6
  Persona Cross-Reference sheet had a missing Type value, shifting every
  subsequent column. Eliminated by deriving the cross-references.

### Known issues surfaced by the new validator

These are reported as warnings and are open work, not migration defects:

- **31 asymmetric cross-references** — a risk cites a guardrail that does not cite
  it back, or a guardrail cites a control that does not cite it back. Affects
  RK-SC03, RK-CR04, RK-G05, RK-HX05, RK-HX06, RK-ID06, RK-EX04, RK-EX06, RK-SC05,
  GR-03, GR-04, GR-06, GR-08, GR-12, GR-20, GR-21 among others.
- **3 orphaned controls** — CT-51, CT-52 and CT-53 are defined but referenced by
  no risk and no guardrail.
- **28 risks marked `must_address`** with no acceptance pathway available.
- **37 metrics with no runtime monitoring definition** (expected; v0.4 scope).

## Prior artefact versions

Recorded for continuity. These predate the single-version scheme.

| Artefact | Version | Date | Change |
|---|---|---|---|
| Risk Register | v5 | 2026-08 | Edge-case personas: 8 new risks (RK-HX04–06, RK-ID06, RK-EX04–06, RK-SC05), 10 new controls (CT-57–66), 3 new guardrails (GR-19–21), 3 new assurance tests (AT-19–21); `Critical` severity introduced |
| User Stories Framework | v6 | 2026-08 | EC1–EC4 edge-case personas; US-13–36, SC-13–33, EPIC-14–21, M-19–37 added |
| Workflow Reference | v1 | 2026-04 | Five-stage lifecycle with gap annotations |
| AI-Assisted Process guide | v1 | 2026-04 | Five worked examples |
| Risk Register | v4 | 2026-03 | DTG Credential Spec v0.3 review: 4 new risks, 8 new controls, 1 guardrail, 1 assurance test |
| User Stories Framework | v3 | 2026-03 | Three pivot sheets; metric IDs replace persona columns as the cross-reference standard |
| HTML reference site | v1 | 2026-03 | Initial release |
