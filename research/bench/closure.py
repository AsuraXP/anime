#!/usr/bin/env python3
"""research/bench/closure.py -- the pre-flight gate: is the composite STATE space big enough to bite?

Run:  python3 research/bench/closure.py        (stdlib, CPU, deterministic enumeration, ~0.1 s)

THE LAW, AND ITS TWO CORRECTIONS
--------------------------------
`graveyard/0013` states the rule that killed two benchmarks in two days: if composition closes into a
finite structure of order M, an M-state automaton saturates the task with ceil(log2 M) bits and no
learning at all. Digit addition died to it (M = 2, the carry); candidate `0004` died to it
(M = 10,100, AGL(1,101)).

Two corrections have been adopted since, and both are implemented here:

1. **Finiteness alone is not a kill -- feasibility is** (agent-c's K4, adopted in D-023). Dyck-2 at
   nesting depth <= 256 closes into 2^257 - 1 states: finite, regular, and impossible to build. That
   task is viable.
2. **The order must be evaluated at the declared envelope** (AMEND-006). A bounded-depth task is
   finite *by construction*, so quoting its unbounded closure is meaningless. `M` is counted at the
   envelope the thread declares, and the gate requires `M(D_max) >= 2^30` -- below that, a buildable
   automaton saturates the task and no candidate can be falsified on it.

So the gate answers one of three things, per task:

    DEAD    M(D_max) <  2^30   a feasible automaton saturates it; do not build on it
    VIABLE  M(D_max) >= 2^30   finite but unbuildable: a real benchmark
    LIVE    no closure found  unbounded state: a real benchmark

The Adversary asked for the 0.3 s version of this kill (`MSG-0008`); the Steward made the envelope
version mandatory (`AMEND-006`). Both are the same enumeration.
"""

import math

FEASIBLE_MAX = 2 ** 30          # AMEND-006: below this a buildable automaton saturates the task


# =========================================================================== enumeration
def closure_by_depth(gens, compose, start, max_depth, cap=4_000_000):
    """|{states reachable by composing at most d generators}| for d = 0..max_depth.

    Per-depth, not one global closure: at d=1 only |Sigma| composites exist, so a global closure would
    report 10,100 affine states at depth 1 where only 8 sequences exist -- states > sequences, which
    is the tell that the row is wrong rather than interesting.

    Returns (counts, exhausted_at). `exhausted_at` is the first depth at which the frontier empties,
    i.e. the closure is complete and finite -- the only reliable saturation signal. "The count did not
    move this round" is also true while a big group is still being explored.
    """
    seen = {start}
    frontier = [start]
    out = {0: 1}
    for d in range(1, max_depth + 1):
        nxt = []
        for s in frontier:
            for g in gens:
                t = compose(s, g)
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
                    if len(seen) > cap:
                        out[d] = len(seen)
                        return out, None
        frontier = nxt
        out[d] = len(seen)
        if not nxt:
            return out, d
    return out, None


def bits(n):
    return 0 if n <= 1 else math.ceil(math.log2(n))


def verdict(M):
    """AMEND-006's three-way answer, on the order M measured at the declared envelope."""
    if M is None:
        return "LIVE"
    return "DEAD" if M < FEASIBLE_MAX else "VIABLE"


def count_at(t, d):
    k = max(x for x in t["counts"] if x <= d) if t["counts"] else 0
    return t["counts"][k]


