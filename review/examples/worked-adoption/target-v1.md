# Training target: bounded membership credential lifecycle, version 1

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

This version does not specify notice, decision rationale, appeal or restoration procedure. The validity of a signed revocation update does not establish that a fair decision occurred.

## T2: expiry

The relying service MUST reject a credential after its expiry time.

This version does not specify a renewal request interface, a renewal time window or the behavior of the service while a renewal request is pending.
