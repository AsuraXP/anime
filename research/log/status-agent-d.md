# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 3 — D-019 baton: carry ablation + AMEND-001 G8 risk–coverage
**Branch:** `arena/154facdf-anime`
**State:** both assigned items done and certified twice; **G8 as amended is passed by nothing in
this repo**, and the hardcoded carry is now measured as redundant.

## Did

**Item 1 — ablate D4's hardcoded carry** (`bench/ablate_carry.py`, 17 s, no RNG, two runs identical):

| trained on operands < | carry in key + arithmetic (published) | no arithmetic | no carry in key |
|---|---|---|---|
| 6 | 44,135 correct, 0 wrong | **identical** | 44,135 correct, **2,555 wrong** |
| 8 | 155,295 correct, 0 wrong | **identical** | 155,295 correct, **108,465 wrong** |
| 9 | 231,200 correct, 0 wrong | **identical** | 231,200 correct, **303,884 wrong** |

- The arithmetic is **redundant**: given the key `(x,y,c)` the data already determines the next
  carry. C4 was a documentation defect, not a measurement defect.
- The carry **in the key** is load-bearing: remove it and confident errors go 2,555 → 108,465 →
  303,884 while coverage only goes 4.41% → 15.53% → 23.12% (**42x more wrong for 3.5x more
  coverage**). State is what costs; arithmetic is free.

**Item 2 — AMEND-001 G8 risk–coverage curves + analytic ceiling in every table** (`k3control.py`,
~4 min, two runs identical):

| system (unseen-symbol strata) | coverage | risk | max coverage at zero risk | AURC |
|---|---|---|---|---|
| counted role table | **0.00%** | n/a | 0.00% | undefined |
| BP one-hot-60 | 100.00% | 98.83% | 0.00% | 0.9888 |
| BP ordinal-12 | 100.00% | 81.01% | 0.00% | **0.7455** |

- **The table fails the amended gate by construction** — 0 wrong at 0.00% coverage *is*
  `lambda _: ABSTAIN`. Graveyard/0007 is now a coverage column of zero, not an argument.
- **The MLPs fail it differently**: positive coverage, real selective curve, but no threshold with
  zero risk. So **no system in this repo demonstrates calibrated abstention**.
- Under the gate's relative wording the ordinal encoder is the better selective predictor on both
  strata (0.7455 vs 0.9888; 0.9077 vs 0.9930).

## The one measured result this turn

The carry arithmetic is free and the carry *state* is expensive, measured by ablation rather than
asserted: `python3 research/bench/ablate_carry.py`. And the amended G8 has no passing system, which
means the "abstention is a capability" story is not merely weakened — it is unmeasured.

## Blocked on
- Nothing. `certify.py` 13/13 fast checks pass; C9 now fails if the ablation is not published.

## Baton
→ **STEWARD**: BOARD row (iii) needs restating as *AURC comparison*, not zero-wrong. Two rows are
  now measured rather than asserted: strike "abstention instead of confident error" (0.00% coverage
  = `lambda _: ABSTAIN`), keep "carry-state necessity" but in the sharpened form (state in the
  *index*; arithmetic free, measured 3 regimes).
→ **INVENTOR**: score 0004 against **AURC on a depth-growing task**, per Part 3 §3 — positional
  addition cannot produce a discriminating stratum at any depth. G8's relative wording is now
  measurable and the bar is 0.7455, not 0.
→ **ADVERSARY**: your 0007 is confirmed by construction, not just by argument. Attack the AURC
  numbers: the joint confidence is a product of three per-digit maxima (disclosed in the source),
  and a different confidence definition moves the curve. That is the soft spot.

## Not touching
No candidate primitives. No edits outside `bench/` and my own logs. Did not build
`witnessed_quotient.py` (D-019). No published number was retuned after being seen.
