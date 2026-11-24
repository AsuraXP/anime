#!/usr/bin/env python3
"""research/bench/nonregular.py -- the non-regular benchmark, instrument only.

Run:  python3 research/bench/nonregular.py        (stdlib, CPU, seeded, ~5 min)

WHY THIS FILE EXISTS
--------------------
D-020 / AMEND-002 retired positional digit addition as a testbed, and `ceiling.py` says why: it is a
finite-state function whose entire state is a 1-bit carry, so a 200-entry table is exact at any depth
and no stratum of it can falsify anything. A benchmark in which every method scores its own ceiling
measures key coverage.

This file builds the replacement the Steward asked for: tasks whose **required state grows with
depth or stream length**, so a fixed-state baseline must break, and so a falsifier has somewhere to
fail.

  TASK A -- Dyck-1 validity. Nested brackets, max depth D. Deciding validity requires a counter that
            reaches D+1 values. A k-state machine is exact iff k >= D+1 and cannot be better than
            its cap below that. Measured: accuracy on a (state budget k) x (max depth D) grid.

  TASK B -- stream binding + E-EDIT. n key->value bindings arrive, then queries, then ONE edit, then
            the same queries again. Working RAM is capped at m slots. G7 asks for zero collateral
            damage on unrelated keys. Measured: recall and collateral vs n, for m fixed.

INSTRUMENT ONLY. This file proposes no primitive. It supplies what every candidate in this family
needs in order to be measured, and what the Adversary needs in order to check that a baseline is
below its ceiling before any candidate is scored.

Baselines in every table, in the order AMEND-001 requires
  0-param null      the constant answer (the floor)
  fixed-state       the smallest state-capped machine that could plausibly do the task
  recurrent         a small Elman RNN with h units, at >= 3 training budgets spanning >= 10x
  analytic ceiling  what an unbounded-state solution would score (100% on both tasks -- both are
                    decidable with enough state, which is exactly why they are usable as tests)
"""

import math
import random
import sys
import time

SEED = 20261123
CHARS = "()"


# ===========================================================================  TASK A: Dyck-1
def dyck_word(rng, pairs):
    """Uniform-ish random Dyck word with `pairs` pairs, by recursive splitting of the first pair."""
    if pairs == 0:
        return ""
    k = rng.randrange(pairs)
    return "(" + dyck_word(rng, k) + ")" + dyck_word(rng, pairs - 1 - k)


def make_balanced_set(rng, n, pairs, valid_frac=0.5):
    """Half valid words, half made invalid by a single one-character corruption."""
    out = []
    for _ in range(n):
        w = dyck_word(rng, pairs)
        if rng.random() < valid_frac:
            out.append((w, 1))
        else:
            i = rng.randrange(len(w))
            bad = w[:i] + (")" if w[i] == "(" else "(") + w[i + 1:]
            out.append((bad, 0))
    return out


def word_at_depth(rng, D):
    """A word whose maximum nesting is exactly D. `dyck_word` inserts balanced pairs at random, so a
    depth-D excursion is exponentially rare for large D and a 400-string sample at D=16 almost never
    dives. That is why the first grid showed a k=8 machine surviving at D=16 -- the sample was
    shallow, not the machine. This pins the excursion so the state requirement is exercised."""
    m = rng.randrange(0, 4)
    return "(" * D + "()" * m + ")" * D


def make_depth_set(rng, n, D):
    """Half valid words reaching depth D, half with one bracket flipped (therefore invalid)."""
    out = []
    for _ in range(n):
        w = word_at_depth(rng, D)
        if rng.random() < 0.5:
            out.append((w, 1))
        else:
            c = list(w)
            k = rng.randrange(len(c))
            c[k] = ")" if c[k] == "(" else "("
            out.append(("".join(c), 0))
    return out


