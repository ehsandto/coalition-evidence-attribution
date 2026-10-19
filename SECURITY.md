# Security policy

Experimental and unaudited. Report vulnerabilities privately to the repository
owner; do not include wallet keys, API credentials or raw validator receipts.
No token custody, native-value acceptance, transfers, approvals, code evaluation,
cross-contract writes, admin override or upgrade path is implemented.

## Enforced

- Native sender-bound creator nonce, per-creator 32-case cap, immutable input root.
- Permissionless resolution; exact root fencing; immutable one-time resolution.
- Only safe full-commit GitHub raw coordinates; two/three distinct URL/hash pairs.
- Actual full-body acquisition by each validator; strict HTTP/UTF-8/size/hash checks.
- Normalized duplicate rejection; complete fixed coalition enumeration.
- Exact canonical full-report comparison including typed labels/masks/source data.
- Revalidate report post-consensus; recompute outputs rather than trust model credit.
- Signed integer factorial-weight arithmetic; no confidence tolerance/threshold trick.
- Unknown ranges and failed-source HELD; exact consumer gate requires root + EXACT.

## Not solved

Model semantic mistakes, correlated validators, injection, source honesty,
authorship/independence, semantic duplicates, corpus manipulation, internet-wide
coverage, current applicability, economic fairness and Sybil-resistant rate limits.
Changing the selected claim can change contribution. Pinned fictional fixtures
are transparent test documents, not evidence of operational service delivery.

If consensus cannot finish, the case stays unresolved and can be retried by anyone.
No funds or external permission are blocked by an unresolved case. HELD/BOUNDED
are terminal accounting outcomes, not accusations against a source or publisher.
