# Training target: bounded membership credential lifecycle, version 2

This fictional specification is an RAHP adoption exercise. It describes no real organization, implemented service or actual affected participant.

## Scope

A fictional community issues a membership credential that enables participation. This exercise considers revocation and expiry only. Identity proofing, issuance eligibility, cryptographic algorithm security and deployment effectiveness are outside the exercise.

## Participants and consequences

- A member relies on the credential for participation. An unexplained revocation can exclude them and impair their reputation.
- An operator can suspend or revoke membership. Its ability to sign an update does not establish the legitimacy of the decision.
- A reviewer needs an attributable reason and a challenge route to distinguish legitimate action from error or abuse.

These are synthetic participant contexts, not interviews or validated representative personas. The exercise reuses existing RAHP risks rather than adding persona or risk records to the maintained DTG corpus.

## T1: revocation

The relying service MUST reject a credential after an authenticated revocation update from its authorized issuer. The issuer MUST record the revocation timestamp and credential identifier.

The companion training governance procedure in T3 specifies documentary notice, rationale, appeal and restoration requirements. The validity of a signed revocation update does not establish that a fair decision occurred.

## T2: expiry

The relying service MUST reject a credential after its expiry time.

This version does not specify a renewal request interface, a renewal time window or the behavior of the service while a renewal request is pending.

## T3: companion governance procedure

Before a revocation decision takes effect, the operator MUST provide the affected member with the decision reason, a decision reference and an accessible notice. An emergency suspension MAY take immediate effect to prevent a documented immediate harm; its notice MUST follow within 24 hours and record the reason for the exception.

The member MUST be able to request review without holding an active membership credential. A reviewer separate from the original decision maker MUST record the evidence considered, the review outcome and any unresolved disagreement. A reversed decision MUST have a recorded restoration action.

For this fictional exercise, the community's governance body is the authority responsible for adopting and revising this procedure. A technical issuer signature is not that authority's approval. These statements establish documentary requirements only; no execution, notice delivery, reviewer independence or effective restoration is demonstrated.

T2's renewal gap remains unresolved. This procedure does not define a renewal interface or authorize continued access using an expired credential.