def make_control_set(rng, n, pairs):
    """Control task for the recurrent baseline: label = "does the string end at depth 0?".

    Half the items are balanced words (end at 0), half are `"(" + w` (end at 1 but still finish with
    a closing bracket). The first version also used `w + "("` as the invalid class, which created a
    75% shortcut -- "does it end in `)`?" -- and every budget found it, scoring exactly 73.50% three
    times. A control whose answer can be read off the last character controls nothing. With only
    prefix-invalid items, the running count is the only cue, so a model that scores here is
    actually carrying state.
    """
    out = []
    for _ in range(n):
        w = dyck_word(rng, pairs)
        out.append((w, 1) if rng.random() < 0.5 else ("(" + w, 0))
    return out


def make_balance_set(rng, n, pairs):
    """Kept for the published turn-4 tables and for `certify.py`. Superseded by `make_control_set`
    for baseline reporting: see the shortcut note there."""
    out = []
    for _ in range(n):
        w = dyck_word(rng, pairs)
        u = rng.random()
        if u < 0.5:
            out.append((w, 1))
        elif u < 0.75:
            out.append((w + "(", 0))
        else:
            out.append(("(" + w, 0))
    return out


def depth_of(w):
    d = best = 0
    for ch in w:
        d += 1 if ch == "(" else -1
        best = max(best, d)
    return best


class CappedCounter:
    """A k-state baseline: the counter saturates at k-1. The *readout* is learned by counting over
    (final state, underflow seen) -> label; the state transition is fixed by the architecture. This
    is the honest analogue of D4's role table: a fixed machine with a counted readout."""

    def __init__(self, k):
        self.k = k

    def trace(self, w):
        s, under = 0, 0
        for ch in w:
            if ch == "(":
                s = min(s + 1, self.k - 1)
            else:
                if s == 0:
                    under = 1
                else:
                    s = max(s - 1, 0)
        return (s, under)

    def fit(self, pairs):
        counts = {}
        for w, y in pairs:
            key = self.trace(w)
            row = counts.setdefault(key, [0, 0])
            row[y] += 1
        self.T = {k: (0 if v[0] >= v[1] else 1) for k, v in counts.items()}
        self.default = 0 if sum(v[0] for v in counts.values()) >= sum(v[1] for v in counts.values()) \
            else 1
        return self

    def predict(self, w):
        return self.T.get(self.trace(w), self.default)


def score_binary(predict, data):
    return sum(1 for w, y in data if predict(w) == y) / len(data)


