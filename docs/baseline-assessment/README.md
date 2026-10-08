# Shared RAHP testing baseline: bounded fit assessment

Assessment for [issue #17](https://github.com/trustoverip/dtgwg-rahp-tf/issues/17), observed 2026-10-08. Contributor: Codex (AI-assisted preparation). This is a proposal and execution record, not a task-force decision or independent human review.

## Recommendation and adopter

Start with a working-group specification reviewer who needs to examine one bounded question at an immutable revision, connect observations to the group's risk corpus, retain reproducible evidence, and identify who can resolve each finding. A repository maintainer supports reproduction and review; a governance authority decides risk acceptance separately.

The smallest useful contribution is a **real-source replay adapted to the existing upstream review contract**, with positive and negative fixtures. The downstream standalone TRQP exercise demonstrates source integrity, schema conformance and a semantic counterexample without a running service. It is a candidate for adaptation, not an approved transfer. The maintainer's request for a VRC Spec 0.3 worked example is also relevant; the task force should choose which subject to use first.

A shared baseline should let another group pin its target and method context, use a bounded procedure, record findings and evidence, reproduce checks, and understand omissions. Successful checks establish the stated structural or replay claims only. They do not establish certification, target assurance PASS, independent review, authorization to act, or risk acceptance. Revocation and delegation behavior require deployment evidence when they are within the examination scope.

## Immutable sources and evidence

| Source | Revision | Boundary |
|---|---|---|
| [Upstream task-force repository](https://github.com/trustoverip/dtgwg-rahp-tf/tree/ab191485b48bca805ea2cc962c2ea9476a65db66) | `ab191485b48bca805ea2cc962c2ea9476a65db66` | Accepted `main`, before this assessment |
| [Downstream toolkit](https://github.com/sankarshanmukhopadhyay/rahp-toolkit/tree/af58247e83d0aff4d47650d929bfc6280d9e41d3) | `af58247e83d0aff4d47650d929bfc6280d9e41d3` | Candidate implementation, not upstream authority |
| [Pending validation CI, PR #14](https://github.com/trustoverip/dtgwg-rahp-tf/pull/14) | `2457428547b95d5511b49bae8978235ffa14fc24` | Open at inspection; exclude from accepted baseline |

[inventory.json](inventory.json) contains eight candidate groups, 46 individually identified source assets, immutable links and SHA-256 digests. Each group records interfaces, dependencies, observed consumers, upstream overlap, limits and proposed disposition. Consumers are those located in inspected code/docs/tests; external users were not surveyed. This is a bounded fit assessment, not a full downstream security or portability audit.

[execution.json](execution.json) retains commands, revisions, interpreter/dependency versions, exit codes and outputs. `<workspace>` in paths is a sanitized local checkout root. The build command uses a temporary sibling output directory. Digests identify inspected bytes; they do not establish source authenticity or author approval.

## What upstream already provides

| Surface | Current responsibility | Gap or constraint |
|---|---|---|
| `method/lifecycle.yaml`, `method/vocabularies.yaml`, `method/schema/rahp.schema.json` | Portable method stages, controlled corpus vocabulary, structural records | Review `control_plane` values currently live separately in the review schema |
| `data/instance.yaml`, `data/*.yaml` | DTG corpus, namespaces, references and invariants | Adopters replace instance data; existing review examples are connected to this corpus |
| `tools/validate.py` | Corpus schemas, vocabularies, references and invariants | Does not discover/validate specification-review records; optional missing jsonschema currently produces a warning and skips schema checks |
| `review/spec-review.schema.json`, `review/validate_spec_review.py` | Review structure, full Git revision, unique finding IDs, risk resolution | Structural validation does not verify truth, remote source availability, resolution authority or evidence bytes |
| `review/examples/`, `tests/test_spec_review.py`, `tests/test_worked_adoption.py` | Minimal positive/negative fixtures and fictional two-version reassessment | Real-source replay and unfamiliar-adopter evidence remain useful additions |
| `tools/build.py`, `context/rahp.jsonld` | Derived site/JSON-LD outputs | Successful generation is not proof of deployed Pages behavior |
| `ADOPTION.md`, `docs/data-model.md`, `docs/pressure-testing-a-spec.md`, `CONTRIBUTING.md` | Adoption, model, review and contribution instructions | Independent review/merge ownership remains a GAP-5.1 decision |
| Root `validate.yml`, pending PR #14 | Inactive template on accepted main; proposed installed CI | No installed `.github/workflows/` exists at the accepted source pin |

The initial local test attempt lacked jsonschema: review tests failed to import, while the corpus summary returned zero errors with 33 warnings because schema validation was skipped. After installing the repository requirements, all recorded checks ran with jsonschema present and the corpus had 32 warnings. Only the fully provisioned run is used as successful evidence. This is an existing behavior to consider in a separate hardening increment, not silently repaired in this assessment.

## Candidate disposition register

All dispositions below are **contributor recommendations pending maintainer decision**. Detailed source paths and evidence are in the inventory.

| ID | Candidate | Proposed disposition | Adopter value, fit and maintenance consequence |
|---|---|---|---|
| C1 | Standalone TRQP retained-source replay and fixtures | Redesign with maintainers; first increment candidate | Teaches the difference between source integrity, schema validity and semantic correctness. Keep observations, hashes, attribution and negative cases; express findings in upstream records rather than import downstream Pages markup/catalogue references. Three tests and expected replay passed. |
| C2 | Downstream pressure-test validator | Redesign with maintainers | Useful record checks, but it scans example/instance/corpus directories and consumes six catalogue layers plus different vocabularies. A direct copy creates overlapping validators and unresolved semantic authority. Inspected, not executed here. |
| C3 | Engine result contract, retention and conformance fixtures | Defer | Missing-source and evidence-integrity negative tests are useful ideas. Full contract revision 1.3 adds lifecycle/evaluation/terminal responsibilities beyond a bounded review. Four focused tests passed; no full engine conformance claim. |
| C4 | Evidence provenance/freshness/delta contracts | Defer | Makes reassessment explicit, but needs an agreed relationship to upstream review history and conclusion semantics. Six freshness/transition tests passed; schema CLI and live freshness were not evaluated. |
| C5 | Portable harm-to-evidence catalogue | Defer | Could reduce instance coupling. Requires mapping of pattern IDs to upstream risk/control/guardrail/test records and a named vocabulary owner. Located cache tests are not domain-portability evidence; not run here. |
| C6 | Assessment/autonomous controllers and telemetry | Retain downstream | Introduces terminal outcomes, specialists and operational state that the shared review baseline does not need. Existing tests located; controller behavior not executed here. |
| C7 | Portfolio routing and DTG policy | Retain downstream | Repository targeting, qualification and toolkit integration are instance/automation concerns. A group can review a specification without portfolio routing. Self-test inspected, not run. |
| C8 | Expanded downstream corpus and build/validator replacement | Reject bulk transfer | Upstream already owns these surfaces. Replacing them would import instance assumptions and duplicate authority. Specific justified records or tests can be proposed separately; no equivalence is claimed. |

No candidate is recommended for unconditional transfer as-is. That conclusion follows from overlap and dependencies, not from a presumption that downstream code is unsuitable.

## Review-model consolidation dependency

The maintainer suggested moving `control_plane` into `method/vocabularies.yaml` and including review checks in `tools/validate.py`. The proposal is reasonable to examine but is not accepted architecture.

The upstream review uses lowercase control planes such as `specification` and `runtime-control`, separately from `status: open|in_progress|resolved|risk_accepted|out_of_scope|superseded`. The downstream pressure-test vocabulary uses human-facing disposition labels and allows statuses including `in-progress`, `complete` and `monitoring`. These fields are not drop-in equivalents. Upstream corpus `control_type` and `standards_status` describe different properties again.

Before consolidation, decide:

1. Whether method vocabulary becomes authoritative for the existing review values, and how schema constraints remain synchronized without maintaining two conflicting lists.
2. Whether the corpus CLI calls the existing review validator or validation logic is extracted into a shared library. Compare composability and maintenance before deciding; neither requires merging record semantics.
3. Which review files are selected, how caller-supplied risk corpora work, and how intentionally invalid fixtures are excluded from normal validation but asserted in negative tests.
4. How review errors/warnings appear in existing CLI/JSON reports and exit codes, and how old commands and records remain compatible.
5. Who owns vocabulary interpretation and accepts changes. A valid reference to a risk-acceptance record is not verification of the accepting authority.

Pressure tests for any later implementation should include invalid control plane, unknown risk, duplicate finding ID, mutable revision, resolved-without-resolution, intentionally invalid example discovery, a non-DTG risk corpus, missing validation dependency and conflicting vocabulary declarations. Existing upstream tests already cover several of these; reuse them first.

## Smallest next contribution proposal

**Working title:** `test(adoption): add a bounded real-source specification replay`.

**Adopter:** working-group reviewer of one specification question. **Proposed contributor:** issue assignee, with AI disclosure where applicable. **Maintenance owner:** task-force repository maintainers, subject to explicit acceptance; no new owner is appointed by this assessment. **Independent reviewer/merge authority:** task-force decision under GAP-5.1.

**Scope:** one immutable target snapshot, one existing-format review record, retained licensed source or an agreed acquisition strategy with digests, a small offline replay, expected results and negative tests. Proposed paths are `review/examples/real-source/` and `tests/test_real_source_review.py`; these names are proposals, not additions made here. Add adopter instructions close to the example and link from `review/README.md` after the increment is accepted.

**Non-goals:** catalogue/schema/vocabulary migration, consolidated CLI, live service assurance, controllers, DPIP/Interop integration, automated risk acceptance, repository restructuring and publication workflow changes.

**Acceptance criteria for that separate increment:**

- [ ] Maintainers select the target (TRQP replay adaptation or VRC 0.3) and agree the review/maintenance boundary.
- [ ] Target and method context have immutable pins; retained source has path/digest/license provenance.
- [ ] Findings conform to the current upstream review schema and reference justified existing risks; any mapping gap is stated rather than fabricated.
- [ ] Replay independently demonstrates its observations, with expected output and tampering/invalid-input negative cases.
- [ ] Observation, inference, harm hypothesis, control plane and human disposition remain distinguishable.
- [ ] Missing runtime, authority, delegation and post-revocation evidence is explicitly unassessed wherever relevant.
- [ ] An unfamiliar adopter can follow documented commands in a fresh checkout without downstream modules or undocumented knowledge; retain that trial's results.
- [ ] Upstream regression/corpus/build checks pass; warnings and evidence omissions remain visible.
- [ ] Independent review and maintainer acceptance are recorded; neither is inferred from CI.

**Validation plan:** validate the new record through `review/validate_spec_review.py`; run replay and negative tests, then all upstream tests, corpus validation and a temporary-output build. For TRQP, adapt the demonstrated source-tampering rejection and schema-valid/time-mismatch case. For VRC, establish equivalent claims from its actual pinned source first. No new implementation issue is created until target, owner and scope are agreed.

**Compatibility:** use the existing review contract, preserve all current commands and records, and avoid implicit downstream risk-ID imports. **Release:** none for this assessment; any later accepted capability follows upstream release policy.

## Execution evidence and reproduction

| Check | Observed result | Limit |
|---|---|---|
| Upstream corpus | Exit 0; 0 errors, 32 warnings | Warnings retained, no risk acceptance implied |
| Upstream test suite | 12 tests passed | Contract/fixture checks, not target truth |
| Minimal upstream review | Exit 0 | Record validity only |
| Temporary upstream build | Exit 0 | Generated outputs, no deployment verification |
| Downstream standalone TRQP | 3 tests passed; replay matches expected output | Retained source and constructed fixtures, not service traffic |
| Downstream engine contract | 4 tests passed | Selected result/retention assertions, not full engine suite |
| Downstream freshness/delta | 6 tests passed | Pure-function semantics, not freshness policy approval |

Reproduce from separate checkouts of the source pins above after `python3 -m pip install -r requirements.txt` in the relevant repository. Dependency versions for the observed run are recorded in execution.json; repository lower-bound requirements are not a lockfile.

Upstream:

```bash
python3 tools/validate.py --json
python3 -m unittest discover -s tests -v
python3 review/validate_spec_review.py review/examples/minimal-review.yaml
python3 tools/build.py --out /tmp/rahp-baseline-build
```

Downstream:

```bash
python3 -m unittest discover -s tests -p test_standalone_trqp.py -v
python3 -m unittest discover -s tests -p test_engine_contract.py -v
python3 -m unittest discover -s tests -p test_evidence_freshness_delta.py -v
python3 examples/standalone-trqp/replay.py --check
```

No full downstream suite, external-adopter trial, live runtime, independent review or deployed Pages check was performed. The focused runs support fit assessment, not broad maturity certification.

## Decisions and issue completion boundary

| Decision | State | Authority / next evidence |
|---|---|---|
| Start with bounded working-group specification review | Proposed | Task force confirms or refines adopter |
| Choose first real-source subject | Open | Maintainers choose TRQP adaptation or VRC 0.3 |
| C1–C8 dispositions | Proposed | Maintainers accept, revise or reject with rationale |
| Vocabulary and validator consolidation | Open dependency | Joint design decision and compatibility tests |
| Independent reviewer, maintenance and merge rights | Open dependency | GAP-5.1 task-force discussion |
| Installed CI baseline | Waiting on PR #14 | Maintainer merge decision and refreshed default-branch evidence |

Assessment inventory, upstream mapping, proposed dispositions, validation evidence and next-increment proposal are supplied. Task-force decisions and actual adoption evidence remain outstanding. Keep #17 open until those decisions are recorded or its scope is explicitly narrowed by maintainers. Refresh source/PR state before executing a transfer: mutable `main` and PR state may have advanced since this snapshot.

This assessment changes documentation and evidence only. It transfers no code and changes no schema, corpus, enforcement, authority, workflow or repository layout.
