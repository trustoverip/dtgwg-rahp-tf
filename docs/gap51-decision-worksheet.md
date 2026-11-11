# GAP-5.1 governance decision worksheet (proposed)

This worksheet is a **decision aid, not an adopted governance rule**. Record actual task-force decisions with meeting/issue reference. Do not fill authority fields by inference from GitHub permissions.

| Decision | Actual authority/body (to be confirmed) | Evidence/source | Outcome |
| --- | --- | --- | --- |
| Triage/assignment of method changes | **Interim (V2):** RAHP TF | TF meeting 4 Nov 2026, D3; #43 | Contributor proposes with evidence; a reviewer who isn't the author reviews. Permanent arrangement pending |
| Schema/vocabulary acceptance | **Interim (V2):** RAHP TF | TF meeting 4 Nov 2026, D3; #43 | Needs an explicit acceptance decision, recorded in the meeting notes or on the issue. A merge or passing CI is not acceptance |
| DTG instance corpus acceptance | **Pending** | TF meeting 4 Nov 2026, D4; #44 | Not decided. Risk acceptance for the DTG instance is expected to need DTG working group authorisation |
| Review sufficiency and conflict handling | **Interim (V2):** RAHP TF, then the DTG working group | TF meeting 4 Nov 2026, D3 | Contributors don't approve their own substantive changes. Unresolved disagreements go to the TF; matters outside its mandate go to the DTG working group |
| Human accountability for AI-assisted contributions and agent-executed repository actions | **Agreed (V2):** the named human contributor | TF meeting 4 Nov 2026, D3; #32 template | Disclosure is accurate and proportionate. The named person is responsible for the work, the DCO sign-off and fixing review findings. AI output is not independent review |
| Human authorization of agent-assisted or automated releases | **Agreed in principle:** the release authority (not yet named) | TF meeting 4 Nov 2026, D1 and D3 | A person approves a release PR; GitHub Actions then publishes it. Publishing rights don't give authority |
| Exception approval / urgent corrective fixes | **Pending** | — | Undecided |
| Acceptance into the next RAHP version (method, corpus, tooling, examples, documentation) | **Agreed for V2:** RAHP TF | TF meeting 4 Nov 2026, D1; #17 | V2 = accepted baseline, completed adopter trial (Increment 7) and a qualified release. #50 and #52 don't block V2; #56, #46 and the research issues are V3 unless a finding shows the method gives a misleading result |
| Release qualification and publication | **Pending:** release authority to be named | TF meeting 4 Nov 2026, D1 | A named release authority approves a versioned release with its baseline, validation evidence, capabilities and known limitations. V2 is a TF milestone; its v0.x tag is chosen at release |
| Required checks on `main` | Repo admin (ToIP), at the TF's request | TF meeting 4 Nov 2026, D3; [#57](https://github.com/trustoverip/dtgwg-rahp-tf/pull/57) | Done: EasyCLA, DCO and `validate` are required |

A recorded GitHub merge proves integration into a branch, not the scope of delegated decision authority. The recorded 4 November decisions establish interim V2 practices, not permanent governance delegation. Preserve unresolved entries as pending, and mark GAP-5.1 resolved only after required authority decisions and a worked governance exercise are evidenced.


## Interim operating practice from 14 October 2026

The task force agreed to keep progress moving through reciprocal review and merging of one another's contributions while concentrating on the V2 baseline. Treat that as an **interim integration practice**, not as a final assignment of normative acceptance or release authority. PRs merged under that practice are integrated repository state; endorsement scope remains governed by whatever authority decision the task force records here.

Live contribution examples and their disposition are tracked in issue #43; this worksheet deliberately does not mirror changing PR states.
