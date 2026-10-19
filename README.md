# CoalitionEvidenceAttribution

Bounded, source-acquired **signed Shapley attribution of documentary evidence**.
Experimental GenLayer infrastructure; not a truth oracle, source reputation score,
financial allocator, graph mutation system or consumable certificate.

[Verified StudioNet deployment](https://explorer-studio.genlayer.com/address/0x7a201CDDD0c3e9CcaBcBd79A0C04CD05F3f30bB8).
Deployed source matches this file's published version. See [live proof ledger](LIVE_PROOFS.md)
for finalized execution results, independently checked arithmetic and fixture scope.

## Problem and why GenLayer

Two documents may jointly establish a claim although neither establishes it alone.
Another document may undermine the same conclusion. Counting documents or paying
for a caller's asserted relevance misses complementarity and contradiction.

This contract acquires complete, immutable document versions itself. The leader
and validators independently reason about **every nonempty coalition** of two or
three sources. Those exact semantic judgments drive signed marginal-contribution
accounting. A deterministic blockchain can calculate Shapley arithmetic but
cannot independently fetch and interpret prose. A private model can interpret it
but cannot provide a shared, independently checked onchain accounting result.

```text
claim + full-commit source coordinates + raw-body commitments
                  |
permissionless resolve (no creator veto)
                  |
each validator independently fetches ALL full source bodies
                  |
independent SUPPORT / REFUTE / NEITHER / UNKNOWN for EVERY coalition
                  |
exact complete-report consensus + deterministic integrity checks
                  |
signed rational Shapley points / uncertainty bounds / HELD
```

## Distinct mechanism

Storage contains immutable attribution problems and terminal accounting records.
There are no graph edges, parent-head transitions, mutation proposals, selectable
favorable subsets, prediction books, worker leases or one-time approval tokens.
It is not an annotation accuracy audit: no provider label is supplied. It is not
a cover optimizer: no cheapest winning subset is selected. It is not a policy
truth-table compiler: no hypothetical action is authorized or compiled for reuse.
Every coalition participates in one signed marginal-contribution calculation.
This is one representative mechanism, not parallel domain variants. Novelty or
reviewer acceptance is not guaranteed.

## Evidence and consensus boundary

`open_case(nonce, claim, sources_text)` binds the authenticated creator, deployment,
nonce, fixed claim, ordered sources and mechanism policy to an immutable input root.
Each source line is `OWNER/REPO/FULL_40_HEX_COMMIT/PATH.txt|RAW_SHA256`. Only constructed
`https://raw.githubusercontent.com/...` URLs, safe paths, two or three distinct
URLs and distinct expected hashes are accepted. No caller provides source bodies,
coalition labels, utility scores, confidence or summaries.

`resolve(case_key, expected_input_root)` is permissionless. All bodies must pass
HTTP 200, strict UTF-8, nonempty/no-NUL and 1–5000 raw-byte bounds. Hashes bind the
**entire** response, never a truncation. Whitespace-normalized duplicate bodies
block accounting. Hash equality establishes byte integrity, not semantic validity
or independent authority. Semantic paraphrase duplicates are not detected.

Each validator refetches each source and independently reconstructs the full
report: case/input/contract binding, source bodies/statuses/raw hashes/normalized
fingerprints and the complete ordered coalition vector. Exact canonical equality
is required. Format-only checks are not sufficient. Malformed model output or
validator disagreement applies no write; no fictitious CONFLICTED record is made.

The model uses only each coalition's included documents, not outside knowledge.
SUPPORT requires the complete claim; REFUTE requires explicit incompatible
evidence. NEITHER is clear absence of sufficient support and refutation. UNKNOWN
includes ambiguity and material conflicting evidence. Partial support for a
conjunction is NEITHER, not refutation. More evidence need not be monotone.

## Signed accounting and uncertainty

For a fixed ordered source set N, use utility `SUPPORT=+1`, `REFUTE=-1`, `NEITHER=0`.
The empty coalition has utility zero. For each source i:

```text
phi_i = sum over S excluding i:
        |S|! (n-|S|-1)! [v(S union {i}) - v(S)] / n!
```

All numerators are signed integers, with denominator `n!`; no floats, rounding,
normalization to positive percentages or caller-selected weights. Negative
attribution is meaningful. Scores can exceed one in magnitude for nonmonotone
games. Exact scores sum to full-coalition utility (efficiency conservation),
checked deterministically. They do not sum to one for a neutral or refuting game.

UNKNOWN is **not** converted to zero. Its possible utilities are -1, 0, +1.
The contract computes each source's minimum/maximum rational contribution over
those unconstrained possibilities. These are sharp per-source algebraic bounds
conditional on the known judgments, not statistical confidence intervals or
proof of truth. Interval endpoints for different sources need not be jointly
attainable; do not sum or distribute them as if they were a point allocation.

```text
OPEN --all source bytes valid + all coalition judgments known--> EXACT
OPEN --all source bytes valid + any UNKNOWN--------------------> BOUNDED
OPEN --failed acquisition or duplicate full body---------------> HELD
OPEN --network disagreement or malformed AI--------------------> OPEN (no write)
```

All stored resolutions are terminal and immutable. BOUNDED exposes intervals,
never an exact point vector. HELD exposes no attribution. `exact_attribution`
requires EXACT and the exact input root. No balances are held; no party's funds
can be locked. Anyone can retry unresolved consensus; a terminal failure requires
a new nonce/problem. Limits are 32 cases per creator per deployment, not Sybil
resistance or a guarantee of network availability.

## Example workflows

The authored fixtures describe a **fictional** archive, not an observed service.
One document specifies encryption at rest; another specifies deletion after thirty
days. Claim: every stored archive has both properties. Expected singleton utilities
are zero and joint utility one, yielding `1/2` attribution to each document.

An unresolved discussion does not establish any applicable rule: a BOUNDED result
must not be advertised as exact credit. A wrong raw commitment must produce HELD
without semantic accounting. Duplicate resolution must revert without replacing
the old result. Actual live outcomes, not these expectations, are recorded in
[LIVE_PROOFS.md](LIVE_PROOFS.md).

Observed StudioNet outcomes: complementary documents received `1/2` each. The
uncertainty evaluation finalized with **MAJORITY_DISAGREE and no resolution**, not
a BOUNDED artifact. The wrong commitment produced HELD with no attribution;
replay and wrong-root transactions reverted as expected. All nine transactions
and independent state readbacks are documented, with errors and disagreement
kept separate from successful committed execution.

## Install and test

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/genvm-lint check contracts/CoalitionEvidenceAttribution.py --json
.venv/Scripts/python -m pytest tests -q
npm ci
npm run test:sdk
node --test tests/checker.test.mjs
```

Direct tests mock HTTP/AI and execute only the leader. Separate callback tests
execute the actual extracted validator and verify independent re-observation.
Neither is a substitute for live distributed consensus. Exhaustive arithmetic
tests cover every 2/3-source known utility table and all two-source uncertainty
completions. No production audit or semantic error-free guarantee is claimed.

Local validation: 37 Python tests, five independent Node checker tests, five SDK
calldata roundtrips, and GenVM lint/SDK validation pass. Arithmetic checks include
2,214 exact tables, 216 two-source uncertainty completions and permutation-based
enumeration of all 2,187 completions of an all-unknown three-source game.

## Deployment and interaction

```powershell
npm install -g genlayer@0.39.2
genlayer network set studionet
genlayer account use YOUR_ENCRYPTED_TEST_ACCOUNT
genlayer account unlock
genlayer deploy --contract contracts/CoalitionEvidenceAttribution.py
# $sources is a newline-delimited pair/triple of commit-pinned coordinates|hash.
genlayer write ADDRESS open_case --args demo "Every stored archive is encrypted at rest and deleted after thirty days." $sources
genlayer call ADDRESS get_case --args CASE_KEY
genlayer write ADDRESS resolve --args CASE_KEY INPUT_ROOT
genlayer call ADDRESS get_resolution --args CASE_KEY
genlayer call ADDRESS exact_attribution --args CASE_KEY INPUT_ROOT
```

StudioNet is gasless. Keep keys in a dedicated encrypted native keystore, never
Git or environment variables. Check FINALIZED **and leader execution SUCCESS**;
an expected revert is an ERROR, not successful accounting. Compare source from
`gen_getContractCode`/Explorer with the exact published file. Recompute input and
result roots and signed fractions from stored reports. After an uncertain send,
inspect its recorded hash and signer history before any rebroadcast.

## Threat model

Sources can be authored by the caller or share a publisher. This is attribution
**within a chosen corpus**, not independently corroborated reality, source
credibility, author ownership, fair payment or representativeness of the internet.
Commit pinning is version integrity, not freshness. Source splitting, corpus
selection and ordering affect the game; exact/normalized duplicate rejection
does not prevent semantic duplication or Sybil gaming. Claim wording and utility
mapping define the accounting, not an objectively correct reward schedule.

Prompts frame evidence as untrusted data, but injection resistance and model
accuracy are not formally proved. Validators may share errors. Historical pinned
documents can be obsolete. No claim of service delivery, real agent behavior,
compliance, safe authorization or formal logical entailment follows from EXACT.
See [SECURITY.md](SECURITY.md) and [architecture](docs/architecture.md).
