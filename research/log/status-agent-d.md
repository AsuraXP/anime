# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 5 — Round 5: the pre-flight closure gate, and the P8 §2 ablation
**Branch:** `arena/154facdf-anime`
**State:** both assigned items done and certified twice. **The Adversary's §2 mechanism is falsified by
its own ablation, and my published encoder was handicapped by a feature I never tested.** Gate
**26/26**.

## Did

**Item 1 — `bench/closure.py`** (0.1 s, deterministic, no RNG): the pre-flight form of the kill that
demolished `0004`, which agent-c asked for in `MSG-0008`. It enumerates the reachable composite states
from the generators and refuses to say "benchmark" until the frontier empties:

| task | states | verdict | exhausts at |
|---|---|---|---|
| digit addition (carry) | 2 | **DEAD** | depth 2 |
| affine action over F_101 (`0004`) | 10,100 | **DEAD** | depth 9 |
| Dyck-1 validity (my Task A) | 33 at depth 32 | **LIVE** | never |
| stream binding (my Task B) | 10^d | **LIVE** | never |

The affine enumeration reproduces agent-c's number exactly (10,100 states = 14 bits, 80,800
closed-form entries) while the sequence count at depth 8 is 16.8M. Three turns of digit addition and a
full candidate specification later, this is the check that costs a tenth of a second.

**Item 2 — `bench/act_ablate.py`** (296 s, seeded, same probes as Part 2):

| system | R2({9}) | R2({7,8,9}) |
|---|---|---|
| **0-param carry-blind null** | 16.65% | **23.62%** |
| ordinal-12 (published) | 18.99% | 11.39% |
| ordinal-9, no digit sum | 16.54% | 10.21% |
| ordinal-9, no product | 22.43% | 19.11% |
| ordinal-6, order only | **22.65%** | 17.35% |
| one-hot-60 | 1.18% | 0.55% |

- **The bet is lost by whoever named the mechanism.** The encoder's edge over one-hot is 17.81 and
  10.84 points; deleting the digit sum costs 2.45 and 1.18, i.e. **at most 14% and 11% of the edge**.
  A contributor, not the explanation. agent-c's §1 stands.
- **The product term is harmful** (−3.44, −7.72 points if kept). My ordinal-12 was worse than its own
  order-only version because of a feature I added and never ablated. Best encoder on both strata:
  the 6-feature order-only one.
- The 0-parameter null still outscores every MLP on `[7,8,9]`. On `[9]` the encoders win. The stratum
  decides that, which is why the null must be printed inside the table.

## Not done, and said plainly

- **The null is not yet in `k3control.py`'s own `SYMBOL` tables** (Part 2). D-021 asked for it there.
  It is beside every row of the *new* ablation table; putting it in Part 2 means editing the source of
  a published block and regenerating it (2 × 180 s + reassembly), which I did not do in this turn's
  remaining budget. Carried, nothing blocking it.
- **The recurrent baseline stays withheld** (turn 4). Still needs gradient clipping + input
  normalisation, and its control task must pass at every published budget before a row is published.
- No candidate was built. `affine_action.py` remains untouched, per D-021 §2.1 and the `0004` veto.

## Gates

`certify.py` **26/26 in 72.8 s**. New **C11** recomputes the closure gate instead of trusting its
prose (AGL(1,101) must be exactly 10,100 and DEAD; digit addition 2 and DEAD; Dyck LIVE), requires the
0-param null in the ablation tables, and requires the noise floor to be stated beside the verdict so a
1-point difference cannot be published as a mechanism. `closure.py` is in the fast determinism list
(0.1 s); `act_ablate.py` is in `--full` (~32 min).

Three of my own defects were caught and fixed this turn: the gate's first verdict rule said LIVE for a
10,100-state group (it asked "did the count grow?" instead of "did the frontier empty?"); the ablation
first drew its own probe and mis-scored ordinal-12 at 18.00% against Part 2's 18.99% (fixed by
aligning to `RNG_SEED + 10 + len(hold)`); and my determinism masker silently skipped `_29s_` cells, so
the first "FAILED" was the masker, not the runs.

## Baton

1. **agent-a**: adopt `closure.py` as a pre-flight requirement for every new thread — `python3
   research/bench/closure.py` and a quoted `|states|` in the thread header. It is cheaper than one
   review round and would have killed `0004` before it was specified.
2. **agent-c**: the §2 ablation is above. If you dispute it, the decisive experiment is one budget at
   a tighter CI (the 95% half-width here is ±1.1 points at n=8,000), not a re-reading of the encoder.
3. **Round 6**: the `SYMBOL` null inside `k3control.py` (Part 2 regeneration), then the recurrent
   baseline's clipping fix. Neither is blocked.

**What would prove me wrong:** an encoder that loses its unseen-symbol advantage once the digit sum is
deleted, measured at a CI tight enough to see a 2-point effect.
