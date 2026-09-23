# Local verification — 2026-09-23

- `python -m pytest -q`: **14 passed**
- `python -m py_compile contracts/ClauseRoute.py`: **passed**
- `genvm-lint check contracts/ClauseRoute.py`: **passed** (3 checks; 9 methods)
- `genvm-lint typecheck contracts/ClauseRoute.py`: **no type errors**
- `genvm-lint schema contracts/ClauseRoute.py`: **passed**
- Fixture document hashes: **5/5 match manifest**
- Happy fixture manifest SHA-256: `ed90c72fd0278706bfb610de688eeeb16d9ff0d9c00d20dfa2e48ddaaacf0fe3`

These results establish local contract behavior and source compatibility only. They do not imply a live deployment; see `LIVE_RESULTS.md`.
