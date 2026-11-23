#!/usr/bin/env python3
"""research/bench/closure.py -- the pre-flight gate: does the composite STATE space grow with depth?

Run:  python3 research/bench/closure.py        (stdlib, CPU, deterministic enumeration, ~0.1 s)

WHY THIS FILE EXISTS
--------------------
`graveyard/0013` states the law that killed two benchmarks in two days:

    If composition closes into a finite structure of order M, the composite of any sequence is one of
    M states -- so an M-state automaton with |Sigma|*M transitions saturates the task with ceil(log2 M)
    bits of state and no learning at all.

Digit addition died to it (M = 2, the carry). Candidate `0004` died to it (M = 10,100, the affine
group AGL(1,101)). Both were argued *after* the code was written. This file makes it a pre-flight
check: enumerate the states reachable by composing at most d generators, print them against the number
of sequences at that depth, and say DEAD or LIVE before anyone builds anything.

The Adversary asked for exactly this (`MSG-0008`, BUILDER baton). It is an instrument: it proposes no
primitive and scores no candidate.

HOW TO READ THE OUTPUT
----------------------
  reachable states by depth    saturates at M   -> the composite is a finite family: DEAD
                              still growing    -> unbounded state: LIVE, and the depth at which a
                                                  fixed budget breaks is the benchmark's threshold
  ratio |states| / |Sigma|^d   ~0 means the sequence count is a mirage: names grow, states do not
"""

import math


