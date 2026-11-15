# Example: Arthur and Margaret, a persona-led review of an implementation

**Status: checked by a person.** Nicky Hickman confirmed the findings on 11 Nov 2026. She hasn't re-checked the code evidence, and no independent examination has been done yet. Passing the RAHP checks means the record is well formed, not that its findings are right.

**What was reviewed:** an open-source trust-community implementation stack. It isn't named here. The review record and evidence pin its three repositories to exact commits, and are kept privately.

## The question

Arthur has early-stage dementia. He has capacity now, but it comes and goes and will decline. Margaret, his partner and carer, holds registered lasting powers of attorney. Can Arthur stay a member of his community, and can Margaret act for him lawfully, visibly and within limits? Does the system protect him?

## How the review was done

This review started from **people, not from code**. That's the route a human-focused, non-technical reviewer would take.

1. **The people** (RAHP personas EC2a and EC2b) and their situations (scenarios SC-28 and SC-29), user stories (US-29 to US-32), risks (RK-HX04, RK-HX05, RK-HX06, RK-SC05) and proposed safeguards (CT-57 to CT-61), all taken from the RAHP catalogue.
2. **What the stack offers them,** found by searching its code and documentation.
3. **Eight findings,** drafted with AI help, then confirmed by the reviewer acting as Arthur and Margaret's advocate.
4. **A review record,** checked with RAHP's validator, plus an evidence file linking each finding to its sources.

| Step | Who |
|---|---|
| Choose people and situations | Human |
| Gather catalogue context; search the code and docs; draft findings | AI |
| Pin the repositories; validate the record; hash the evidence | Machine |
| Confirm, change or drop each finding | **Human, by rule** |
| Independent examination | **Human, by rule.** Not done yet |

## Findings, by where the fix belongs

| Where | Finding |
|---|---|
| Technical standards | **F-001** No way to represent a legal attorney, so the system can't tell Margaret from an account takeover |
| Technical standards | **F-004** Notices go only to the member, so Arthur's right to appeal is lost once he can't use his account. Any second recipient must be his own, withdrawable choice, because it could also expose someone under coercive control |
| Technical implementation | **F-002** Margaret can only act through a generic role or Arthur's unlock code: not recorded as attorney, not limited, not visible |
| Configuration for an instance | **F-003** Co-approval ("a second person must agree") exists, but is off by default. A good basis for supported decisions, with the wrong default |
| Governance | **F-005** No pathway for closing an identity on death; Arthur stays a "ghost" member |
| Governance | **F-007** No oversight of whoever acts for Arthur: no audit he can see, no way to take control back, no route for concerns |
| User experience | **F-006** No accessibility for cognitive differences; the member app works by keyboard only |
| User experience | **F-008** No safe way to decline under pressure |

Full findings, evidence descriptions, limits and next steps: `example.json`.

## What this example teaches about the toolkit

- **The format strains to hold an implementation review.** A record holds one repository, but this stack has three. There are no fields for evidence, the person affected, or who must act. And RAHP has **no control plane for user experience**, so F-006 and F-008 had to be filed as "implementation guidance".
- **Two findings rest on proposed risks** that aren't in the catalogue yet: coercion by someone close, and abuse of delegated authority (RAHP issue #58).
- **Protection can create risk.** F-004 shows it: a second notice recipient protects Arthur, but could expose someone else (RAHP #56).
