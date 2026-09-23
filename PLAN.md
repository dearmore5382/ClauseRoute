# Build and live-verification plan

1. Run all local tests and GenVM static checks.
2. Publish this exact source and fixture set; recorded evidence commit: `ea3d3c260712838092e7704a62f5840281f09b52`.
3. Deploy `contracts/ClauseRoute.py` from the published source using the submitter wallet.
4. Register one authority pointing to the published repository.
5. Open a case whose identity exactly matches `fixtures/happy/manifest.json`.
6. Attach the published 40-character commit, manifest path, and byte-exact manifest SHA-256.
7. Seal and assess the case; wait for finalization after every write.
8. Read `get_case` and `get_finding`, and record explorer links for every transaction.
9. Exercise failure evidence separately: wrong manifest digest, identity substitution, unavailable source, injected model output, and validator disagreement.

Deployment is recorded in `verification/LIVE_RESULTS.md`; lifecycle calls remain unclaimed until their finalized transaction hashes are added there.
