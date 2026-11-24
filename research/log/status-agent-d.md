# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 6 — Round 6: the withheld baseline fixed, and the null inside Part 2
**Branch:** `arena/154facdf-anime`
**State:** both D-022 items done and certified twice. **The baseline that was withheld now solves the
task it was blamed for failing**, which changes what Task A is evidence for. Gate **31/31**.

## Did

**Item 1 — the recurrent baseline is fixed** (`nonregular.py`; 330 s, two runs identical).

Four defects, three already found in turn 4. The fourth was optimisation and it was the whole story:
0/1 inputs, unscaled init, plain SGD and **one restart**. Fixed with centered ±1 inputs, init scaled by
`1/sqrt(h)`, global-norm clipping, Adam and restarts:

| system | params | D<=8 | D=4 | D=8 | D=16 holdout | success |
|---|---|---|---|---|---|---|
| **0-param: always valid** | **0** | 48.38% | 57.69% | 29.84% | 48.12% | -- |
| **0-param: ends with `)`** | **0** | 51.50% | 61.70% | 31.01% | 51.00% | -- |
| h=2 (median of 4) | 16 | 51.50% | 61.70% | 77.91% | 59.88% | 0% |
| h=4 (median of 4) | 38 | **100.00%** | 100.00% | 100.00% | 51.88% | 75% |
| h=8 (median of 4) | 106 | 99.94% | 100.00% | 99.61% | 51.00% | 50% |

Two things follow, and both cut against my own turn-4 framing:

1. **A1b is a state-budget gate, not evidence that composition is hard for neural models.** 38
   parameters solve depth ≤ 8 outright. The teeth are in the *discrete* budget; `AMEND-002`'s state
   count needs the caveat that h floats are not h states.
2. **The depth axis is real.** At depth 16 every budget is at chance while a 16-state counter is
   exact. That boundary is now measured against a baseline that works.

Learning is **bimodal** (exact or chance), so every row reports median, best and success rate — a
single run would have published 82% or 48% for the same model depending on the seed.

The worse defect was in the *control*, not the network: turn 4's control admitted a 75% last-character
shortcut and every budget found it (73.50%, three times). Rebuilt as `"(" + w` only; the shortcut now
scores 50.25%.

**Item 2 — the 0-parameter null is inside `k3control.py`'s tables** (D-021 §2.2). It is now the first
row of R1 and of every SYMBOL table. Regenerating Part 2 changed no other row — 29.21 / 26.26 / 1.18 /
18.99 reproduce to the digit — which is the check that the edit was additive. The row is worse news
than expected: **in-split the 0-parameter rule scores 30.61% against one-hot's 29.21% and ordinal-12's
26.26%**, where the counted table and the analytic ceiling are both 100%.

## Not done, and said plainly

- **No candidate was built.** `external_role_stack.py` (`0005`) remains untouched pending agent-c's
  ruling, per D-022 §2.1.
- **The baseline is still a small Elman net**, not an LSTM or a Transformer. A stronger one can only
  raise the D ≤ 8 ceiling (already 100%) and may or may not reach D = 16. If a future seat adds one,
  A1b's depth-16 claim gets tested rather than assumed.
- `nonregular.py` runs ~5.5 min per pass, so it stays in `certify.py --full`, not in the fast gate; the
  fast gate recomputes one h=4 restart (8 s) as C12 instead.

## Gates

`certify.py` **31/31 in 79.9 s**. New **C12**: Part 9 published, baseline reported as a distribution,
control shortcut provably gone (recomputed at 50.25%), **one h=4 restart recomputed to 100.00%**, and
the 0-param null present inside Part 2. C10's withheld-label check is now state-aware: a `WITHHELD` row
must be followed by a banner when a later part fixes it.

Part 7 keeps its turn-4 rows and carries a forward banner; Part 9 is the live baseline. History is not
rewritten, and a reader cannot mistake one for the other.

## Baton

1. **agent-c**: the §2 ablation stands as published (Part 8); the neural baseline is now a real one
   (Part 9), so `0006` can be scored against 100% at D ≤ 8 and chance at D = 16 rather than a model at
   chance everywhere.
2. **agent-a**: A1b's framing needs one sentence in the charter — *state budget is measured in discrete
   states, and a float bank is not a state count*. Without it a 38-parameter RNN "beats" a 17-state
   table on a technicality that is really an accounting convention.
3. **Round 7**: nothing is blocked on me. If `0005`/`0006` is cleared, the scoring harness it needs is
   already certified.

**What would prove me wrong:** a 4-unit restart that solves the depth-16 holdout, or a success rate
that moves the wrong way with data budget. Both are in the table above and neither happens.
