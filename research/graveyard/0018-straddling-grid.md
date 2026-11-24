# 0018 — a mean over a grid that straddles the viability threshold
**Status:** DEAD (a measurement practice; it produces a number that looks like a curve and is a
composition artifact)
**Family:** reporting an average over a grid of depths / budgets when some cells of that grid are
state-saturated and others are not.
**Failed because:** the verdict is **binary per cell**. At depth `D` a task either has a feasible
minimal automaton (dead — an `M(D)`-state table is exact) or it does not (viable). Averaging over cells
on both sides of that boundary produces a number that moves with the *grid's composition* — how many
dead cells you happened to include — and not with the mechanism. It is worse than a wrong number
because it looks like a learning curve.

**Already happened once, and it produced a false headroom claim.** `bench/nonregular.py` A1b is a
`k ∈ {2,4,8,16}` × `D ∈ {2,4,8,16}` grid whose requirement is `k ≥ D+3`:

| `k` | exact at | below ceiling at |
|---|---|---|
| 2 | none | 2, 4, 8, 16 |
| 4 | none | 2, 4, 8, 16 |
| 8 | 2, 4 | 8, 16 |
| **16** | **2, 4, 8** | **16** ← read as "headroom" |
| 19 | 2, 4, 8, 16 | none |

The `k=16` row is a straddling row: exact on three cells, below ceiling on the fourth. Reading its
70.8% as headroom was reading a *mixture cell* as a *measurement*. `agent-d`'s turn-7 audit confirms the
requirement is `D+3` and that one 19-state machine is exact on the whole grid — so the entire grid is
saturated and every "below ceiling" cell was a smaller budget, not headroom.

**About to happen again.** Round 7 is building Dyck-2 at `D ∈ {4..64}`. `M(D) = 2^(D+1) − 1` and
`AMEND-006` clause 1 sets the bar at `M(D_max) ≥ 2^30`:

| `D` | `M(D)` | bits | verdict |
|---|---|---|---|
| 4 | 31 | 5 | DEAD (feasible) |
| 8 | 511 | 9 | DEAD |
| 16 | 1.31e5 | 17 | DEAD |
| 24 | 3.36e7 | 25 | DEAD |
| 28 | 5.37e8 | 29 | DEAD |
| 29 | 1.07e9 | 30 | DEAD |
| **30** | **2.15e9** | **31** | **VIABLE** |
| 32 | 8.59e9 | 33 | VIABLE |
| 48 | 5.63e14 | 49 | VIABLE |
| 64 | 3.69e19 | 65 | VIABLE |

**Crossover at `D* = 30`. Of the 61 cells in `{4..64}`, 26 are DEAD and 35 are VIABLE — 43% of the grid
is a saturated task.** A mean over that grid is 43% "did you learn a 31-state table" and 57% "did you
learn a `2^31`-state quotient", weighted by nothing in particular.

**What a candidate inherits if it reuses this:** a score that improves when the grid is re-balanced
toward high `D`, with no change in the mechanism. And a learning curve that looks smooth because the
mixture fraction changes smoothly with `D`.

**Escape condition:** the grid must be **declared as one or the other**:
- **a train/test split** — train at `D ≤ D_train`, test at `D > D_train`. Then it is a genuine
  extrapolation benchmark and the whole range is legitimate, *provided the test cells are all on the
  viable side* (`D ≥ 30` here).
- **a grid of independent cells** — then each cell is its own envelope, the verdict must be per-cell,
  and the kill metric must be carried by `D_max` alone.

Either is fine. Averaged is not.

**The check (sub-second).** For every `D` in the grid, print `M(D)`, `⌈log₂ M(D)⌉`, and
`DEAD if M(D) < 2^30 else VIABLE` **in the same table as the scores**. If the table contains both
verdicts, the mean row must be suppressed or explicitly labelled *"mean over a straddling grid — 26 of
61 cells are state-saturated; not a measurement."* Cost: one line of arithmetic, before any run.

**Distinct from `0015`, which it extends.** `0015` says the verdict must be taken *at the declared
envelope* rather than in the limit — one envelope, one verdict. `0018` says a **range is not an
envelope**: when the declared envelope is a set, the state requirement is a step function over it, and
any statistic computed across the step is a statistic about the set. `0015` is about *where* you
evaluate; `0018` is about *what happens when "where" is plural*.
