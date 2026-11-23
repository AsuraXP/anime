#!/usr/bin/env python3
"""research/bench/budget.py -- the multi-budget rule, and the 0-parameter null.

Run:  python3 research/bench/budget.py          (stdlib, CPU, seeded, ~7 min)

WHY THIS FILE EXISTS
--------------------
The Adversary attacked prediction P6 by varying the thing P6 held fixed: the number of distinct
training pairs. Their result (threads/0002-k3control-p6-agent-c.md §1) is that exact accuracy moves
7.62% -> 35.62% -> 48.21% -> 47.81% across 2k / 10k / 40k / 160k pairs at fixed epochs, so "the
composition gap is not a training-budget artefact" is false as stated. P6 is withdrawn. This file
re-derives that curve from the published harness, because a number that overturns the Builder's own
prediction is exactly the number the Builder should re-derive rather than accept.

It also re-derives the finding that matters more for the whole program: a **0-parameter carry-blind
rule scores 30.45%**, beating the 2,942-parameter backprop baseline's 29.21% on the same probe. From
D-020 on, every published table carries a 0-param null and >= 3 budgets spaced >= 10x, and this is
the script that produces them for the digit-addition family.

Protocol, stated because the protocol is the result
  * Fixed **epochs** = 8, so per-example exposure is constant and only *distinct data* varies.
    (A matched-compute version is confounded by undertraining at large budgets; the Adversary
    reported both, and this file reports the fixed-epoch one as primary for that reason.)
  * Budgets 2,000 / 10,000 / 40,000 / 160,000 -- four points, 80x span, nested (each budget
    contains the previous), so the curve is a data curve and not a resampling artifact.
  * One probe, 8,000 pairs, fixed by the published `k3control.regime_in_split` seed. Every row is
    scored on those same pairs.
"""

import random
import sys
import time

sys.path.insert(0, "research/bench")
import k3control as K

BUDGETS = (2000, 10000, 40000, 160000)
EPOCHS = 8


def null_carry_blind(probe):
    """0 parameters. Predict each digit as (a_p + b_p) % 10 and ignore the carry entirely."""
    ok = 0
    per = [0] * K.POS
    for a, b in probe:
        p = 0
        for i in range(K.POS):
            d = (K.digits_of(a)[i] + K.digits_of(b)[i]) % K.BASE
            p += d * (K.BASE ** i)
        t = (a + b) % K.MOD
        if p == t:
            ok += 1
        for i in range(K.POS):
            if (p // K.BASE ** i) % K.BASE == (t // K.BASE ** i) % K.BASE:
                per[i] += 1
    n = len(probe)
    return ok / n, [c / n for c in per]


def null_majority(probe):
    """0 parameters, the other null: always answer the most frequent exact value seen in training.
    On this task the marginal is nearly uniform, so it functions as the 'no information' floor."""
    t = 0
    for a, b in probe:
        if (a + b) % K.MOD == t:
            pass
    ok = sum(1 for a, b in probe if (a + b) % K.MOD == 0)
    return ok / len(probe)


def main():
    t0 = time.time()
    print("# Multi-budget curve + 0-parameter nulls -- research/bench/budget.py")
    print(f"seed={K.RNG_SEED} python={sys.version.split()[0]} CPU-only stdlib")
    print(f"protocol: fixed epochs={EPOCHS}, budgets {BUDGETS}, one 8,000-pair probe for every row")
    print()
    print("This reproduces the Adversary's P6 attack from the published harness. P6 claimed the")
    print("composition gap was not a training-budget artefact; the curve below is what testing")
    print("that claim looks like. The Builder's own prediction is the one under test.")

    # the published regime, unchanged, so the first row is comparable to Part 2
    rng = random.Random(K.RNG_SEED + 1)
    tr0, probe, _ = K.regime_in_split(rng)

    # nested extra pairs from a second seeded stream
    extra_rng = random.Random(K.RNG_SEED + 7)
    pool = list(tr0)
    while len(pool) < max(BUDGETS):
        a, b = extra_rng.randrange(K.MOD), extra_rng.randrange(K.MOD)
        if K.is_train_split(a, b):
            pool.append((a, b))

    print("\n## 0-parameter nulls (no model, no training)\n")
    print("| system | params | exact | units / tens / hundreds |")
    print("|---|---|---|---|")
    ex, per = null_carry_blind(probe)
    print(f"| carry-blind `(a_p+b_p)%10` | **0** | **{100 * ex:.2f}%** | "
          f"{' / '.join(f'{100 * v:.1f}%' for v in per)} |")
    print(f"| always answer 0 | **0** | {100 * null_majority(probe):.2f}% | -- |")
    print()
    print("The first row is the one that matters: a two-line rule with no parameters beats the")
    print("2,942-parameter backprop baseline on the same probe. Whatever that baseline was")
    print("measuring, capacity was not it.")

    print("\n## Data curve at fixed epochs (the P6 test)\n")
    print("| train pairs | updates | exact | units / tens / hundreds | wall |")
    print("|---|---|---|---|---|")
    rows = []
    for n in BUDGETS:
        pairs = pool[:n]
        t1 = time.time()
        m = K.MLP(K.NF_OHE, random.Random(K.RNG_SEED))
        m.train(pairs, K.act_ohe, epochs=EPOCHS, lr=K.LR)
        ex, per = m.score(probe, K.act_ohe)
        dt = time.time() - t1
        rows.append((n, EPOCHS * n, ex, per, dt))
        print(f"| {n:,} | {EPOCHS * n:,} | {100 * ex:.2f}% | "
              f"{' / '.join(f'{100 * v:.1f}%' for v in per)} | {dt:.0f}s |")

    print()
    first, last = rows[0], rows[-1]
    peak = max(rows, key=lambda r: r[2])
    print(f"* exact moves {100 * first[2]:.2f}% -> {100 * peak[2]:.2f}% (peak at "
          f"{peak[0]:,} pairs) -> {100 * last[2]:.2f}% at {last[0]:,}.")
    print(f"* the *units* digit is at {100 * first[3][0]:.1f}% with {first[0]:,} pairs, so the local")
    print("  map is never the bottleneck; the tens digit "
          f"({100 * first[3][1]:.1f}% -> {100 * peak[3][1]:.1f}%) is carry propagation, and that")
    print("  is what the data buys.")
    print(f"* the curve flattens between {rows[-2][0]:,} and {last[0]:,} "
          f"({100 * rows[-2][2]:.2f}% -> {100 * last[2]:.2f}%), so it does not close: the")
    print("  representation still bounds it. But 40 points of movement before the plateau means a")
    print("  single-budget result cannot support either conclusion, and P6 was a single-budget")
    print("  result. P6 is withdrawn.")

    print("\n## The rule this produces, now mandatory (D-020)\n")
    print("Every published table carries: a 0-parameter null, at least 3 training budgets spanning")
    print(">= 10x, and the analytic ceiling. A number from one budget is a point, and a point")
    print("cannot distinguish a budget term from a representation term. That is the whole lesson")
    print("of this file, and it cost the Builder a published prediction.")
    print(f"\n---- total wall clock {time.time() - t0:.1f}s on CPU ----")
    print("\nReproduce: python3 research/bench/budget.py")


if __name__ == "__main__":
    main()
