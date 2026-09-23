# ClauseRoute specification

## Trust model

An authority controller registers one immutable repository namespace and interpretation policy. The controller opens cases; the resulting case steward binds one exact 40-character Git commit and one expected manifest SHA-256. After sealing, no locator or case identity can change.

All evidence URLs are derived internally as `raw.githubusercontent.com/{owner}/{repository}/{commit}/{path}`. Callers cannot supply an arbitrary host.

## Authenticated evidence

`clauseroute-v1` requires an exact schema and exactly five documents: main contract, amendment, incorporated terms, notice, and precedence schedule. The manifest identity must equal the on-chain case identity. Every fetched byte sequence must match its manifest SHA-256 before semantic analysis runs.

## Consensus boundary

The model may return only six ordered ternary observations:

1. dispute in scope
2. arbitration controls merits
3. court controls merits
4. negotiation prerequisite unsatisfied
5. clauses conflict
6. amendment controls

Validators independently refetch, rehash, and re-evaluate the complete observation. The model cannot directly select the final route.

## State transitions

- `OPEN`: case exists and may accept a document locator.
- `ATTACHED`: exact commit, manifest path, and manifest digest are bound.
- `SEALED`: evidence locator is immutable; anyone may trigger assessment.
- `CLOSED`: one terminal finding and route are stored.

`SOURCE_UNAVAILABLE` maps to the non-terminal `ASSESSMENT_RETRYABLE`. Integrity or schema failures close the case as `DOCUMENT_SET_REJECTED` so a bad sealed set cannot be silently replaced.

## Explicit non-goals

- legal advice or enforceability analysis
- adjudication of the underlying dispute
- payments, escrow, token custody, or native transfers
- mutable upgrades to a sealed case
- accepting arbitrary URLs
- web or dashboard UI

