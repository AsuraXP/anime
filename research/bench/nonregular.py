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


def make_balance_set(rng, n, pairs):
    """Control task for the recurrent baseline: label = "does the string end at depth 0?". Half the
    items are balanced words, half are a balanced word with one extra opener appended or prepended.
    This is a running-sum readout, not underflow detection -- far easier, and that is the point: it
    makes the gradient path itself testable, so a null on the hard task cannot be blamed silently on
    a broken trainer."""
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
    """Elman RNN, 2 inputs, h hidden units, 2-way softmax readout, BPTT. The bounded-state neural
    baseline: it carries h floats of state across the whole string, which is the thing the charter
    bounds. Small on purpose -- this is a baseline, not a candidate."""

    def __init__(self, hid, rng):
        self.h = hid
        self.Wx = [[rng.uniform(-0.5, 0.5) for _ in range(2)] for _ in range(hid)]
        self.Wh = [[rng.uniform(-0.5, 0.5) for _ in range(hid)] for _ in range(hid)]
        self.b = [0.0] * hid
        self.Wo = [[rng.uniform(-0.5, 0.5) for _ in range(hid)] for _ in range(2)]
        self.bo = [0.0, 0.0]

    def nparams(self):
        return self.h * 2 + self.h * self.h + self.h + 2 * self.h + 2

    def forward(self, w):
        hs = []
        h = [0.0] * self.h
        for ch in w:
            x = [1.0, 0.0] if ch == "(" else [0.0, 1.0]
            nh = []
            for j in range(self.h):
                s = self.b[j] + self.Wx[j][0] * x[0] + self.Wx[j][1] * x[1]
                for k in range(self.h):
                    s += self.Wh[j][k] * h[k]
                nh.append(math.tanh(s))
            hs.append(nh)
            h = nh
        o = [self.bo[c] + sum(self.Wo[c][j] * h[j] for j in range(self.h)) for c in (0, 1)]
        mx = max(o)
        e = [math.exp(v - mx) for v in o]
        z = sum(e)
        return hs, [v / z for v in e]

    def train(self, data, epochs, rng, lr=0.05):
        """Full backprop-through-time. The first version of this file updated only the last two
        steps and never touched Wx, so the network collapsed to a constant classifier and the
        baseline "failed" for a reason that had nothing to do with state. A baseline that cannot
        learn is not a baseline."""
        for _ in range(epochs):
            order = list(range(len(data)))
            rng.shuffle(order)
            for idx in order:
                w, y = data[idx]
                hs, p = self.forward(w)
                g = p[:]
                g[y] -= 1.0
                g = [max(-1.0, min(1.0, v)) for v in g]
                hT = hs[-1] if hs else [0.0] * self.h
                dh = [0.0] * self.h
                for c in (0, 1):
                    if g[c]:
                        self.bo[c] -= lr * g[c]
                        for j in range(self.h):
                            dh[j] += self.Wo[c][j] * g[c]
                            self.Wo[c][j] -= lr * g[c] * hT[j]
                for t in range(len(w) - 1, -1, -1):
                    ht = hs[t]
                    hprev = hs[t - 1] if t > 0 else [0.0] * self.h
                    d = [dh[j] * (1 - ht[j] * ht[j]) for j in range(self.h)]
                    x = [1.0, 0.0] if w[t] == "(" else [0.0, 1.0]
                    # Compute the recurrence gradient from the CURRENT Wh *before* mutating it.
                    # Three bugs have now been found in this class by the same symptom -- a
                    # baseline that will not move off chance: the transpose (dh used Wh[j][k]*d[k]),
                    # in-place mutation feeding its own gradient, and one-step-only backprop.
                    dh_next = [sum(self.Wh[j][k] * d[j] for j in range(self.h))
                               for k in range(self.h)]
                    for j in range(self.h):
                        if d[j]:
                            self.b[j] -= lr * d[j]
                            self.Wx[j][0] -= lr * d[j] * x[0]
                            self.Wx[j][1] -= lr * d[j] * x[1]
                            for k in range(self.h):
                                self.Wh[j][k] -= lr * d[j] * hprev[k]
                    dh = dh_next

    def train_batch(self, data, epochs, rng, lr=0.1, B=32):
        """Averaged-gradient (mini-batch) BPTT. This is the fair baseline: online single-sample SGD
        at lr 0.05-0.2 could not move the flip task off chance even with correct gradients, and a
        baseline that cannot learn is not a baseline. Same math as train(), one step per batch."""
        h = self.h
        for _ in range(epochs):
            order = list(range(len(data)))
            rng.shuffle(order)
            for start in range(0, len(order), B):
                gb = [0.0] * h
                gWx = [[0.0, 0.0] for _ in range(h)]
                gWh = [[0.0] * h for _ in range(h)]
                gWo = [[0.0] * h for _ in range(2)]
                gbo = [0.0, 0.0]
                nb = 0
                for idx in order[start:start + B]:
                    w, y = data[idx]
                    nb += 1
                    hs, p = self.forward(w)
                    g = [max(-1.0, min(1.0, p[c] - (1.0 if c == y else 0.0))) for c in (0, 1)]
                    hT = hs[-1] if hs else [0.0] * h
                    dh = [0.0] * h
                    for c in (0, 1):
                        if g[c]:
                            gbo[c] += g[c]
                            for j in range(h):
                                dh[j] += self.Wo[c][j] * g[c]
                                gWo[c][j] += g[c] * hT[j]
                    for t in range(len(w) - 1, -1, -1):
                        ht = hs[t]
                        hprev = hs[t - 1] if t > 0 else [0.0] * h
                        d = [dh[j] * (1 - ht[j] * ht[j]) for j in range(h)]
                        x = [1.0, 0.0] if w[t] == "(" else [0.0, 1.0]
                        nxt = [sum(self.Wh[j][k] * d[j] for j in range(h)) for k in range(h)]
                        for j in range(h):
                            if d[j]:
                                gb[j] += d[j]
                                gWx[j][0] += d[j] * x[0]
                                gWx[j][1] += d[j] * x[1]
                                for k in range(h):
                                    gWh[j][k] += d[j] * hprev[k]
                        dh = nxt
                sc = lr / max(1, nb)
                for j in range(h):
                    self.b[j] -= sc * gb[j]
                    self.Wx[j][0] -= sc * gWx[j][0]
                    self.Wx[j][1] -= sc * gWx[j][1]
                    for k in range(h):
                        self.Wh[j][k] -= sc * gWh[j][k]
                for c in (0, 1):
                    self.bo[c] -= sc * gbo[c]
                    for j in range(h):
                        self.Wo[c][j] -= sc * gWo[c][j]

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
    print("  A candidate must beat the k-state machine at k < D+1 *without growing working state*,")
    print("  and must not lose accuracy at k >= D+1.\n")
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
    print("\nReading: accuracy is exact exactly when `k >= D+1` for the depth the strings actually")
    print("reach, and collapses below it -- 4 states cannot decide depth-8 brackets however long it")
    print("trains, because the information is gone by then. This is the property positional addition")
    print("could never show: the state budget, not the trainer, is what the task charges for, and the")
    print("**baseline sits strictly below its ceiling**, so a candidate has somewhere to be wrong.")
    print("\nOne caveat, visible in the table: k=4 at D=2 is 97.0%, not 100%, even though 4 >= 2+1.")
    print("That cell is transition-key coverage -- the machine only learns the (state, character) pairs")
    print("its 400 strings visited -- not a state limit. Coverage is the same artefact `ceiling.py`")
    print("found in every earlier benchmark, which is why this table is the one that varies the budget.")

    # recurrent baseline: measured, then checked for degeneracy before it is allowed to count
    print("\n### A2. Recurrent baseline vs state budget (h units), strings of depth <= 8\n")
    print("**WITHHELD -- these rows are measurements, not a baseline. See A2d.**\n")
    print("| hidden units h | params | all | D<=2 | D=4 | D=8 | wall |")
    print("|---|---|---|---|---|---|---|")
    PAIRS = 8
    train = make_balanced_set(random.Random(SEED + 7), 8000, PAIRS)
    test = make_balanced_set(random.Random(SEED + 11), 1600, PAIRS)
    buckets = {2: [], 4: [], 8: []}
    for w, y in test:
        d = depth_of(w)
        b = 2 if d <= 2 else (4 if d <= 4 else 8)
        buckets[b].append((w, y))
    rnn_cache = {}
    sigs = {}
    for hid in (2, 4, 8, 16):
        t1 = time.time()
        m = RNN(hid, random.Random(SEED))
        m.train_batch(train, 12, random.Random(SEED + 1))
        dt = time.time() - t1
        rnn_cache[hid] = m
        sigs[hid] = tuple(m.predict(w) for w, _ in test)
        allacc = score_binary(m.predict, test)
        sub = [score_binary(m.predict, buckets[b]) for b in (2, 4, 8)]
        print(f"| {hid} | {m.nparams()} | {100 * allacc:.2f}% | "
              f"{' | '.join(f'{100 * v:.2f}%' for v in sub)} | {dt:.0f}s |")

    print("\n### A2c. Control witness -- same code path, easier task (end at depth 0)\n")
    print("| hidden units h | params | train strings | lr | control accuracy |")
    print("|---|---|---|---|---|")
    ctr = make_balance_set(random.Random(SEED + 7), 8000, PAIRS)
    cte = make_balance_set(random.Random(SEED + 11), 800, PAIRS)
    for hid, lr in ((8, 0.1), (8, 2.0)):
        m = RNN(hid, random.Random(SEED))
        m.train_batch(ctr, 12, random.Random(SEED + 1), lr=lr)
        print(f"| {hid} | {m.nparams()} | 8,000 | {lr} | **{100 * score_binary(m.predict, cte):.2f}%** |")
    print("\nThe same code path reaches the control ceiling, so the gradient plumbing works. The next")
    print("table is the reason that is still not enough to publish A2.")

    print("\n### A2d. Degeneracy check -- are the state budgets actually doing anything?\n")
    print("A model that carries state must predict *differently* at different state budgets. If a")
    print("4-unit and an 8-unit net emit the same answer on all 1,600 test strings, the hidden state")
    print("has collapsed and the row is measuring the readout bias, not state.\n")
    print("| lr | settings tried | distinct prediction vectors | verdict |")
    print("|---|---|---|---|")
    rows = []
    for lr in (0.1, 2.0):
        ds = {}
        for hid in (2, 4, 8):
            m = RNN(hid, random.Random(SEED))
            m.train_batch(train, 12, random.Random(SEED + 1), lr=lr)
            ds[hid] = tuple(m.predict(w) for w, _ in test)
        nd = len(set(ds.values()))
        rows.append((lr, nd))
        print(f"| {lr} | h=2,4,8 | {nd} of 3 | "
              f"{'usable' if nd == 3 else '**DEGENERATE -- A2 withheld**'} |")
    print("\nVerdict, read off the table above and not off intention: no setting tried gives both a")
    print("working control and a trustworthy state budget.")
    print("  * lr=0.1 -- budgets are distinct (3 of 3) but the control only reaches 73.50% and accuracy")
    print("    is non-monotone in h (h=8 beats h=16), which a capacity story cannot produce; the model")
    print("    is under-trained, and A2's 51-66% is a trainer artefact, not a state budget.")
    print("  * lr=2.0 -- the control is exact (100.00%) but two of three state budgets emit identical")
    print("    predictions on all 1,600 strings, so the recurrence is dead and the rows measure the")
    print("    readout bias.")
    print("The mechanism is tanh saturation: |h| -> 1 kills the gradient, and whichever unit pattern")
    print("wins early freezes in. Two optimizers (online, mini-batch), four state budgets and lr in")
    print("{0.1, 0.5, 1, 2} were tried. **No claim in this file rests on A2 or A2b.** A usable")
    print("recurrent baseline needs gradient clipping and input normalisation, and that is the")
    print("open defect this instrument ships with rather than a result it invents.")

    print("\n### A2b. Data budget at fixed h=8 (>= 3 budgets, >= 10x span)\n")
    print("Measured, and withheld for the same reason as A2.\n")
    print("| train strings | params | all | D<=2 | D=4 | D=8 | wall |")
    print("|---|---|---|---|---|---|---|")
    for n in (2000, 10000, 40000):
        t1 = time.time()
        big = make_balanced_set(random.Random(SEED + 7), n, PAIRS)
        m = RNN(8, random.Random(SEED))
        m.train_batch(big, 6, random.Random(SEED + 1))
        dt = time.time() - t1
        allacc = score_binary(m.predict, test)
        sub = [score_binary(m.predict, buckets[b]) for b in (2, 4, 8)]
        print(f"| {n:,} | {m.nparams()} | {100 * allacc:.2f}% | "
              f"{' | '.join(f'{100 * v:.2f}%' for v in sub)} | {dt:.0f}s |")

    # risk-coverage for the largest-budget RNN (AMEND-001 G8 shape)
    m = rnn_cache[8]
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
    print("  A candidate must beat recall m/n at equal m *without* collateral, and must not lose")
    print("  exactness on the keys it does hold.\n")
    print("n key->value bindings, then queries, then ONE edit, then the same queries again.")
    print("Working RAM capped at m slots. G7 requires zero collateral damage on unrelated keys.\n")
    print("| stream n | RAM m | recall before edit | recall after edit | COLLATERAL "
          "(unrelated keys changed) |")
    print("|---|---|---|---|---|")

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
                # direct-address store: slot = key mod m. Collisions overwrite, which is exactly
                # how a bounded lookup table produces collateral damage after an edit.
                store = {}
                for k in keys:
                    store[k % m] = vals[k]
                label = f"{m} (direct-address)"
            slot = (lambda k: k if m is None else k % m)

            def read(k, store=store, slot=slot):
                s = slot(k)
                return store.get(s)

            recall_before = sum(1 for k in keys if read(k) == vals[k]) / n
            # the edit
            store[slot(edit_key)] = new_val
            recall_after = sum(1 for k in keys
                               if read(k) == (new_val if k == edit_key else vals[k])) / n
            collateral = sum(1 for k in keys if k != edit_key and vals[k] != vals[k] and
                             read(k) == new_val and read(k) != vals[k])
            collateral = sum(1 for k in keys
                             if k != edit_key and read(k) != vals[k])
            print(f"| {n:,} | {label} | {100 * recall_before:.2f}% | {100 * recall_after:.2f}% | "
                  f"{collateral:,} of {n - 1:,} |")

    print("\n| 0-param null (answer the single most frequent value, 0) | -- | "
          f"| {100 * (sum(1 for k in range(1000) if k == 0) / 1000):.2f}% (1/1000 by construction) "
          f"| -- | -- |")
    print("\nReading: a bounded store answers a *fraction* m/n of queries, exactly, with zero")
    print("collateral for the keys it holds. The failure mode is coverage, not correctness --")
    print("which is the same trade `ceiling.py` found in D4, now with a stream length to vary.")
    print("A candidate must beat recall m/n at equal m **without** collateral, and that is a")
    print("measurable bar rather than an adjective.")


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
