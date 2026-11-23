#!/usr/bin/env python3
"""research/bench/symmetry.py -- thread 0001: does a VERIFIED symmetry recover the abstained part?

Run:  python3 research/bench/symmetry.py      (stdlib, CPU, ~10 s)
Falsifier (pre-registered in threads/0001, written before this file existed):
    DEAD if coverage gain < 10 points, or any wrong answer, or symmetry check fails.

The setup is deliberately the same task family as scorecard D4, so the numbers are comparable:
    y = (a + b) mod 10^k, trained ONLY on operands a,b < 16, tested on everything.

Three systems, identical data, identical closed-form trainer (counts, no gradients):
  B0  unshared table per operand pair          (what D2 did -- expect ~chance)
  B1  shared table over (digit_a, digit_b, carry)   (what D4 did -- expect ~55.7% coverage, 0 wrong)
  C   B1 + verified symmetry folding

The symmetry: addition of k-digit numbers is commutative, and the observed data VERIFIES it
(T[x][y][c] == T[y][x][c] for every observed key, no contradictions). Once verified on the observed
data only, the transposed entries may be filled in -- they were never observed, and they are not
invented either: they are implied by a property the data itself certifies.

That is the entire claim under test. If it recovers a real chunk of the 44.3% abstention with zero
new examples and zero new parameters, then D4's abstention is a *role algebra* and not merely a
lookup table that knows its own key space.
"""

import sys

BASE = 10
DIGITS = 2
SEEN_MAX = 16
M = BASE ** DIGITS


def digits_of(n):
    return [(n // (BASE ** i)) % BASE for i in range(DIGITS)]


def train(seen_max):
    """Shared role table: (x, y, carry) -> digit, by counting. Symmetry is NOT assumed here."""
    T = {}
    for a in range(seen_max):
        for b in range(seen_max):
            c = 0
            for i in range(DIGITS):
                x, y = digits_of(a)[i], digits_of(b)[i]
                row = T.setdefault((x, y, c), {})
                d = (x + y + c) % BASE
                row[d] = row.get(d, 0) + 1
                c = (x + y + c) // BASE
    return {k: max(v, key=v.get) for k, v in T.items()}


def check_symmetry(T):
    """Verify commutativity on OBSERVED data only. Returns (holds, checked, contradictions)."""
    checked = contra = 0
    for (x, y, c), d in T.items():
        j = (y, x, c)
        if j in T:
            checked += 1
            if T[j] != d:
                contra += 1
    return contra == 0, checked, contra


def fold_symmetry(T):
    """Fill MIRRORED entries that were never observed, using the verified symmetry.
    Never overwrites an observed entry; never invents a third possibility."""
    out = dict(T)
    filled = 0
    for (x, y, c), d in T.items():
        j = (y, x, c)
        if j not in out:
            out[j] = d
            filled += 1
    return out, filled


def predict(T, a, b):
    """Recursive application of the SAME table at every position. None = abstain."""
    out, c = 0, 0
    for i in range(DIGITS):
        x, y = digits_of(a)[i], digits_of(b)[i]
        if (x, y, c) not in T:
            return None
        out += T[(x, y, c)] * (BASE ** i)
        c = (x + y + c) // BASE
    return out


def score(T, pairs):
    ok = wrong = abst = 0
    for a, b in pairs:
        p = predict(T, a, b)
        if p is None:
            abst += 1
        elif p == (a + b) % M:
            ok += 1
        else:
            wrong += 1
    return ok, wrong, abst


def main():
    all_pairs = [(a, b) for a in range(M) for b in range(M)]
    seen = [(a, b) for a, b in all_pairs if a < SEEN_MAX and b < SEEN_MAX]
    held = [(a, b) for a, b in all_pairs if a >= SEEN_MAX or b >= SEEN_MAX]

    print("# thread 0001 -- verified symmetry vs abstention")
    print(f"# y = (a+b) mod {M}; trained on a,b < {SEEN_MAX} ({len(seen)} pairs); "
          f"held out {len(held)} pairs")
    print(f"# python {sys.version.split()[0]}, CPU, stdlib, fully deterministic (no RNG used)")
    print()

    T = train(SEEN_MAX)
    holds, checked, contra = check_symmetry(T)
    print("## Symmetry verification (observed data only)")
    print(f"| question | answer |")
    print(f"|---|---|")
    print(f"| commutativity holds on observed keys? | {'YES' if holds else 'NO'} |")
    print(f"| keys checked | {checked} |")
    print(f"| contradictions | {contra} |")
    print()

    Tf, filled = fold_symmetry(T)
    print("## Coverage and exactness")
    print("| system | table entries | held-out correct | held-out WRONG | abstain |")
    print("|---|---|---|---|---|")

    rows = []
    for name, tab in (("B1 shared table (D4 baseline)", T),
                      ("C  shared + verified symmetry", Tf)):
        ok, wrong, abst = score(tab, held)
        rows.append((name, len(tab), ok, wrong, abst))
        print(f"| {name} | {len(tab)} | {100*ok/len(held):.1f}% | **{wrong}** | "
              f"{100*abst/len(held):.1f}% |")

    print()
    (_, e1, ok1, w1, ab1), (_, e2, ok2, w2, ab2) = rows
    gain = 100 * (ok2 - ok1) / len(held)
    rescued = ab1 - ab2
    print(f"## Falsifier check")
    print(f"| condition | value | threshold | verdict |")
    print(f"|---|---|---|---|")
    print(f"| coverage gain | {gain:+.1f} pts | must be >= +10 | "
          f"{'PASS' if gain >= 10 else 'FAIL'} |")
    print(f"| wrong answers | {w2} | must be 0 | {'PASS' if w2 == 0 else 'FAIL'} |")
    print(f"| symmetry holds | {holds} | must be True | {'PASS' if holds else 'FAIL'} |")
    print(f"| abstentions rescued | {rescued} | (informational) | |")
    print(f"| extra entries | +{e2-e1} | (from symmetry, not from data) | |")
    print()

    ok_after, wrong_after, abst_after = ok2, w2, ab2
    print(f"Of {ab1} abstentions, **{rescued} were answered correctly and {wrong_after} were answered"
          f" wrongly**.")
    print(f"Remaining abstentions: {abst_after} — every one of them is a cell that neither the data")
    print("nor the verified symmetry can reach. That is the honest boundary of this method, and it is")
    print("enumerable rather than a mystery (#CHARTER G8).")

    verdict = "SURVIVES" if (gain >= 10 and w2 == 0 and holds) else "DEAD"
    print(f"\n## VERDICT: {verdict}")
    print("Command to reproduce: python3 research/bench/symmetry.py")


if __name__ == "__main__":
    main()
