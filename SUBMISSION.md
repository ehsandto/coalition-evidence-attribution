# Builder submission

Contribution type: Builder → Intelligent Contracts

Title: CoalitionEvidenceAttribution — Signed Source Contribution Accounting

## Notes / Description

CoalitionEvidenceAttribution measures signed document contributions. For a fixed claim and 2–3 commit-pinned sources, validators independently fetch full bodies, check HTTP/UTF-8/SHA-256 and duplicates, and interpret every nonempty source coalition. Consensus requires exact full-report equality.

Contract-owned rational Shapley arithmetic derives marginal contributions. UNKNOWN remains an interval; failed acquisition yields HELD. Exact-root consumers receive point credit only for EXACT. Immutable inputs/results and nonce/case/deployment bindings prevent substitution and replay.

StudioNet proofs show complementary documents each receiving 1/2, disagreement writing no result, bad commitments HELD, and replay/wrong-root rejection. 42 tests, five SDK roundtrips and lint pass; source matches GitHub. No graph, owner-controlled head or certificate exists. This attributes the selected documents, not truth, source credibility or actual service delivery.

## Evidence

- https://github.com/ehsandto/coalition-evidence-attribution
- https://github.com/ehsandto/coalition-evidence-attribution/blob/main/contracts/CoalitionEvidenceAttribution.py
- https://github.com/ehsandto/coalition-evidence-attribution/blob/main/README.md
- https://github.com/ehsandto/coalition-evidence-attribution/blob/main/LIVE_PROOFS.md
- https://github.com/ehsandto/coalition-evidence-attribution/blob/main/PROOFS.json
- https://explorer-studio.genlayer.com/address/0x7a201CDDD0c3e9CcaBcBd79A0C04CD05F3f30bB8
- https://explorer-studio.genlayer.com/tx/0x95af95429f637354e764e1b6a3f348c6c50a8e26a1208903727990c1b529fac8
- https://explorer-studio.genlayer.com/tx/0x505e5fd9dd0520115b84213682ccab38a2d50385a1458fd75dc01f44037fb98d
- https://explorer-studio.genlayer.com/tx/0x66eeff6b6ea50fb6bd68078f93043cb1debb7e82e39282b099b16c7a3eac1010 — finalized disagreement; no published result
- https://explorer-studio.genlayer.com/tx/0x30b5a473601167b1548b090ee0ae2ee9705d3659bc210cc3aab61062bd8f5848
- https://explorer-studio.genlayer.com/tx/0xba3f7c66eb2ca959073e6b149290b4e347959b96682139a775b21895ba84bf3a — expected replay ERROR
- https://explorer-studio.genlayer.com/tx/0x624df79f47a45a53830257114acaef336a1e471e45c95808ddfcbcaae6d7e092 — expected input-root ERROR

Authored fictional fixtures demonstrate document attribution, not behavior of an
operating service or independent-source corroboration. No points/acceptance or
formal semantic-correctness guarantee is made. Read LIVE_PROOFS.md before claiming
any particular lifecycle result; negative execution errors are not successful accounting.