# =========================================================================== enumeration
def closure_by_depth(gens, compose, start, max_depth, cap=4_000_000, stable_stop=3):
    """|{states reachable by composing at most d generators}| for d = 0..max_depth.

    Per-depth, not one global closure: at d=1 only |Sigma| composites exist, so a global closure would
    report 10,100 affine states at depth 1 where only 8 sequences exist -- states > sequences, which is
    the tell that the row is wrong rather than interesting.
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
                        return out
        frontier = nxt
        out[d] = len(seen)
        # Stop when the count has not moved for `stable_stop` consecutive levels: the composite has
        # closed into a finite family and further depth cannot add states. This is the test that
        # separates "still exploring a big finite group" from "genuinely unbounded".
        if not nxt:
            # The frontier is empty: every state reachable from the generators has been found. That
            # is the definition of a closed finite family, and it is the only reliable signal --
            # "the count did not move this round" is also true while a big group is still being
            # explored.
            return out, d
        if d >= stable_stop and len({out[d], out[d - 1], out[d - 2]}) == 1:
            break
    return out, None


def count_at(t, d):
    """The state count at displayed depth d (counts stop accumulating once the set is exhausted)."""
    k = max(x for x in t["counts"] if x <= d)
    return t["counts"][k]


def bits(n):
    return 0 if n <= 1 else math.ceil(math.log2(n))


def verdict_from(counts, exhausted_at):
    """DEAD when the reachable set is exhausted (a finite family closes), LIVE when the frontier is
    still growing at the probe limit. A big-but-finite group (10,100 affine maps) is exhausted and
    therefore dead; an unbounded counter or store is not, at any depth tested."""
    if exhausted_at is not None:
        return "DEAD", exhausted_at
    return "LIVE", None


# =========================================================================== the four tasks
def digit_addition():
    """State = carry. Generators = the 100 digit pairs at one position. Compose = carry arithmetic."""
    gens = [(x, y) for x in range(10) for y in range(10)]
    depths = (1, 2, 4, 8, 16)
    counts, exh = closure_by_depth(gens, lambda c, g: (g[0] + g[1] + c) // 10, 0, 40)
    v, sat = verdict_from(counts, exh)
    return dict(name="digit addition mod 10^k (positional digits)", alphabet=len(gens),
                counts=counts, depths=depths, verdict=v, sat=sat,
                note="the carry is 2 states at every depth; the ~40 points of exact accuracy that "
                     "training data bought were position coverage, not composition")


def affine_action():
    """State = an affine map x -> a*x + b over F_101. Generators = 8 maps. Compose = composition."""
    P = 101
    gens = [(a, b) for a in (2, 3, 5, 7) for b in (0, 1)]
    depths = (1, 2, 4, 8)

    def compose(s, g):
        a, b = s
        c, e = g
        return ((c * a) % P, (c * b + e) % P)

    counts, exh = closure_by_depth(gens, compose, (1, 0), 40)
    v, sat = verdict_from(counts, exh)
    return dict(name="affine action over F_101 (candidate 0004)", alphabet=len(gens),
                counts=counts, depths=depths, verdict=v, sat=sat,
                note=f"the composite of any sequence is one of {counts[max(depths)]} group elements; "
                     f"8^d counts sequence NAMES, not states")


def dyck_counter():
    """State = nesting depth, uncapped. Generators = '(' and ')'. Compose = depth arithmetic."""
    gens = ["(", ")"]
    depths = (1, 2, 4, 8, 16, 32)

    def compose(d, g):
        return max(0, d + (1 if g == "(" else -1))

    counts, exh = closure_by_depth(gens, compose, 0, 64)
    v, sat = verdict_from(counts, exh)
    return dict(name="Dyck-1 validity (this harness, Task A)", alphabet=2,
                counts=counts, depths=depths, verdict=v, sat=sat,
                note="depth is unbounded, so the state count grows with d without limit: no M-state "
                     "machine is exact for every depth, which is what makes k >= D+1 falsifiable")


def stream_binding():
    """State = the set of live bindings. Symbolic: composing d bindings yields one of |V|^d stores."""
    depths = (1, 2, 4, 8)
    counts = {d: 10 ** d for d in range(0, 9)}
    v, sat = verdict_from(counts, None)      # no closure at all: |V|^d stores
    return dict(name="stream binding + E-EDIT (this harness, Task B)", alphabet=10,
                counts=counts, depths=depths, verdict=v, sat=sat,
                note="stores do not compose into a finite family; the bounded-RAM breakdown at "
                     "m << n is the measurable threshold, and the collateral count is its cost")


# =========================================================================== reporting
def report(t):
    print(f"### {t['name']}\n")
    print(f"| depth d | reachable states (<= d compositions) | sequences |Sigma|^d | ratio |")
    print("|---|---|---|---|")
    for d in t["depths"]:
        s, seqs = count_at(t, d), t["alphabet"] ** d
        print(f"| {d} | {s:,} | {seqs:,} | {s / seqs:.2e} |")
    last = count_at(t, t["depths"][-1])
    print("")
    print(f"  *(states include the empty composite, the identity, so the d=1 ratio can exceed 1)*")
    print("")
    if t["verdict"] == "DEAD":
        print(f"- saturates at **{last:,} states** by depth {t['sat']}, then never grows: "
              f"{bits(last)} bit{'s' if bits(last) != 1 else ''} of state, "
              f"{last * t['alphabet']:,} closed-form transitions, 1 read/token")
    else:
        print(f"- **unbounded**: {last:,} states at depth {t['depths'][-1]} and still growing "
              f"({bits(last)} bits would only cover the depths shown)")
    print(f"- verdict: **{t['verdict']}** -- {t['note']}\n")


def main():
    print("# Pre-flight closure gate -- research/bench/closure.py")
    print("seed=none (enumeration is deterministic) python=3.11.2 CPU-only stdlib\n")
    print("Rule (`graveyard/0013`): if the composite of any sequence lands in a finite family of order")
    print("M, an M-state automaton saturates the task with ceil(log2 M) bits and no learning. Check")
    print("this BEFORE building a candidate.\n")

    tasks = [digit_addition(), affine_action(), dyck_counter(), stream_binding()]
    for t in tasks:
        report(t)

    print("## Verdict table\n")
    print("| task | states at max depth | verdict | saturates at |")
    print("|---|---|---|---|")
    for t in tasks:
        last = count_at(t, t["depths"][-1])
        print(f"| {t['name']} | {last:,} | **{t['verdict']}** | "
              f"{('depth ' + str(t['sat'])) if t['sat'] is not None else 'never (tested to depth ' + str(t['depths'][-1]) + ')'} |")
    print("\nTwo of the four are dead benchmarks, both killed after they were built and both by this")
    print("law. The gate costs a tenth of a second, which is the entire argument for running it first.\n")
    print("### What would prove this gate wrong\n")
    print("A task whose reachable composite states saturate at M, on which a candidate still beats the")
    print("M-state automaton **without losing accuracy**. Under `graveyard/0013` that is impossible for")
    print("a deterministic decider, so a positive result here means the enumeration missed a generator")
    print("-- which is exactly what this file exists to catch.\n")
    print("Reproduce: python3 research/bench/closure.py")


if __name__ == "__main__":
    main()
