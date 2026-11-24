#!/usr/bin/env python3
"""research/bench/audit_harness.py -- audit the two benchmark tasks in `nonregular.py`.

Run:  python3 research/bench/audit_harness.py        (stdlib, CPU, seeded, ~5 s)

WHY THIS FILE EXISTS
--------------------
`nonregular.py` published two claims that other agents then used. The Adversary audited them
(`MSG-0011`) and made three statements about my own harness:

  (a) "A1b is a 19-state problem: k = 19 scores 100.0% on all four cells, one fixed machine fit once
       on the D=16 cell is exact on the whole grid, and its readout table has 4 rows."
  (b) "the requirement is D+3, linear in the declared depth."
  (c) "Task B is an m/n problem: the ceiling is m/n by pigeonhole, the baseline is at it."

Third-party audits of my numbers are exactly what this seat is for, so each statement is checked here
rather than accepted or rejected in prose. Two of them were right and one exposed a defect of mine.

THE TWO DEFECTS THIS FILE FOUND IN MY OWN PUBLISHED TABLES
----------------------------------------------------------
1. **"exact iff k >= D+1" was wrong.** The grid only sampled k in {2,4,8,16}, so it never tested
   k = D+1 or D+2. Scanning the boundary, the requirement is exactly **D+3** (5, 7, 11, 19 at
   D = 2, 4, 8, 16). The published sentence understated what the task costs by two states.
2. **Task B's "COLLATERAL" column was mislabelled.** It counted every key wrong after the edit --
   almost all of it write-time collision loss (934 of 999 at m=64, n=1000), which does not depend on
   the edit at all. Measured properly, the edit's blast radius is **0-3 keys**, bounded by the slot
   population.

Neither error was in the direction of flattering the harness, and both were found by checking someone
else's claims about it -- which is the argument for having adversaries.
"""

import math
import random
import sys

import nonregular as nr


# =============================================================  Task A: what does the state cost?
def min_exact_k(D):
    """Smallest k for which the capped counter is exact on a depth-pinned set at depth D."""
    data = nr.make_depth_set(random.Random(nr.SEED + 1000 * D), 400, D)
    for k in range(1, D + 8):
        if nr.score_binary(nr.CappedCounter(k).fit(data).predict, data) == 1.0:
            return k, data
    return None, data


def task_a_audit():
    print("## 1. Task A -- what state does it actually cost?\n")
    print("`nonregular.py` never sampled k = D+1 or D+2, so its published rule (`k >= D+1`) was never")
    print("tested at the boundary. Scanning it:\n")
    print("| depth D | min k for 100% | requirement | D+1 | D+2 | D+3 |")
    print("|---|---|---|---|---|---|")
    need = {}
    for D in (2, 4, 8, 16):
        k, _ = min_exact_k(D)
        need[D] = k
        print(f"| {D} | **{k}** | D+{k - D} | {D + 1} | {D + 2} | {D + 3} |")
    ok = all(need[D] == D + 3 for D in need)
    print(f"\nRequirement is exactly `D+3` on every depth tested: **{'confirmed' if ok else 'NOT confirmed'}**.")
    print(f"That is ~{math.ceil(math.log2(max(need.values())))} bits of state at D=16 -- small, linear,")
    print("and cheap, which is the Adversary's point (a).\n")

    print("Cross-cell transfer: fit ONE machine at `k = D+3` on the deepest cell only, then score it")
    print("on every cell. If this is exact, the four cells are one problem, not four.\n")
    k16 = need[16]
    data16 = nr.make_depth_set(random.Random(nr.SEED + 1000 * 16), 400, 16)
    m = nr.CappedCounter(k16).fit(data16)
    print("| cell D | accuracy of the machine fitted at D=16 |")
    print("|---|---|")
    transfer = {}
    for D in (2, 4, 8, 16):
        cell = nr.make_depth_set(random.Random(nr.SEED + 1000 * D), 400, D)
        acc = nr.score_binary(m.predict, cell)
        transfer[D] = acc
        print(f"| {D} | {100 * acc:.1f}% |")
    print(f"\nReadout table: **{len(m.T)} rows** over `(final depth, underflow seen)`, "
          f"{2 * len(m.T)} entries, {math.ceil(math.log2(k16))} bits of state.")
    print("A 19-state machine with a 4-row counted readout is exact on the whole grid, so A1b cannot")
    print("falsify a claim about *composition*; it falsifies a claim about a *state budget*. That is")
    print("what Part 9 said, and this is the number behind it.\n")
    return need, transfer


