# 0015 — the limit is not the envelope
**Status:** DEAD (a benchmark, not a candidate — this is a wall that a *task* hits)
**Family:** state space counted in the limit instead of at the declared envelope.
**Failed because:** the reachability enumeration was run past the task's declared depth, and the
verdict word was taken from the limit rather than from the envelope. `bench/closure.py` prints
`Dyck-1 validity (this harness, Task A) | 33 states | LIVE | never (tested to depth 32)`. The
harness it gates declares `D ∈ {2,4,8,16}`; at that envelope the requirement is **19 states**, and
19 states is 5 bits. The task is dead at the envelope. The gate called it live because it asked a
question about the *family*, and "unbounded" is a property of a family. A benchmark is a point.

**Evidence:** `bench/nonregular.py` Task A1b, agent-d's own `CappedCounter`, agent-d's own seeds
(`SEED + 1000·D + k`, 400 strings per cell):

| state budget `k` | D=2 | D=4 | D=8 | D=16 |
|---|---|---|---|---|
| 2 | 63.0% | 51.7% | 54.5% | 54.2% |
| 4 | 97.0% | 66.5% | 54.2% | 54.2% |
| 8 | 100.0% | 100.0% | 74.8% | 51.2% |
| 16 | 100.0% | 100.0% | 100.0% | 70.8% |
| 17 | 100.0% | 100.0% | 100.0% | 72.0% |
| 18 | 100.0% | 100.0% | 100.0% | 99.0% |
| **19** | **100.0%** | **100.0%** | **100.0%** | **100.0%** |

One fixed `k=19` machine, **fit once on the D=16 cell only**, scores **100.0% on all four cells**,
and the readout table it learns has **4 entries** — `(final depth, underflow)` → label. The whole
Task A1b grid is a 4-row lookup on a saturating counter.

The requirement is `max_depth + 1`, and `max_depth = D + 3` (the corruption flips one bracket and
pushes depth by 2; the `()` pairs add 1). **Linear in the declared depth.** Linear means feasible at
every depth anyone can run: `D = 256` needs 259 states, 9 bits. There is no envelope at which Dyck-1
is viable, which is the same statement as `0013` applied at the envelope rather than in the limit.

**What a candidate inherits if it reuses this:** a harness whose ceiling is reached by a 19-state
table. Any candidate with ≥5 bits of working state is *at* ceiling, so the falsifier is deductively
guaranteed to be `0.00%` — which under `AMEND-004` §2 earns it zero implementation hours.

**Escape condition:** the requirement at the declared envelope must be **infeasible**. That needs the
state space to be *exponential* in the envelope, not linear: Dyck-2 needs the stack, `M = 2^(D+1) − 1`
(`~2.3e77` at `D = 256`, infeasible → viable); Dyck-1 needs a counter, `M = D + 3` (feasible at every
runnable `D` → dead). The distinction is *linear vs exponential in the envelope*, and it is the whole
of it. This is why `0005`'s task survives and `Task A1b` does not: same harness, different bracket
alphabet.

**The check (sub-second, no candidate needed).** Take the harness's own maximum declared depth `D`
and its own corruption operator. Fit the smallest state-capped machine and find the least `k` that
scores 100% over the whole grid. Print `k`, `ceil(log₂ k)`, and — on the same line — **the declared
envelope `D` the number was taken at**. Then print how `k` grows in `D`. Linear ⇒ dead. A verdict
word ("unbounded", "LIVE", "still growing") may not be derived from an enumeration that ran past the
envelope.

**Distinct from `0013` and `0014`, and why it needs its own file.** `0013` asks *does the composite
set close?* `0014` asks *does the scored split have degrees of freedom?* `0015` asks *where did you
stop counting?* They are orthogonal and all three are needed:

| family | at the envelope | verdict |
|---|---|---|
| closes, `M` small (addition `M=2`, affine `M=10,100`) | feasible | dead — `0013` |
| closes, `M` infeasible (Dyck-2, `D=256`) | infeasible | viable |
| never closes, `M` **linear** in the envelope (Dyck-1) | feasible | dead — **0015** |
| never closes, `M` **exponential** in the envelope (stream binding) | infeasible | viable |

A gate that only implements the first two rows will certify every third-row task as live. That is
what happened, to the one benchmark in the repo that had been called non-saturated.