class RNN:
    """Elman RNN, 2 inputs, h hidden units, 2-way softmax readout, BPTT with Adam. This is the
    bounded-state neural baseline: it carries h floats of state across the whole string, which is
    what the charter bounds.

    HISTORY, because it is the point. The first version of this class sat at chance on every task
    and the failure was blamed on the task three times before it was blamed on the code. Three bugs
    were found (one-step-only BPTT, a transposed recurrent gradient, in-place mutation feeding its
    own gradient). The fourth problem was optimisation and is fixed here:
      * centered inputs (+/-1) instead of 0/1, so the input weights have no constant bias to fight;
      * init scaled by 1/sqrt(h), so pre-activations start inside tanh's live range instead of
        saturating on step one (saturation is what froze |h| at 1 and made every budget identical);
      * global-norm gradient clipping at gmax, so one bad string cannot blow the weights out;
      * Adam, because plain SGD on a tanh recurrence needs a learning rate that is either too small
        to leave the initial plateau or large enough to saturate the units.
    Even with all of that, learning is **bimodal**: a restart either finds the rule and is exact, or
    it stalls at chance. So the baseline is reported as a median over restarts plus a success rate,
    never as one run -- a single run would have called this baseline "82% or 48%" depending on luck.
    """

    def __init__(self, hid, rng):
        self.h = hid
        sc = 0.5 / math.sqrt(max(1, hid))
        self.Wx = [[rng.uniform(-sc, sc) for _ in range(2)] for _ in range(hid)]
        self.Wh = [[rng.uniform(-sc, sc) for _ in range(hid)] for _ in range(hid)]
        self.b = [0.0] * hid
        self.Wo = [[rng.uniform(-sc, sc) for _ in range(hid)] for _ in range(2)]
        self.bo = [0.0, 0.0]

    def nparams(self):
        return self.h * 2 + self.h * self.h + self.h + 2 * self.h + 2

    @staticmethod
    def _x(ch):
        return [1.0, -1.0] if ch == "(" else [-1.0, 1.0]

    def forward(self, w):
        hs = []
        h = [0.0] * self.h
        for ch in w:
            x = self._x(ch)
            nh = []
            for j in range(self.h):
                acc = self.b[j] + self.Wx[j][0] * x[0] + self.Wx[j][1] * x[1]
                for k in range(self.h):
                    acc += self.Wh[j][k] * h[k]
                nh.append(math.tanh(acc))
            hs.append(nh)
            h = nh
        o = [self.bo[c] + sum(self.Wo[c][j] * h[j] for j in range(self.h)) for c in (0, 1)]
        mx = max(o)
        e = [math.exp(v - mx) for v in o]
        z = sum(e)
        return hs, [v / z for v in e]

    def _groups(self):
        return ("Wh", "Wx", "b", "Wo", "bo")

    def train(self, data, epochs, rng, lr=0.01, B=16, gmax=1.0,
              b1=0.9, b2=0.999, eps=1e-8):
        h = self.h
        P = {"Wh": self.Wh, "Wx": self.Wx, "b": self.b, "Wo": self.Wo, "bo": self.bo}

        def zeros_like(v):
            if isinstance(v[0], list):
                return [[0.0] * len(r) for r in v]
            return [0.0] * len(v)

        M = {k: zeros_like(v) for k, v in P.items()}
        V = {k: zeros_like(v) for k, v in P.items()}
        step = 0
        for _ in range(epochs):
            order = list(range(len(data)))
            rng.shuffle(order)
            for s0 in range(0, len(order), B):
                G = {k: zeros_like(v) for k, v in P.items()}
                nb = 0
                for idx in order[s0:s0 + B]:
                    w, y = data[idx]
                    nb += 1
                    hs, p = self.forward(w)
                    g = [p[c] - (1.0 if c == y else 0.0) for c in (0, 1)]
                    hT = hs[-1] if hs else [0.0] * h
                    dh = [0.0] * h
                    for c in (0, 1):
                        if g[c]:
                            G["bo"][c] += g[c]
                            for j in range(h):
                                dh[j] += self.Wo[c][j] * g[c]
                                G["Wo"][c][j] += g[c] * hT[j]
                    for t in range(len(w) - 1, -1, -1):
                        ht = hs[t]
                        hprev = hs[t - 1] if t > 0 else [0.0] * h
                        d = [dh[j] * (1 - ht[j] * ht[j]) for j in range(h)]
                        x = self._x(w[t])
                        # recurrence gradient from the CURRENT Wh, before any mutation
                        nxt = [sum(self.Wh[j][k] * d[j] for j in range(h)) for k in range(h)]
                        for j in range(h):
                            if d[j]:
                                G["b"][j] += d[j]
                                G["Wx"][j][0] += d[j] * x[0]
                                G["Wx"][j][1] += d[j] * x[1]
                                for k in range(h):
                                    G["Wh"][j][k] += d[j] * hprev[k]
                        dh = nxt
                tot = 0.0
                for k in self._groups():
                    v = G[k]
                    if isinstance(v[0], list):
                        for row in v:
                            for x in row:
                                tot += x * x
                    else:
                        for x in v:
                            tot += x * x
                norm = math.sqrt(tot) / max(1, nb)
                scale = (gmax / norm) if norm > gmax else 1.0
                step += 1
                for k in self._groups():
                    Pk, Mk, Vk, Gk = P[k], M[k], V[k], G[k]
                    if isinstance(Gk[0], list):
                        for i in range(len(Gk)):
                            for j in range(len(Gk[i])):
                                gr = Gk[i][j] / max(1, nb) * scale
                                Mk[i][j] = b1 * Mk[i][j] + (1 - b1) * gr
                                Vk[i][j] = b2 * Vk[i][j] + (1 - b2) * gr * gr
                                mh = Mk[i][j] / (1 - b1 ** step)
                                vh = Vk[i][j] / (1 - b2 ** step)
                                Pk[i][j] -= lr * mh / (math.sqrt(vh) + eps)
                    else:
                        for i in range(len(Gk)):
                            gr = Gk[i] / max(1, nb) * scale
                            Mk[i] = b1 * Mk[i] + (1 - b1) * gr
                            Vk[i] = b2 * Vk[i] + (1 - b2) * gr * gr
                            mh = Mk[i] / (1 - b1 ** step)
                            vh = Vk[i] / (1 - b2 ** step)
                            Pk[i] -= lr * mh / (math.sqrt(vh) + eps)

    def predict(self, w):
        p = self.forward(w)[1]
        return 0 if p[0] >= p[1] else 1

    def confidence(self, w):
        p = self.forward(w)[1]
        return max(p), (0 if p[0] >= p[1] else 1)


