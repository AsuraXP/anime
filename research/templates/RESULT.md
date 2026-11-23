# RESULT — <candidate> / <gate>

**Author:** `[agent-x]` · **Commit:** `<sha>` · **Command:** `python3 ...` · **Machine:** CPU-only

> Every result carries its denominator. A number without a same-parameter baseline is not a result.
> Negative and null results get published exactly like positive ones — that is the whole point of
> the arrangement (`CHARTER.md` §3, K3).

## Table
| gate | requirement | measured | pass/fail | baseline (same params) |
|---|---|---|---|---|
| G1 | 100% exact @ 10⁶ | | | |
| G2 | state ratio ≤ 1.10 | | | |
| G3 | per-token ratio ≤ 1.20 | | | |
| G4 | ≤ 4 KiB reads/token | | | |
| G5 | ≤ 10 min CPU to parity | | | |
| G6 | held-out gap ≤ 5 pts | | | |
| G7 | 0 collateral edits | | | |
| G8 | 0 wrong + attributable abstain | | | |

## What surprised me
(Required field. If nothing surprised you, the run was too small or you already knew the answer and
therefore designed the test to confirm it — say which.)

## What this kills
(Which hypothesis or candidate does this result falsify? If none, say "nothing — inconclusive" and
why. "Inconclusive" is an acceptable result; "suggestive" is not a result.)

## Regenerate
```bash
# exact command, exact expected runtime
```
