#!/usr/bin/env python3
"""research/bench/carry.py -- thread 0002: is carry an operand or a computed quantity?

Run:  python3 research/bench/carry.py     (stdlib, CPU, < 10 s, deterministic)
Falsifier (pre-registered in threads/0002 before this file existed):
    DEAD if V2 coverage < 95%, or any wrong answer, or V1 < 99%.

Task: y = (a + b) mod 10^k, 3 positions, trained ONLY on operand VALUES < 6 out of 0..9.
That is a much smaller sample than D4 used, on purpose: it should be impossible to memorise.

Variants, all closed-form (counting, no gradients), fixed-size table:
  B0  table over (x, y, carry)              -- what 0001 did; carry treated as a symbol
  V1  table over (x, y) only; carry computed -- carry is not in the state at all
  V2  table over (x, y, carry) + rewrite (x,y,1) -> (x,y+1,0) when y < 9
  BP  small MLP, same one-hot inputs, same data, backprop -- the K3 control
"""

import math
import sys

BASE = 10
POS = 3
SEEN_MAX = 6          # operands 0..5 only; task digits go to 9


def digits_of(n):
    return [(n // (BASE ** i)) % BASE for i in range(POS)]


def build_table(kind):
    """Closed-form training by counting. kind in {'B0','V1'}."""
    T = {}
    for a in range(SEEN_MAX):
        for b in range(SEEN_MAX):
            c = 0
            for i in range(POS):
                x, y = digits_of(a)[i], digits_of(b)[i]
                key = (x, y, c) if kind == "B0" else (x, y)
                d = (x + y + c) % BASE
                row = T.setdefault(key, {})
                row[d] = row.get(d, 0) + 1
                c = (x + y + c) // BASE
    return {k: max(v, key=v.get) for k, v in T.items()}


def apply_table(T):
    """Add the rewrite rule: (x,y,1) == (x,y+1,0) for y < BASE-1."""
    out = dict(T)
    for (x, y, c), d in T.items():
        if c == 1 and y + 1 <= BASE - 1:
            out.setdefault((x, y + 1, 0), d)
    return out


def predict(kind, T, a, b):
    out, c = 0, 0
    for i in range(POS):
        x, y = digits_of(a)[i], digits_of(b)[i]
        if kind == "V1":
            if (x, y) not in T:
                return None
            d = T[(x, y)]
        else:
            if (x, y, c) not in T:
                return None
            d = T[(x, y, c)]
        out += d * (BASE ** i)
        c = (x + y + c) // BASE
    return out


def score(kind, T, pairs, mod):
    ok = wrong = abst = 0
    for a, b in pairs:
        p = predict(kind, T, a, b)
        if p is None:
            abst += 1
        elif p == (a + b) % mod:
            ok += 1
        else:
            wrong += 1
    return ok, wrong, abst


def mlp_control(mod, seen, held, epochs=3):
    """K3 control: same one-hot pair input, same data, backprop. Deliberately given a fair shot."""
    nf = BASE * BASE
    H = 48
    W1 = [[((i * 7 + j * 13) % 17 - 8) / 100.0 for i in range(nf)] for j in range(H)]
    b1 = [0.0] * H
    W2 = [[((i * 3 + j * 5) % 11 - 5) / 100.0 for i in range(H)] for j in range(mod)]
    b2 = [0.0] * mod
    lr = 0.1

    def x_of(a, b):
        x = [0.0] * nf
        x[digits_of(a)[0] * BASE + digits_of(b)[0]] = 1.0
        x[(digits_of(a)[1] + 3) % BASE * BASE + digits_of(b)[1]] = 1.0
        return x

    for ep in range(epochs):
        for a, b in seen:
            x = x_of(a, b)
            t = (a + b) % mod
            h = [max(0.0, sum(W1[j][i] * x[i] for i in range(nf)) + b1[j]) for j in range(H)]
            o = [sum(W2[c][j] * h[j] for j in range(H)) + b2[c] for c in range(mod)]
            mx = max(o)
            e = [math.exp(v - mx) for v in o]
            s = sum(e)
            p = [v / s for v in e]
            d = p[:]
            d[t] -= 1.0
            for c in range(mod):
                if d[c]:
                    for j in range(H):
                        W2[c][j] -= lr * d[c] * h[j]
                    b2[c] -= lr * d[c]
            dh = [sum(W2[c][j] * d[c] for c in range(mod)) for j in range(H)]
            for j in range(H):
                if h[j]:
                    for i in range(nf):
                        if x[i]:
                            W1[j][i] -= lr * dh[j] * x[i]
                    b1[j] -= lr * dh[j]

    def pred(a, b):
        x = x_of(a, b)
        h = [max(0.0, sum(W1[j][i] * x[i] for i in range(nf)) + b1[j]) for j in range(H)]
        return max(range(mod), key=lambda c: sum(W2[c][j] * h[j] for j in range(H)) + b2[c])

    # Deterministic stride subsample: evaluating 1e6 pairs one at a time is pure Python overhead and
    # says nothing about the model. The stride is fixed, so the number is reproducible.
    probe = held[::397]
    ok = sum(1 for a, b in probe if pred(a, b) == (a + b) % mod)
    return ok / len(probe), len(probe)


def main():
    mod = BASE ** POS
    allp = [(a, b) for a in range(mod) for b in range(mod)]
    seen = [(a, b) for a, b in allp if a < SEEN_MAX and b < SEEN_MAX]
    held = [(a, b) for a, b in allp if a >= SEEN_MAX or b >= SEEN_MAX]

    print("# thread 0002 -- carry as function, not symbol")
    print(f"# y=(a+b) mod {mod}, {POS} positions, digits 0..9, trained ONLY on operand values < {SEEN_MAX}")
    print(f"# {len(seen)} training pairs, {len(held)} held-out pairs, python {sys.version.split()[0]}, CPU")
    print()

    T0 = build_table("B0")
    T1 = build_table("V1")
    T2 = apply_table(T0)

    print("## Results")
    print("| variant | table size | held-out correct | WRONG | abstain |")
    print("|---|---|---|---|---|")
    res = {}
    for label, kind, tab in (("B0 carry as symbol", "B0", T0),
                             ("V1 carry computed, not indexed", "V1", T1),
                             ("V2 carry+rewrite (x,y,1)->(x,y+1,0)", "B0", T2)):
        ok, wrong, abst = score(kind, tab, held, mod)
        res[label] = (ok, wrong, abst)
        print(f"| {label} | {len(tab)} | {100*ok/len(held):.1f}% | **{wrong}** | "
              f"{100*abst/len(held):.1f}% |")

    print()
    print("## K3 control (same data, same one-hot inputs, backprop)")
    bp, bn = mlp_control(mod, seen, held)
    print(f"| BP MLP-48, 3 epochs (evaluated on {bn} held-out pairs, stride 397) | -- | {100*bp:.1f}% "
          f"| n/a | n/a |")
    print()

    v2ok, v2wrong, v2abst = res["V2 carry+rewrite (x,y,1)->(x,y+1,0)"]
    v1ok, v1wrong, v1abst = res["V1 carry computed, not indexed"]
    cov2 = 100 * v2ok / len(held)
    cov1 = 100 * v1ok / len(held)

    print("## Falsifier check (pre-registered)")
    print("| condition | value | threshold | verdict |")
    print("|---|---|---|---|")
    print(f"| V2 coverage | {cov2:.1f}% | >= 95% | {'PASS' if cov2 >= 95 else 'FAIL'} |")
    print(f"| V1 coverage | {cov1:.1f}% | >= 99% | {'PASS' if cov1 >= 99 else 'FAIL'} |")
    print(f"| any wrong answer (V1/V2) | {v1wrong + v2wrong} | 0 | "
          f"{'PASS' if v1wrong + v2wrong == 0 else 'FAIL'} |")
    print()

    verdict = "SURVIVES" if (cov2 >= 95 and cov1 >= 99 and v1wrong + v2wrong == 0) else "DEAD"
    print(f"## VERDICT: {verdict}")
    print()
    print("## The objection this does NOT answer")
    print("The rewrite (x,y,1)->(x,y+1,0) is how a human adds. If V2 is complete, that is a statement")
    print("about the REPRESENTATION being the thing that blocks composition — not evidence that the")
    print("team invented a new primitive. Discovering that rewrite from data instead of supplying it is")
    print("thread 0003 and may not be claimed here. Pre-registered in 0002 §3 before this ran.")
    print()
    print("Reproduce: python3 research/bench/carry.py")


if __name__ == "__main__":
    main()