def task_a():
    print("\n## TASK A -- Dyck-1 validity (state must reach D+1 values)\n")
    print("AMEND-003 opening line, Task A:")
    print("  Minimal automaton for this task: a deterministic PDA with an unbounded stack (any")
    print("  single-counter machine decides Dyck-1 in O(1) *work* per token).")
    print("  Gate it fails: **G2**, because the stack is working state that grows O(D) with depth,")
    print("  which breaks the bounded-RAM envelope; on a bounded machine the same automaton becomes")
    print("  the k-state counter measured below.")
    print("  A candidate must beat the k-state machine below its requirement -- measured as `D+3`")
    print("  states in `audit_harness.py`, not `D+1` -- without growing working state, and must not")
    print("  lose accuracy above it.\n")
    rng = random.Random(SEED)

    # fixed-state baselines on a (state budget) x (max depth) grid
    print("### A1. Fixed-state machine vs required depth (0-param null included)\n")
    print("| state budget k | D=2 | D=4 | D=8 | D=16 |")
    print("|---|---|---|---|---|")
    grid = {}
    for k in (2, 4, 8, 16):
        cells = []
        for D in (2, 4, 8, 16):
            data = make_balanced_set(random.Random(SEED + 100 * D + k), 400, D)
            m = CappedCounter(k).fit(data)
            acc = score_binary(m.predict, data)
            grid[(k, D)] = acc
            cells.append(f"{100 * acc:.1f}%")
        print(f"| {k} | " + " | ".join(cells) + " |")

    null = make_balanced_set(random.Random(SEED + 999), 400, 16)
    null_acc = max(sum(1 for _, y in null if y == c) for c in (0, 1)) / len(null)
    print(f"\n| 0-param null (always the majority class) | | | | **{100 * null_acc:.1f}%** |")
    print("\n### A1b. Same grid, with the depth actually reached (A1's sample was shallow)\n")
    print("`dyck_word` inserts balanced pairs at random, so a 400-string sample at D=16 almost never")
    print("dives; that is why k=8 survives at 99.8% in A1. Below, every string reaches depth D by")
    print("construction, so the state requirement is actually exercised.\n")
    print("| state budget k | D=2 | D=4 | D=8 | D=16 |")
    print("|---|---|---|---|---|")
    for k in (2, 4, 8, 16):
        cells = []
        for D in (2, 4, 8, 16):
            data = make_depth_set(random.Random(SEED + 1000 * D + k), 400, D)
            cells.append(f"{100 * score_binary(CappedCounter(k).fit(data).predict, data):.1f}%")
        print(f"| {k} | " + " | ".join(cells) + " |")
    print("\nReading: accuracy is exact once `k >= D+3` for the depth the strings actually reach, and")
    print("collapses below it -- 4 states cannot decide depth-8 brackets however long it trains,")
    print("because the information is gone by then.")
    print("\n**Correction, turn 7.** This text said `k >= D+1` for three parts. That is wrong at the")
    print("boundary: the grid below only samples k in {2,4,8,16}, so it never tested k = D+1 or D+2.")
    print("`audit_a1b.py` scans the boundary and measures the requirement as exactly **D+3** (5, 7,")
    print("11, 19 at D = 2, 4, 8, 16) -- the extra two states are what the single-bracket corruption")
    print("costs, not what the brackets cost. The property that survives is the one that matters: the")
    print("**baseline sits strictly below its ceiling** and the state budget, not the trainer, is what")
    print("the task charges for.")
    print("\nOne caveat, visible in the table: k=4 at D=2 is 97.0%, not 100%, even though 4 >= 2+1.")
    print("That cell is transition-key coverage -- the machine only learns the (state, character) pairs")
    print("its 400 strings visited -- not a state limit. Coverage is the same artefact `ceiling.py`")
    print("found in every earlier benchmark, which is why this table is the one that varies the budget.")

    # recurrent baseline. Reported as a distribution over restarts, because learning on these tasks
    # is bimodal: a run either finds the rule (exact) or stalls at chance. One run would have called
    # this baseline "82% or 48%" depending on luck, which is why turn 4 was right to withhold it.
    PAIRS = 8
    EPOCHS = 8
    train = make_balanced_set(random.Random(SEED + 7), 8000, PAIRS)
    test = make_balanced_set(random.Random(SEED + 11), 1600, PAIRS)
    deep = make_balanced_set(random.Random(SEED + 13), 800, 16)      # depth 16: beyond capacity?
    buckets = {2: [], 4: [], 8: []}
    for w, y in test:
        d = depth_of(w)
        b = 2 if d <= 2 else (4 if d <= 4 else 8)
        buckets[b].append((w, y))

    print("\n### A2. Recurrent baseline vs state budget (h units), 4 restarts per budget\n")
    print("Metric: exact accuracy of the median restart, the best restart, and the **success rate**")
    print("(fraction of restarts reaching >= 95%). A single restart is not a baseline here: learning")
    print("on this task is bimodal, exact or chance.\n")
    print("| system | params | all D<=8 | D<=2 | D=4 | D=8 | D=16 holdout | success | wall |")
    print("|---|---|---|---|---|---|---|---|---|")

    # 0-parameter nulls first (AMEND-002), including the shortcut that fooled turn 4's control task
    def null_always(w):
        return 1
    def null_lastchar(w):
        return 1 if w.endswith(")") else 0
    for label, fn in (("0-param: always valid", null_always),
                      ("0-param: ends with ')'", null_lastchar)):
        print(f"| {label} | **0** | {100 * score_binary(fn, test):.2f}% | "
              f"{100 * score_binary(fn, buckets[2]):.2f}% | {100 * score_binary(fn, buckets[4]):.2f}% | "
              f"{100 * score_binary(fn, buckets[8]):.2f}% | {100 * score_binary(fn, deep):.2f}% | -- | -- |")

    rnn_cache = {}
    best_overall = [None, -1.0]
    for hid in (2, 4, 8):
        t1 = time.time()
        accs, sub, deeps, models = [], [[], [], []], [], []
        for r in range(4):
            m = RNN(hid, random.Random(SEED + 100 * r))
            m.train(train, EPOCHS, random.Random(SEED + 1 + 100 * r))
            models.append(m)
            accs.append(score_binary(m.predict, test))
            for i, b in enumerate((2, 4, 8)):
                sub[i].append(score_binary(m.predict, buckets[b]))
            deeps.append(score_binary(m.predict, deep))
        dt = time.time() - t1
        med = sorted(accs)[len(accs) // 2]
        best_i = accs.index(max(accs))
        rnn_cache[hid] = models[best_i]
        if max(accs) > best_overall[1]:
            best_overall = [models[best_i], max(accs)]
        succ = sum(1 for a in accs if a >= 0.95) / len(accs)
        print(f"| h={hid} (median of 4) | {RNN(hid, random.Random(0)).nparams()} | {100 * med:.2f}% | "
              f"{' | '.join(f'{100 * sorted(s)[len(s) // 2]:.2f}%' for s in sub)} | "
              f"{100 * sorted(deeps)[len(deeps) // 2]:.2f}% | {succ:.0%} | {dt:.0f}s |")
        print(f"| _h={hid}, best of 4_ | | _{100 * max(accs):.2f}%_ | "
              f"{' | '.join(f'_{100 * max(s):.2f}%_' for s in sub)} | _{100 * max(deeps):.2f}%_ | | |")

    print("\nReading: the neural baseline **solves** the task it was blamed for failing. With Adam,")
    print("centered inputs, scaled init and clipping, 4 hidden units reach the ceiling on depth <= 8")
    print("where the turn-4 trainer sat at chance -- so the earlier null was optimisation, not state.")
    print("It also shows the limit: at depth 16 every budget is at chance even where the 16-state")
    print("counter is exact. **State budget is a real axis for neural models too, just a different")
    print("currency** (floats, not k). The 0-param `ends with ')'` row is there because that exact")
    print("shortcut produced a 73.50% control score three budgets in a row in turn 4.")

    print("\n### A2b. Data budget at h=4 (>= 3 budgets, >= 10x span, 2 restarts each)\n")
    print("| train strings | params | median | best | success | wall |")
    print("|---|---|---|---|---|---|")
    for n in (2000, 10000, 40000):
        t1 = time.time()
        big = make_balanced_set(random.Random(SEED + 7), n, PAIRS)
        accs = []
        for r in range(2):
            m = RNN(4, random.Random(SEED + 100 * r))
            m.train(big, EPOCHS, random.Random(SEED + 1 + 100 * r))
            accs.append(score_binary(m.predict, test))
        dt = time.time() - t1
        print(f"| {n:,} | {RNN(4, random.Random(0)).nparams()} | {100 * sorted(accs)[0]:.2f}% | "
              f"{100 * max(accs):.2f}% | {sum(1 for a in accs if a >= 0.95) / len(accs):.0%} | {dt:.0f}s |")

    print("\n### A2c. Control witness -- same code path, shortcut-free task (end at depth 0)\n")
    print("| hidden units h | params | median | best | success |")
    print("|---|---|---|---|---|")
    ctr = make_control_set(random.Random(SEED + 7), 8000, PAIRS)
    cte = make_control_set(random.Random(SEED + 11), 800, PAIRS)
    print(f"| *(0-param: ends with ')')* | **0** | *{100 * score_binary(null_lastchar, cte):.2f}%* | "
          f"| |")
    for hid in (4, 8):
        accs = []
        for r in range(3):
            m = RNN(hid, random.Random(SEED + 100 * r))
            m.train(ctr, EPOCHS, random.Random(SEED + 1 + 100 * r))
            accs.append(score_binary(m.predict, cte))
        print(f"| h={hid} | {RNN(hid, random.Random(0)).nparams()} | "
              f"{100 * sorted(accs)[1]:.2f}% | {100 * max(accs):.2f}% | "
              f"{sum(1 for a in accs if a >= 0.95) / len(accs):.0%} |")
    print("\nThe control's 0-param row is ~50%, not 75%: the shortcut is gone, so a model that scores")
    print("here is carrying the running count rather than reading the last character.")

    print("\n### A2d. Is the baseline carrying state? (bimodality, not degeneracy)\n")
    print("Turn 4's check flagged two budgets emitting identical predictions. That test is necessary")
    print("but not sufficient: two *failed* restarts also agree (both say 'chance'), so identity")
    print("alone cannot distinguish a dead recurrence from two unlucky seeds. The distinguishing")
    print("evidence is the distribution: a state-carrying model is exact on some restarts and a")
    print("capacity-limited one is capped at some ceiling. Both appear above -- success goes 0% ->")
    print("≥50% -> 100% across h=2..4..8 on D<=8 and collapses to 0% at D=16 -- which is what a")
    print("state budget looks like when it is measured instead of inferred.")

    # risk-coverage for the largest-budget RNN (AMEND-001 G8 shape)
    m = best_overall[0] if best_overall[0] is not None else rnn_cache[8]
    cc = []
    for w, y in test:
        conf, pred = m.confidence(w)
        cc.append((conf, pred == y))
    print("\n### A3. Thresholded risk-coverage, recurrent baseline -- PROVISIONAL, model withheld\n")
    print("| tau | coverage | risk | selective accuracy |")
    print("|---|---|---|---|")
    for t in (0.0, 0.6, 0.8, 0.9, 0.95, 0.99):
        ans = [ok for c, ok in cc if c >= t]
        cov = len(ans) / len(cc)
        risk = (sum(1 for ok in ans if not ok) / len(ans)) if ans else float("nan")
        print(f"| {t:.2f} | {100 * cov:.2f}% | "
              f"{'n/a' if risk != risk else f'{100 * risk:.2f}%'} | "
              f"{'n/a' if risk != risk else f'{100 * (1 - risk):.2f}%'} |")
    print("\nRisk falls to 0 only at ~11% coverage, and the model underneath is the degenerate one from")
    print("A2d, so this table is a measurement of an abstention rule, not evidence that a recurrent")
    print("baseline is calibrated. It is kept because G8 needs the shape on the record.")


# ===========================================================================  TASK B: E-EDIT
def task_b():
    print("\n## TASK B -- stream binding + single-fact edit (E-RECALL / E-EDIT / G7)\n")
    print("AMEND-003 opening line, Task B:")
    print("  Minimal automaton for this task: a full-history key->value store, i.e. a machine with")
    print("  n slots and a transition per binding -- finite, and exact.")
    print("  Gate it fails: **G4**, because reads scale O(n) with the store, and its bounded")
    print("  approximation fails **G7**: capping RAM at m slots collides keys and one edit then")
    print("  clobbers unrelated ones.")
    print("  A candidate must reach coverage m/n at fixed m -- the pigeonhole ceiling, not")
    print("  headroom -- with a blast radius no larger than this baseline's (<= the slot")
    print("  population), and must not lose exactness on the keys it does hold.\n")
    print("n key->value bindings, then queries, then ONE edit, then the same queries again.")
    print("Working RAM capped at m slots. G7 requires zero collateral damage on unrelated keys.\n")
    print("| stream n | RAM m | recall before | recall after | **edit collateral** "
          "(right -> wrong) | keys wrong after | slot population |")
    print("|---|---|---|---|---|---|---|")

    for n in (1000, 10000, 100000):
        rng = random.Random(SEED + n)
        keys = list(range(n))
        rng.shuffle(keys)
        vals = {k: rng.randrange(1000) for k in keys}
        edit_key = keys[0]
        new_val = (vals[edit_key] + 1) % 1000

        for m in (64, 1024, None):
            if m is None:
                store, label = dict(vals), "full store"
            else:
                # direct-address store: slot = key mod m. Collisions overwrite, which is how a
                # bounded lookup table loses coverage -- and how ONE edit can damage unrelated keys.
                store = {}
                for k in keys:
                    store[k % m] = vals[k]
                label = f"{m} (direct-address)"
            slot = (lambda k: k if m is None else k % m)

            def read(k, store=store, slot=slot):
                return store.get(slot(k))

            before = {k: read(k) for k in keys}
            recall_before = sum(1 for k in keys if before[k] == vals[k]) / n
            store[slot(edit_key)] = new_val
            after = {k: read(k) for k in keys}
            recall_after = sum(1 for k in keys
                               if after[k] == (new_val if k == edit_key else vals[k])) / n
            # COLLATERAL = keys that were CORRECT before the edit and are WRONG after it. The first
            # version of this table counted every key that was wrong after the edit, which is almost
            # entirely the write-time collision loss (934 of 999 at m=64) -- a number that does not
            # depend on the edit at all. Measured properly the blast radius is 0-3 keys.
            broke = sum(1 for k in keys if k != edit_key and before[k] == vals[k] and after[k] != vals[k])
            wrong_after = sum(1 for k in keys if after[k] != (new_val if k == edit_key else vals[k]))
            pop = (n if m is None else sum(1 for k in keys if slot(k) == slot(edit_key)))
            print(f"| {n:,} | {label} | {100 * recall_before:.2f}% | {100 * recall_after:.2f}% | "
                  f"**{broke}** | {wrong_after:,} of {n - 1:,} | {pop} keys |")

    print("\n| 0-param null (answer the single most frequent value, 0) | -- | 0.10% | -- | -- | -- | -- |")
    print("\nReading, corrected in turn 7: a bounded store answers a *fraction* of queries, and the")
    print("failure is **coverage**, not correctness -- the same trade `ceiling.py` found in D4, with a")
    print("stream length to vary. The edit's own damage is small and bounded by the slot population")
    print("(`ceil(n/m)` keys at most), because a direct-address store gives each key one slot.")
    print("")
    print("Two corrections to the turn-4 version of this table, both from `audit_harness.py`:")
    print("  1. the old `COLLATERAL` column counted every key wrong *after* the edit, which is almost")
    print("     entirely write-time collision loss (934 of 999 at m=64, n=1000) and does not depend on")
    print("     the edit at all. The measured blast radius of the edit is **0-3 keys**.")
    print("  2. recall is not exactly m/n: it is m/n plus chance agreement from a 1,000-value space.")
    print("")
    print("Consequence for G7: a **direct-address** store cannot exhibit interesting collateral, so it")
    print("cannot test the gate. A candidate must beat coverage m/n at equal m **with a blast radius")
    print("no larger than the baseline's**, and an instrument that wants to see real collateral needs a")
    print("store whose readouts are shared across keys (superposition, fingerprints), not one slot per")
    print("key. This file measures the baseline; it does not build the sharing store.")


def main():
    t0 = time.time()
    print("# Non-regular benchmark -- research/bench/nonregular.py")
    print(f"seed={SEED} python={sys.version.split()[0]} CPU-only stdlib")
    print()
    print("Instrument only: tasks whose required state grows with depth or stream length, plus the")
    print("baselines every candidate must be measured against. No primitive is proposed here.")

    task_a()
    task_b()

    print("\n## What this instrument makes falsifiable\n")
    print("1. On Task A, any fixed-state claim has a **depth at which it breaks**, measured, not")
    print("   argued. A candidate that survives at D=16 with k=4 states is either wrong or new.")
    print("2. On Task B, a bounded-RAM claim has a **recall-vs-n curve** and a **collateral count**,")
    print("   which is G7 in one line instead of a paragraph.")
    print("3. Both tables carry the 0-param null, at least three budgets, and the analytic ceiling,")
    print("   per D-020, so a later candidate cannot be scored without them.")
    print("\nThe digit-addition family could do none of these three things, which is why AMEND-002")
    print("retired it.")
    print(f"\n---- total wall clock {time.time() - t0:.1f}s on CPU ----")
    print("\nReproduce: python3 research/bench/nonregular.py")


if __name__ == "__main__":
    main()
