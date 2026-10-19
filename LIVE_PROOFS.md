# Live proof ledger

## Deployment — 2026-10-19

[StudioNet contract](https://explorer-studio.genlayer.com/address/0x7a201CDDD0c3e9CcaBcBd79A0C04CD05F3f30bB8)
on chain 61999. Dedicated encrypted signer: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`.
The native CLI signs without exporting a key. No tokens were transferred.

Deployed source matches `contracts/CoalitionEvidenceAttribution.py` from published
implementation/fixture commit `28eecfdd24a750c316640e33200fd9f4534ddfe7`.
Normalized source SHA-256: `af64eb905926924eb35f5438447b6fc1711692db7d252e13407ad4ffbc989c87`.
The contract source has not changed since deployment.

Preflight acquisition independently fetched all three pinned fixture URLs;
HTTP 200 and full raw-byte hashes match:

| Document | Full raw SHA-256 |
|---|---|
| encryption.txt | `ce6e3e9e38d4835915d80bba4f3e938cf79d5f56063c52b6e60e5c7cc6c20e51` |
| deletion.txt | `cc2ce27f76b07647821de38a36238a5c143f5ddfd31e4d66cf4c44317a0b8d77` |
| ambiguity.txt | `0c9369ed41dcbf59a63e7c3468c2b7ad07886310c0554981d2ef5b81251737a2` |

## Finalized transaction evidence

| Step | Transaction | Execution / consensus |
|---|---|---|
| Deploy | [95af9542](https://explorer-studio.genlayer.com/tx/0x95af95429f637354e764e1b6a3f348c6c50a8e26a1208903727990c1b529fac8) | SUCCESS / MAJORITY_AGREE |
| Open complementary-source case | [6b9ed8c9](https://explorer-studio.genlayer.com/tx/0x6b9ed8c9ffa4883ce1d7e53e6ff45fa6edc00bee7f23b902e121451792048827) | SUCCESS / MAJORITY_AGREE |
| Resolve complementary-source case | [505e5fd9](https://explorer-studio.genlayer.com/tx/0x505e5fd9dd0520115b84213682ccab38a2d50385a1458fd75dc01f44037fb98d) | SUCCESS / MAJORITY_AGREE |
| Open uncertain-profile case | [36efaa4d](https://explorer-studio.genlayer.com/tx/0x36efaa4df42af8663f64565da7e9e905c1333f3422b3f011237e2608450a31e0) | SUCCESS / MAJORITY_AGREE |
| Disputed uncertainty evaluation | [66eeff6b](https://explorer-studio.genlayer.com/tx/0x66eeff6b6ea50fb6bd68078f93043cb1debb7e82e39282b099b16c7a3eac1010) | Leader execution SUCCESS / MAJORITY_DISAGREE; **no application resolution** |
| Open incorrect-commitment case | [df840d46](https://explorer-studio.genlayer.com/tx/0xdf840d463f1f1202ad6cc451f0714defa6c551a038a016c2dde7511918dffb8a) | SUCCESS / MAJORITY_AGREE |
| Resolve incorrect-commitment case | [30b5a473](https://explorer-studio.genlayer.com/tx/0x30b5a473601167b1548b090ee0ae2ee9705d3659bc210cc3aab61062bd8f5848) | SUCCESS / MAJORITY_AGREE; HELD, no attribution |
| Replay resolution | [ba3f7c66](https://explorer-studio.genlayer.com/tx/0xba3f7c66eb2ca959073e6b149290b4e347959b96682139a775b21895ba84bf3a) | Expected ERROR / MAJORITY_AGREE; `Already resolved` |
| Wrong input root | [624df79f](https://explorer-studio.genlayer.com/tx/0x624df79f47a45a53830257114acaef336a1e471e45c95808ddfcbcaae6d7e092) | Expected ERROR / MAJORITY_AGREE; `Input root mismatch` |

All nine transactions are FINALIZED. Six have successful committed execution,
one finalized with majority disagreement and **no application resolution**, and
two are expected execution errors. A successful leader execution on the disputed
transaction is not counted as successful accounting or publication.

## Independently verified readback

Complementary case: `0fa667cb1c7abb651c20f8fff14043312841af699b1fad799b035491f4677ca4`.
Input root: `578c66da3c1d817b76675d634d42514d474e53eb72ed5499f73d4e7d5a9975ce`.
Result root: `3d29d952f7ccf65686fba1987f860d71566ee248dd3e61578eca6d8e7f121e10`.

Mask 0 (empty), 1 (encryption), 2 (deletion), 3 (both) produced
`[NEITHER, NEITHER, NEITHER, SUPPORT]`. Each document's signed numerator is 1
with denominator 2. The sum is the full-coalition utility +1. Status is EXACT;
the root-bound consumer returned that exact record. Both the source bodies and
root bindings were independently checked, and a separate permutation-enumeration
implementation reproduced the fractions rather than trusting the stored output.

### Actual distributed disagreement, not a fabricated business state

Uncertain-profile case: `86c0ca27a7cc41487b6f11633f31578de51cebc5eec0cfc52fda59df7094f638`.
Input root: `dff480970e88e3aae066cc944cf33e6401cceb2a2c7257ac0201a87a8a8a12f7`.
The recorded resolution transaction finalized with MAJORITY_DISAGREE despite
successful leader execution. Readback confirmed `get_resolution` and
`exact_attribution` revert: there is **no stored resolution or point credit**.
This is a fail-closed consensus proof, **not a successful BOUNDED evaluation**.
BOUNDED interval behavior remains locally tested, not claimed as a completed live
result. The disputed transaction was not rebroadcast to manufacture agreement.

### Incorrect raw commitment

Case: `fa1907d078a0b4f7e3d316f99ce3cb77f41948338b947084ffe7a727bf4b32a5`.
Input root: `b96a8dc89a615ac77a517fd6a4c124ee6cc6c10d25d328bfe40491e23e2fb83e`.
Result root: `f2d3e0a3124e65f8a8df65e9795ccdc0acc6a3cdbe962f8ffa34c03472bdbce2`.
The source body did not match the intentionally incorrect all-`f` commitment.
Acquisition was HELD, all nonempty coalition labels were forced UNKNOWN, and
output intervals were empty. The exact-attribution consumer reverted. Successful
HTTP and correct hash length therefore did not produce a semantic attribution.

### Replay and root-binding negatives

Both errors were decoded and matched to their expected messages. After them,
the complementary result and HELD result were read again and their roots were
unchanged. The disputed case still had no resolution or exact consumer output.
Deployed source equality was verified again after the complete workflow. No
uncertain transaction was blindly rebroadcast and no source change was required.

| Scenario | Required behavior | Current evidence |
|---|---|---|
| Complementary docs | Exact signed rational contribution, full denominator | Live EXACT; 1/2 each; roots and consumer independently verified |
| Unknown coalition | Bounded intervals; exact consumer denied | Local BOUNDED tests; live uncertainty evaluation disagreed and stored no result |
| Incorrect commitment | HELD; no attribution or exact consumer | Live HELD, empty attribution, exact consumer denied |
| Duplicate/whitespace duplicate | HELD, no artificial extra player credit | Mocked tests only |
| Replay or wrong root | Execution revert; old record unchanged | Two finalized expected ERRORs; subsequent state/root checks unchanged |
| Validator semantic disagreement | Callback false, no accepted application result | Live MAJORITY_DISAGREE; no resolution and no exact consumer result, independently checked |

Authored fictional fixtures demonstrate document-level accounting, never real
service behavior, independent publisher authority or factual truth.

## Local validation scope

37 Python tests, five Node checker tests, five SDK calldata roundtrips and GenVM
lint/SDK semantic validation pass. Python includes all 2,214 exact 2/3-source tables
and 216 two-source interval completions. The independent Node checker enumerates
2,187 completions of a fully unknown three-source game. Direct tests mock HTTP/AI;
the actual validator callback is separately extracted and tested for independent
re-observation and disagreement. These tests are separate from the actual live
network disagreement documented above.

`PROOFS.json` journals each hash immediately. `node scripts/complete-proofs.mjs`
checks known hashes before continuing and refuses an unknown-broadcast entry.
Never clear such an entry without inspecting sender history. FINALIZED is not
execution success: negative security proofs must be labeled expected ERROR.
