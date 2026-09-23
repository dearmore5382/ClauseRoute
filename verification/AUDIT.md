# Adversarial audit matrix

| Scenario | Expected invariant | Automated coverage |
|---|---|---|
| Happy authenticated set | closes once with deterministic route | full public happy path + validator rerun |
| Wrong manifest digest | model is not called; set rejected | digest mismatch test |
| Manifest identity substitution | case identity cannot be swapped | identity substitution test |
| Prompt injection / extra output | strict parser rejects output | extra-token test |
| Validator semantic disagreement | proposal is rejected | validator disagreement test |
| Temporary source/model failure | remains `SEALED`, no finding stored | retry-no-mutation test |
| Unauthorized attachment/seal | only steward can mutate | role-boundary test |
| Repeat assessment | closed case cannot be assessed again | lifecycle test |
| Arbitrary URL attempt | URLs are derived from registered repo | static source test |
| Native-value/custody attempt | no payable/transfer surface exists | static source test |

Local result: `14 passed`. This is test evidence, not a claim of StudioNet deployment.