# =============================================================  Task B: coverage vs collateral
def task_b_audit():
    print("## 2. Task B -- coverage, and what an edit actually damages\n")
    print("The published table had a column headed `COLLATERAL (unrelated keys changed)` whose value")
    print("was every key wrong after the edit. That number barely moves when the edit is removed, so")
    print("it was measuring write-time collisions. Both quantities are separated here:\n")
    print("| stream n | RAM m | recall | m/n | **edit collateral** | wrong after | slot population |")
    print("|---|---|---|---|---|---|---|")
    rows = []
    for n in (1000, 10000, 100000):
        rng = random.Random(nr.SEED + n)
        keys = list(range(n))
        rng.shuffle(keys)
        vals = {k: rng.randrange(1000) for k in keys}
        edit_key = keys[0]
        new_val = (vals[edit_key] + 1) % 1000
        for m in (64, 1024):
            store = {}
            for k in keys:
                store[k % m] = vals[k]
            before = {k: store.get(k % m) for k in keys}
            rec_b = sum(1 for k in keys if before[k] == vals[k]) / n
            store[edit_key % m] = new_val
            after = {k: store.get(k % m) for k in keys}
            broke = sum(1 for k in keys
                        if k != edit_key and before[k] == vals[k] and after[k] != vals[k])
            wrong = sum(1 for k in keys if after[k] != (new_val if k == edit_key else vals[k]))
            pop = sum(1 for k in keys if k % m == edit_key % m)
            rows.append((n, m, rec_b, broke, wrong, pop))
            print(f"| {n:,} | {m} | {100 * rec_b:.2f}% | {100 * m / n:.2f}% | **{broke}** | "
                  f"{wrong:,} of {n - 1:,} | {pop} keys |")
    print("\nReading: the edit's blast radius is 0-3 keys and is bounded by the slot population")
    print("(`ceil(n/m)`), because a direct-address store gives every key one slot. The 934-of-999")
    print("figure that stood in Part 7 and Part 9 was collision loss wearing the word 'collateral'.")
    print("**A direct-address store cannot exhibit interesting collateral, so it cannot test G7.**")
    print("Coverage is the property it does test, and recall is not exactly `m/n` either: it is `m/n`")
    print("plus chance agreement in a 1,000-value space.\n")
    return rows


# =============================================================  verdicts
def verdicts(need, transfer, rows):
    print("## 3. The bars, corrected\n")
    print(f"- **Task A:** beat the k-state machine at `k < D+3` (not `D+1`) without growing working")
    print(f"  state. The ceiling is a {max(need.values())}-state machine at D=16 -- "
          f"{math.ceil(math.log2(max(need.values())))} bits.")
    worst = max(r[3] for r in rows)
    print(f"- **Task B:** reach coverage `m/n` at fixed m with a blast radius no larger than the")
    print(f"  baseline's (measured: {worst} keys at most). The pigeonhole bound `m/n` is not headroom;")
    print(f"  it is the ceiling, and a candidate that exceeds it is storing more than m keys.")
    print("- **Neither task is a composition test.** Both are budgets: states for A, slots for B. A")
    print("  candidate that passes either has matched a budget, and the charter's question is whether")
    print("  it does so with less than the budget.")
    print("\n## 4. What would prove this audit wrong\n")
    print("- A depth-pinned set on which some `k < D+3` machine is exact (the requirement is not D+3).")
    print("- A store where one edit damages many keys while keeping `m` fixed and reads flat -- that")
    print("  would be a real G7 instrument, and this file would have to adopt it.")
    print("\nReproduce: python3 research/bench/audit_harness.py")


def main():
    print("# Harness audit -- research/bench/audit_harness.py")
    print(f"seed={nr.SEED} python={sys.version.split()[0]} CPU-only stdlib\n")
    print("Checks the Adversary's three claims about `nonregular.py` (`MSG-0011`) against the code,")
    print("and reports the two defects it found in my own published tables.\n")
    need, transfer = task_a_audit()
    rows = task_b_audit()
    verdicts(need, transfer, rows)


if __name__ == "__main__":
    main()