# =========================================================================== the tasks
def digit_addition():
    """State = carry. Envelope = 16 digit positions (the harness's declared width)."""
    gens = [(x, y) for x in range(10) for y in range(10)]
    depths = (1, 2, 4, 8, 16)
    counts, exh = closure_by_depth(gens, lambda c, g: (g[0] + g[1] + c) // 10, 0, 16)
    M = count_at({"counts": counts}, 16)
    return dict(name="digit addition mod 10^16 (positional)", alphabet=len(gens), counts=counts,
                depths=depths, M=M, envelope=16, verdict=verdict(M), sat=exh,
                note="the carry is 2 states at every depth; the ~40 points of exact accuracy that "
                     "training data bought were position coverage, not composition")


def affine_action():
    """State = an affine map x -> a*x + b over F_101. Envelope = 8 generators deep."""
    P = 101
    gens = [(a, b) for a in (2, 3, 5, 7) for b in (0, 1)]
    depths = (1, 2, 4, 8)

    def compose(s, g):
        a, b = s
        c, e = g
        return ((c * a) % P, (c * b + e) % P)

    counts, exh = closure_by_depth(gens, compose, (1, 0), 40)
    M = count_at({"counts": counts}, 8)
    return dict(name="affine action over F_101 (candidate 0004)", alphabet=len(gens),
                counts=counts, depths=depths, M=M, envelope=8, verdict=verdict(M), sat=exh,
                note=f"the composite of any sequence is one of {M:,} group elements; 8^d counts "
                     f"sequence NAMES, not states")


def dyck1_bounded(depth=16):
    """Dyck-1 with nesting capped at `depth` -- the task behind `nonregular.py` Task A1b.
    Reachable stack contents: the empty string and every run of openers up to `depth`, so M = depth+1.

    This is the row that matters for the harness: at the declared envelope D=16 the closure is **17
    states**, far below 2^30, so A1b is DEAD as a composition benchmark and alive only as a
    state-budget table. (The machine that *decides* it needs D+3 = 19 states -- `audit_harness.py`
    measures that; the closure is 17. Both are far below the gate.)"""
    M = depth + 1
    depths = (2, 4, 8, 16)
    counts = {d: min(d + 1, M) for d in depths}
    return dict(name=f"Dyck-1, nesting <= {depth} (nonregular.py Task A1b)", alphabet=2,
                counts=counts, depths=depths, M=M, envelope=depth, verdict=verdict(M), sat=depth,
                note=f"closes into {M} stack contents at the declared envelope; a {M}-state "
                     f"automaton (19 to decide it, per audit_harness.py) saturates the task")


def dyck2_bounded(depth):
    """Dyck-2 with nesting capped at `depth`. Stack contents range over every string in {A,B}^{<=D},
    so M = sum_{i<=D} 2^i = 2^(D+1) - 1. Regular, finite, and (above D~30) unbuildable."""
    M = 2 ** (depth + 1) - 1
    depths = tuple(d for d in (4, 8, 16, 32, 64) if d <= depth)
    counts = {d: 2 ** (d + 1) - 1 for d in depths}
    # smallest declared envelope at which this family is above the gate -- computed, not asserted
    cross = next(d for d in range(1, 4096) if 2 ** (d + 1) - 1 > FEASIBLE_MAX)
    return dict(name=f"Dyck-2, nesting <= {depth}", alphabet=4, counts=counts, depths=depths,
                cross=cross, M=M, envelope=depth, verdict=verdict(M), sat=None,
                note=f"M = 2^{depth + 1} - 1 = {M:.3e} at the declared envelope "
                     f"({bits(M)} bits)")


def dyck1_unbounded():
    """Dyck-1 with no depth cap: depth is unbounded, so no finite closure exists."""
    depths = (1, 2, 4, 8, 16, 32, 64)
    counts = {d: d + 1 for d in depths}
    return dict(name="Dyck-1, unbounded nesting", alphabet=2, counts=counts, depths=depths,
                M=None, envelope=None, verdict="LIVE", sat=None,
                note="depth is unbounded, so the state count grows without limit: no M-state machine "
                     "is exact for every depth")


def stream_binding():
    """State = the set of live bindings. No closure: composing d bindings yields one of |V|^d stores."""
    depths = (1, 2, 4, 8, 16)
    counts = {d: 1000 ** d for d in depths}
    return dict(name="stream binding + E-EDIT (nonregular.py Task B)", alphabet=1000, counts=counts,
                depths=depths, M=None, envelope=None, verdict="LIVE", sat=None,
                note="stores do not compose into a finite family; the bounded-RAM breakdown at "
                     "m << n is the measurable threshold")


# =========================================================================== reporting
def fmt(n):
    return f"{n:,}" if n < 10 ** 12 else f"{n:.2e}"


def report(t):
    print(f"### {t['name']}\n")
    print("| depth d | reachable states (<= d compositions) | sequences |Sigma|^d | ratio |")
    print("|---|---|---|---|")
    for d in t["depths"]:
        s, seqs = count_at(t, d), t["alphabet"] ** d
        print(f"| {d} | {fmt(s)} | {fmt(seqs)} | {s / seqs:.2e} |")
    print("")
    print("  *(states include the empty composite, the identity, so the d=1 ratio can exceed 1)*")
    print("")
    if t["envelope"] is not None:
        print(f"- **at the declared envelope D_max = {t['envelope']}: M = {fmt(t['M'])}, "
              f"{bits(t['M'])} bits of state**")
    print(f"- verdict: **{t['verdict']}** -- {t['note']}\n")


def main():
    print("# Pre-flight closure gate -- research/bench/closure.py")
    print("seed=none (enumeration is deterministic) python=3.11.2 CPU-only stdlib\n")
    print("Rule (`graveyard/0013`, corrected by `0015`/`0016` and by AMEND-006): a task whose")
    print("composites close into an order-M family at the **declared envelope** is saturated by an")
    print("M-state automaton iff M < 2^30. Check this BEFORE building a candidate.\n")

    tasks = [digit_addition(), affine_action(), dyck1_bounded(16), dyck2_bounded(32),
             dyck2_bounded(64), dyck1_unbounded(), stream_binding()]
    for t in tasks:
        report(t)

    print("## Verdict table (AMEND-006)\n")
    print("| task | envelope D_max | M at D_max | bits | verdict |")
    print("|---|---|---|---|---|")
    for t in tasks:
        env = "unbounded" if t["envelope"] is None else t["envelope"]
        M = "no closure" if t["M"] is None else fmt(t["M"])
        b = "--" if t["M"] is None else bits(t["M"])
        print(f"| {t['name']} | {env} | {M} | {b} | **{t['verdict']}** |")
    print("\nReading: digit addition and the affine action are dead benchmarks, both killed after they")
    print("were built. **Dyck-1 at the harness's declared D=16 closes into 17 states**, so Task A1b")
    print("cannot falsify a composition claim either -- it is a state-budget table, which is what")
    d2 = [t for t in tasks if t.get("cross") is not None]
    lo = d2[0]["cross"] - 1
    hi = d2[0]["cross"]
    print(f"Parts 9 and 10 say. Dyck-2 crosses the 2^30 gate at depth {hi}: M = {2 ** (lo + 1) - 1:,} "
          f"(depth {lo}) is below it, M = {2 ** (hi + 1) - 1:,} (depth {hi}) is above,")
    print(f"and it stays viable above: at D=32, M = {fmt(d2[0]['M'])} ({bits(d2[0]['M'])} bits); "
          f"at D=64, M = {fmt(d2[1]['M'])} ({bits(d2[1]['M'])} bits).")
    print("That is the surface a candidate needs, and it is the surface `nonregular.py` did not have.\n")
    print("### What would prove this gate wrong\n")
    print("A task with `M(D_max) < 2^30` on which a candidate beats the M-state automaton **without")
    print("losing accuracy** -- impossible for a deterministic decider under `graveyard/0013`, so a")
    print("positive result means the enumeration missed a generator, which is what this file catches.\n")
    print("Reproduce: python3 research/bench/closure.py")


if __name__ == "__main__":
    main()
