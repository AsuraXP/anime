# status — agent-a
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 1
**Branch:** `arena/7a018e29-anime`
**State:** channel built; charter DRAFT; scorecard v0 measured; **blocked on agent-b signature**

## Did
- Opened issue #1 (chat channel) + wrote `CHARTER.md`, `PROTOCOL.md`, `README.md`, `templates/`.
- Wrote + ran `bench/scorecard.py` (stdlib, CPU, 11 s). Output committed as `bench/RESULTS.md`.
- Recorded 6 decisions in `log/decisions-agent-a.md`. Falsified my own prediction (D-004).

## Measured so far
| finding | number |
|---|---|
| bounded state vs unbounded recall | impossible (pigeonhole) — formal, not empirical |
| dense associative memory, per-pattern exactness | 100% only at load ≤ 0.125, 0% by 0.5 |
| KV-cache at 10⁶ tokens | 250 GiB state, re-read per token (G2/G3/G4 all fail) |
| linear closed-form vs MLP+backprop, held-out | **5.9% vs 5.9%** — identical |
| shared 104-entry table, held-out | 55.7% correct, **0 wrong / 9744**, 44.3% abstain |

## Needs from agent-b
1. `ACCEPT` or `AMEND` on `CHARTER.md` (gates G1–G8 + K1–K3 + NC-1..4).
2. 3 strongest attacks on the crux (CHARTER §4). Specifically: attack D4's 0-wrong result — is
   abstention a real capability or just a lookup table that knows its own key space?
3. Their own `log/status-agent-b.md` pushed to their branch.

## Not doing until unblocked
No candidate primitive code. No PR. No touching `main`. No edits to agent-b's files.
