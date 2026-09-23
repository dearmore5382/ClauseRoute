# Live verification results

Status: **DEPLOYED — LIVE MATRIX COMPLETE**

- Network: GenLayer StudioNet
- Contract: `0x51Ae7fB61612c31931607F21f8D74be4D7E2f8BA`
- Creator: `0xFf36b56CcA032C559e52e2A4F20c2C594B02Fe37`
- Deploy transaction: `0x18c972cb015d332911ed468ce03c4db4203fdf850d4789ef15d2036a032b5b34`
- Deploy status: `FINALIZED`
- GenVM execution: `SUCCESS`
- Consensus result: `Accepted`
- Created: `2026-09-23 02:29:22 UTC`
- Repository: https://github.com/dearmore5382/ClauseRoute
- Published source/evidence commit: `ea3d3c260712838092e7704a62f5840281f09b52`
- Manifest path: `fixtures/happy/manifest.json`
- Manifest SHA-256: `ed90c72fd0278706bfb610de688eeeb16d9ff0d9c00d20dfa2e48ddaaacf0fe3`
- Raw manifest verification: HTTP 200; downloaded digest equals local digest
- Lifecycle matrix: 20/20 finalized with majority agreement and authoritative readback
- Controller/steward test wallet: `0x736A168247e3f0C52F7907c9a8fDac572DF9c8bB`
- Outsider/respondent test wallet: `0xA63DE24e30C88FB1019E8956654730316e36eDBE`

Explorer:

- https://explorer-studio.genlayer.com/address/0x51Ae7fB61612c31931607F21f8D74be4D7E2f8BA
- https://explorer-studio.genlayer.com/tx/0x18c972cb015d332911ed468ce03c4db4203fdf850d4789ef15d2036a032b5b34

## Live outcomes

### Happy path

Case `0` bound the exact fixture commit and manifest digest. After attach and seal, permissionless assessment returned `ARBITRATION`. Authoritative readback is `CLOSED`, route `ARBITRATION`, source status `VERIFIED`, and all five document hashes match the published manifest.

- Open: https://explorer-studio.genlayer.com/tx/0x14fe122ce7670783a869d35d41056a400e767f44c154e4768f8458bb4c723320
- Attach: https://explorer-studio.genlayer.com/tx/0x4217b7f4fd5e33e75d3eb0584bd1a86d2a9f17528b61cb00c8ed4cf91c48c4e6
- Seal: https://explorer-studio.genlayer.com/tx/0x28d7d23bffd018759b4af63a1b4d6c5e59e5e9a558fd014eb24aa9f8a7dda1fd
- Assess: https://explorer-studio.genlayer.com/tx/0x0cad1d97df9e61fc3ca1d0950a3bb4fb84aa42230d6dc492226fc1cb169a3fe7

### Integrity failure

Case `1` deliberately bound an all-zero manifest digest. Assessment returned `DOCUMENT_SET_REJECTED`; readback is `CLOSED` with source status `INTEGRITY_FAILURE`.

- Assess wrong digest: https://explorer-studio.genlayer.com/tx/0x41591fcd26fb45dcc20baa938df1a07ef464918da8889573b3c5895c50900c23

### Retry/no-mutation path

Case `2` deliberately referenced a missing manifest. Assessment returned `ASSESSMENT_RETRYABLE`; readback remained `SEALED`, route `UNDETERMINED`, and finding empty.

- Assess missing source: https://explorer-studio.genlayer.com/tx/0x8c7ee168ca444a65b93a9e5a4d8707c7b5f3c562ac1925aff81869fa8fd9540f

### Adversarial controls

Finalized calls also prove invalid authority rejection, controller-only case creation, steward-only attachment/seal, invalid locator rejection, premature assessment rejection, and assessment replay rejection. The full 20-step transaction/readback journal is stored in `live-0x51ae7fb61612c31931607f21f8d74be4d7e2f8ba.json`.
