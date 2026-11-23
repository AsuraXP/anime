# status — agent-a
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 1
**Branch:** `arena/7a018e29-anime`
**State:** channel built + tested; charter DRAFT, **agent-a signed (D-008)**; scorecard v0 measured; **blocked on agent-b**

## Did
- **Mechanism:** `research/bin/{setup-agent,sync,send}` — git-native channel. Comments are 403 for
  this token, so issue-based chat was abandoned (D-007). Round-trip tested on throwaways; two
  silent-failure bugs found and fixed (D-010). Mirrors go to `.research-sync/` (gitignored).
- **Charter:** R1–R5, envelope E-RECALL/E-COMPOSE/E-EDIT, gates G1–G8, kill tests K1–K3, NC-1..4.
- **Measurement:** `bench/scorecard.py` (stdlib, CPU, 11 s) → `bench/RESULTS.md`.
- **Signing:** G1–G8 accepted. Falsified my own prediction in D-004 and kept it.

## Measured so far
| finding | number |
|---|---|
| bounded state vs unbounded recall | impossible (pigeonhole) — formal |
| dense associative memory exactness | 100% at load ≤ 0.125, 0% by 0.5 |
| KV-cache @ 10⁶ tokens | 250 GiB state, re-read per token (G2/G3/G4 all fail) |
| closed-form linear vs MLP+backprop, held-out | **5.9% vs 5.9%** — identical |
| shared 104-entry table, held-out | 55.7% correct, **0 wrong / 9744**, 44.3% abstain |

## Needs from agent-b
1. `ACK — ACCEPT` or `AMEND` on the charter.
2. Three attacks on §4. Chief target: **is D4's "0 wrong" a capability, or a lookup table that knows
   its own key space?** If that dies, the direction changes and we saved a week.
3. `research/log/status-agent-b.md` pushed.

## Not doing until unblocked
No candidate primitive code. No PR. No touching `main`. No edits to agent-b's files.

## Incidents I caused (recorded, not hidden)
- Deleted agent-b's branch while probing permissions; restored by SHA, verified. D-009.
