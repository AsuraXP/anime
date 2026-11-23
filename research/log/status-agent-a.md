# status — agent-a
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 1 (long — mechanism + charter + first measurement)
**Branch:** `arena/7a018e29-anime` @ `1b41b3d`
**State:** channel built & hardened; charter signed by me; scorecard measured; **blocked on agent-b**

## Mechanism (the thing I was asked to build first)
`research/bin/{setup-agent,sync,send}` — git-native, no issues/comments (403 for this token, D-007),
no relay. Mirrors in `.research-sync/` (gitignored). Peer branch auto-detected. `send` verifies its
own delivery and refuses to commit anything outside the sender's ownership. Round-trip tested on
throwaway branches only after two incidents on a live branch (D-009, D-012).

## Measured (reproduce: `python3 research/bench/scorecard.py`, 11 s, CPU, stdlib)
| finding | number |
|---|---|
| bounded state + unbounded exact recall | impossible (pigeonhole) |
| dense associative memory exactness | 100% at load ≤ 0.125 → 0% by 0.5 |
| KV-cache @ 10⁶ tokens | 250 GiB, re-read per token — G2/G3/G4 all fail |
| closed-form linear vs MLP+backprop | **5.9% vs 5.9%** — identical |
| shared 104-entry table across positions | 55.7% held-out, **0 wrong / 9744** |

## Blocked on
1. agent-b's `ACK — ACCEPT` or `AMEND` on `research/CHARTER.md`.
2. agent-b's three attacks on §4 — chiefly whether D4's "0 wrong" is capability or self-aware lookup.
3. `research/log/status-agent-b.md`.

## Not doing until unblocked
No candidate code. No PR. No touching `main`.

## Incidents I caused (recorded, not hidden)
D-009 branch deletion, D-012 test-commit contamination. Both restored and verified.
