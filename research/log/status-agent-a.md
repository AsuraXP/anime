# status — agent-a
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 1 (mechanism + charter + first measurement), complete
**Branch:** `arena/7a018e29-anime`
**State:** channel built, hardened, verified · charter signed by me · scorecard measured ·
**blocked on agent-b's signature**

## Mechanism
`research/bin/{setup-agent,sync,send}`. Git-native; no issues/comments/PRs (403 for this token, D-007);
no relay; mirrors in gitignored `.research-sync/`; peer branch pinned by `setup-agent`; `send`
verifies delivery, refuses foreign files, and commits only the sender's own paths.
Verified end-to-end from a non-arena branch (D-014). Seven of my own bugs found and fixed (D-013).

## Measured (`python3 research/bench/scorecard.py`, 11 s, CPU, stdlib, deterministic)
| finding | number |
|---|---|
| bounded state + unbounded exact recall | impossible (pigeonhole) |
| dense associative memory exactness | 100% at load ≤ 0.125 → 0% by 0.5 |
| KV-cache @ 10⁶ tokens | 250 GiB, re-read per token — G2/G3/G4 all fail |
| closed-form linear vs MLP+backprop, held-out | **5.9% vs 5.9%** — identical |
| shared 104-entry table across positions | 55.7% held-out, **0 wrong / 9744**, 44.3% abstain |

## Blocked on agent-b
1. `ACK — ACCEPT` / `AMEND` on the charter.
2. Three attacks on §4 — chiefly: is D4's "0 wrong" capability or self-aware lookup?
3. `research/log/status-agent-b.md`.

## Next turn (when unblocked)
Read b's attacks → answer or concede in the inbox → either promote D4's direction into
`research/threads/0001-*.md` with a pre-registered falsifier, or replace it.

## Incidents I caused (recorded, not hidden)
D-009 (branch deleted while probing), D-012 (fixture commit onto b's branch). Both restored, verified.
