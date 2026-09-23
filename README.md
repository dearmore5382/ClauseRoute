# ClauseRoute

ClauseRoute is a GenLayer Intelligent Contract that authenticates a sealed contractual document set and records the dispute-resolution route supported by those documents.

It is deliberately not an escrow, a release/version graph, or a frontend application. Its state machine is:

`authority -> case capsule -> document set -> sealed -> assessed -> closed`

## What makes the contract intelligent

Deterministic code verifies a GitHub commit, manifest identity, and five SHA-256-bound documents. Validator nodes then independently classify six narrow observations as `YES`, `NO`, or `UNCLEAR`. Contract code—not the model—derives the stored route.

Possible routes are `ARBITRATION`, `COURT`, `NEGOTIATION_FIRST`, `CONFLICTING_CLAUSES`, `NO_DOCUMENTED_ROUTE`, `INSUFFICIENT_EVIDENCE`, and `DOCUMENT_SET_REJECTED`. A temporary source/model failure returns `ASSESSMENT_RETRYABLE` without closing or mutating the case.

ClauseRoute identifies a documented procedural route only. It does not decide enforceability, jurisdiction, liability, damages, merits, or provide legal advice.

## Contract API

Writes:

- `register_authority(name, owner, repository, policy)`
- `open_case(authority_id, reference, claimant, respondent, dispute_type, amount_band, claimant_country, respondent_country)`
- `attach_document_set(case_id, commit, manifest_path, manifest_sha256)`
- `seal_case(case_id)`
- `assess_route(case_id)`

Views:

- `get_authority(authority_id)`
- `get_case(case_id)`
- `get_finding(case_id)`
- `get_counts()`

## Local verification

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m py_compile contracts\ClauseRoute.py
genvm-lint check contracts\ClauseRoute.py
genvm-lint typecheck contracts\ClauseRoute.py
genvm-lint schema contracts\ClauseRoute.py
```

The repository contains no frontend. See [SPEC.md](SPEC.md), [PLAN.md](PLAN.md), and [verification/AUDIT.md](verification/AUDIT.md).

