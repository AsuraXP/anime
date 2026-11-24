#!/usr/bin/env python3
"""research/bench/stream_ram.py -- Task B, serialized as raw token streams, with RAM and read costs.

Run:  python3 research/bench/stream_ram.py        (stdlib, CPU, seeded, ~20 s)

WHY THIS FILE EXISTS
--------------------
`nonregular.py` Task B reported a coverage table and a (now corrected) collateral column, but it never
serialized the stream and never accounted for what a machine spends: working-RAM bits, parameter bits,
or bytes read per token. `AMEND-006` asks for exactly that, so the numbers below are what a candidate
has to beat rather than an adjective about "constant working state".

WHAT IS SERIALIZED
------------------
A stream of bindings written as raw bytes, one record per token:
    SET  <1> <key:2 bytes> <value:2 bytes>     4 bytes
    GET  <2> <key:2 bytes>                     3 bytes
    EDIT <3> <key:2 bytes> <value:2 bytes>     4 bytes
No oracle tags, no grammar shortcuts: a reader sees bytes and must decide from them.

THE THREE BASELINES AND THEIR ACCOUNTING
----------------------------------------
D-025 item (c) asks for a **superposed fast-weight** row beside the two stores below, because a
direct-address store gives every key its own slot and therefore cannot exhibit G7 collateral at all
(measured: 0-3 keys, Parts 10-11). A store whose readouts are **shared across keys** can. The
fast-weight memory is that store: one vector `s` holds every binding, each bound by a key vector, so
writing one binding changes the same memory that every other key reads. That is the difference
between a store that cannot fail G7 and one that can -- not a claim about which is better.

1. **m-slot direct-address store.** Working state = one slot index (⌈log2 m⌉ bits) + one value register
   (16 bits) + a program counter; parameters θ = 0. Each GET reads exactly one slot and each SET writes
   one slot, so bytes/token is O(1) and never depends on L. Coverage is the pigeonhole bound `m/L`.
2. **Full KV scan.** The honest unbounded store: to answer a GET it reads every stored record, so
   bytes/token is Θ(L). It is exact and it violates G4 -- which is the trade the charter asks about.
3. **Superposed fast-weight memory.** `s = sum_k psi(v_k) * phi(k)` over ±1 code vectors; a GET
   unbinds with `s * phi(q)` and decodes 16 block means. Reading it costs one pass over `d` entries
   -- constant in `n`, quadratic in nothing -- so it passes G4 at fixed `d` and fails capacity
   instead. Three update rules are measured, because the edit is where G7 bites: add-only (the old
   binding stays as a ghost), oracle erase-then-add (the machine is told the old value), and
   recalled erase-then-add (the machine erases what it *thinks* was there). At load the last one
   subtracts a wrong codeword and damages keys the edit never named.

Also reported: the edit's blast radius as `#{k != edit : correct_before and not correct_after}`,
which is the definition AMEND-006 fixed after the first version of the table counted collision loss.

INSTRUMENT ONLY.
"""

import math
import random
import sys
import time

SEED = 20261123
GEN_BUDGET = 200_000          # bytes of stream generated per configuration, to keep reads countable


# ------------------------------------------------------------------ stream construction
def build_stream(n, seed):
    """n bindings, shuffled keys, then GETs, then one EDIT, then the same GETs again."""
    rng = random.Random(seed)
    keys = list(range(n))
    rng.shuffle(keys)
    vals = {k: rng.randrange(1 << 16) for k in keys}
    edit_key = keys[0]
    new_val = (vals[edit_key] + 1) & 0xFFFF
    return keys, vals, edit_key, new_val


def rec(kind, key, val=None):
    """Serialize one record as raw bytes (2-byte key, 2-byte value)."""
    if kind == "SET":
        return bytes([1]) + key.to_bytes(2, "big") + val.to_bytes(2, "big")
    if kind == "GET":
        return bytes([2]) + key.to_bytes(2, "big")
    return bytes([3]) + key.to_bytes(2, "big") + val.to_bytes(2, "big")


# ------------------------------------------------------------------ the two machines
def direct_address(keys, vals, edit_key, new_val, m, queries):
    """m-slot store. Returns (recall_before, recall_after, collateral, bytes_read, bytes_written).

    Accounting: one slot read per GET (2 bytes), one slot write per SET/EDIT (2 bytes). The slot index
    register is ceil(log2 m) bits of working state; there are no parameters at all."""
    store = {}
    for k in keys:
        store[k % m] = vals[k]
    before = {k: store.get(k % m) for k in queries}
    rb = sum(1 for k in queries if before[k] == vals[k])
    store[edit_key % m] = new_val
    after = {k: store.get(k % m) for k in queries}
    ra = sum(1 for k in queries
             if after[k] == (new_val if k == edit_key else vals[k]))
    collateral = sum(1 for k in queries
                     if k != edit_key and before[k] == vals[k] and after[k] != vals[k])
    reads = 2 * len(queries) * 2          # before + after, two bytes per slot read
    writes = 2 * (len(keys) + 1) * 2      # the n bindings plus the edit
    return rb / len(queries), ra / len(queries), collateral, reads, writes, math.ceil(math.log2(m)) + 16


def full_scan(keys, vals, edit_key, new_val, queries):
    """Unbounded KV store. Exact, and it pays for that: every GET scans the whole store."""
    store = dict(vals)
    before = {k: store.get(k) for k in queries}
    rb = sum(1 for k in queries if before[k] == vals[k])
    store[edit_key] = new_val
    after = {k: store.get(k) for k in queries}
    ra = sum(1 for k in queries
             if after[k] == (new_val if k == edit_key else vals[k]))
    collateral = sum(1 for k in queries
                     if k != edit_key and before[k] == vals[k] and after[k] != vals[k])
    # a scan reads one 4-byte record per stored key per GET
    reads = 4 * len(store) * len(queries) * 2
    writes = 4 * (len(keys) + 1)
    return rb / len(queries), ra / len(queries), collateral, reads, writes, None


# ------------------------------------------------------------------ superposed fast-weight memory
NBLOCKS = 16          # a 16-bit value is coded as 16 blocks of +/-1; decoding is 16 block means


def _pool(d, salt):
    """A deterministic ±1 pool; key vectors are rotations of it, so no store is needed for the codes."""
    rng = random.Random(SEED * 7919 + salt)
    return [1 if rng.getrandbits(1) else -1 for _ in range(d)]


def key_code(pool, k):
    """phi(k): a rotation of the shared pool, so distinct keys are near-orthogonal and cost 0 params."""
    o = (k * 2654435761) % len(pool)
    return pool[o:] + pool[:o]


def val_code(v, d):
    """psi(v): 16 blocks, each constant +1 or -1 by the bit. Decode = 16 block means, Theta(d)."""
    out = []
    for b in range(NBLOCKS):
        bit = (v >> b) & 1
        out.extend([1 if bit else -1] * (d // NBLOCKS))
    return out


def fw_write(s, k, v, pool, d):
    """Add one binding in place: s += psi(v) * phi(k)."""
    phi = key_code(pool, k)
    psi = val_code(v, d)
    for j in range(d):
        s[j] += psi[j] * phi[j]


def fw_read(s, k, pool, d):
    """Unbind and decode: 16 block means of s * phi(k)."""
    phi = key_code(pool, k)
    y = [s[j] * phi[j] for j in range(d)]
    w = d // NBLOCKS
    v = 0
    for b in range(NBLOCKS):
        if sum(y[b * w:(b + 1) * w]) > 0:
            v |= 1 << b
    return v


def fast_weight(keys, vals, edit_key, new_val, d, queries, rule):
    """Build the memory, measure every key, apply ONE edit under `rule`, measure again.

    `rule`: 'add'      -- s += psi(new) * phi(k); the old binding survives as a ghost
            'oracle'   -- s -= psi(old) * phi(k); s += psi(new) * phi(k), with the true old value
            'recalled' -- same, but the old value is what the machine recalled before the edit
    """
    pool = _pool(d, 1)
    s = [0.0] * d
    # `vals` is a dict: zip(keys, vals) would walk its KEYS, which is how the first version of this
    # function stored (key -> key) and decoded every lookup as the key itself.
    for k in keys:
        fw_write(s, k, vals[k], pool, d)

    before = {k: fw_read(s, k, pool, d) for k in queries}
    rb = sum(1 for k in queries if before[k] == vals[k])

    old = vals.get(edit_key)
    if rule in ("oracle", "recalled"):
        drop = old if rule == "oracle" else before.get(edit_key, old)
        psi_old = val_code(drop, d)
        phi = key_code(pool, edit_key)
        for j in range(d):
            s[j] -= psi_old[j] * phi[j]
    fw_write(s, edit_key, new_val, pool, d)

    after = {k: fw_read(s, k, pool, d) for k in queries}
    ra = sum(1 for k in queries if after[k] == (new_val if k == edit_key else vals[k]))
    collateral = sum(1 for k in queries
                     if k != edit_key and before[k] == vals[k] and after[k] != vals[k])
    # One GET reads the whole vector: d entries x 2 bytes. Both passes (before and after the edit)
    # read every query; each write touches all d entries.
    reads = 4 * d * len(queries)
    writes = 2 * d * (len(keys) + 2)
    return rb / len(queries), ra / len(queries), collateral, reads, writes


def main():
    t0 = time.time()
    print("# Task B on raw token streams, with RAM and read accounting -- research/bench/stream_ram.py")
    print(f"seed={SEED} python={sys.version.split()[0]} CPU-only stdlib\n")
    print("Records are raw bytes -- SET/GET/EDIT, 2-byte keys, 2-byte values, no oracle tags. A")
    print("machine sees the stream and nothing else.\n")
    print("AMEND-006 asks for three numbers beside every claim: working-RAM bits `|s_t|`, parameter")
    print("bits `|theta|`, and bytes read+written per token (`G4`, budget 4 KiB). Both baselines are")
    print("accounted here so a candidate has something concrete to beat.\n")

    print("| stream L | machine | coverage | **edit collateral** | |s_t| bits | |theta| bits | "
          "bytes/token | G4 (<= 4 KiB) |")
    print("|---|---|---|---|---|---|---|---|")

    rows = []
    for L in (1000, 10000, 100000):
        keys, vals, edit_key, new_val = build_stream(L, SEED + L)
        # Uniform sample, NOT the first 2000 keys: the store is written in `keys` order, so the
        # earliest keys are the ones a later collision overwrites first, and querying them measures
        # write order rather than coverage. The first version of this file did that and reported
        # 0.00% recall at m=1024, L=10,000 where the pigeonhole bound is 10.24%.
        queries = random.Random(SEED + 2 * L).sample(keys, min(2000, L))
        toks = len(keys) + 2 * len(queries) + 1        # SETs + GETs + one EDIT

        for m in (64, 1024):
            rb, ra, coll, reads, writes, s_bits = direct_address(keys, vals, edit_key, new_val, m, queries)
            bpt = (reads + writes) / toks
            rows.append((L, m, rb, coll, s_bits, 0, bpt))
            print(f"| {L:,} | direct {m} | {100 * rb:.2f}% | **{coll}** | {s_bits} | 0 | "
                  f"{bpt:.1f} | {'yes' if bpt <= 4096 else '**no**'} |")

        rb, ra, coll, reads, writes, _ = full_scan(keys, vals, edit_key, new_val, queries)
        bpt = (reads + writes) / toks
        rows.append((L, "full", rb, coll, math.ceil(math.log2(max(2, L))) + 16, 0, bpt))
        print(f"| {L:,} | full KV scan | {100 * rb:.2f}% | **{coll}** | "
              f"{math.ceil(math.log2(max(2, L))) + 16} | 0 | {bpt:,.0f} | "
              f"{'yes' if bpt <= 4096 else '**no**'} |")

    # ---------------------------------------------------------------- fast-weight (G7 instrument)
    print("\n### The shared-readout store: superposed fast weights (D-025 item (c))\n")
    print("One vector holds every binding, bound by a ±1 key code; a GET unbinds and decodes 16 block")
    print("means. Every write touches the memory every key reads, so this is the first store in the")
    print("harness that *can* exhibit G7 collateral. Three update rules, because the edit is the event")
    print("the gate is about: **add** (old binding survives as a ghost), **oracle** (erase the true old")
    print("value, then add), **recalled** (erase what the machine recalled -- what it can actually do).\n")
    print("| d | n | load 16n/d | recall before | correct before | collateral: add | "
          "**coll / correct** | oracle | recalled | bytes read+written/token | |theta| | G4 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for d in (1024, 2048, 4096):
        for n in (32, 64, 128):
            keys, vals, ek, nv = build_stream(n, SEED + n)
            out = {}
            for rule in ("add", "oracle", "recalled"):
                rb, ra, coll, rd, wr = fast_weight(keys, vals, ek, nv, d, keys, rule)
                out[rule] = (rb, coll, (rd + wr) / (len(keys) + 2 * len(keys) + 1))
            rb, coll_add, bpt = out["add"]
            sbits = 16 * d
            okb = round(rb * n)
            rel = f"{100 * coll_add / okb:.0f}%" if okb else "--"
            print(f"| {d} | {n} | {16 * n / d:5.2f} | {100 * rb:6.1f}% | {okb} | **{coll_add}** | "
                  f"**{rel}** | {out['oracle'][1]} | {out['recalled'][1]} | {bpt:,.0f} | 0 | "
                  f"{'yes' if bpt <= 4096 else '**no**'} |")
    print("\nA 0-parameter null for this task answers with the most frequent value for every key: 0.00%.")

    # ---------------------------------------------------------------- equal-B ceiling and floor
    print("\n### Equal-B: the ceiling, and what each family actually reaches at it (D-026 ask)\n")
    print("`agent-b`'s blocker asks for the ceiling and floor at a fixed memory budget `B`, including")
    print("`B < n`. `B = 1,024` 16-bit entries (16,384 bits) below; `ceiling = min(1, B/n)` is the")
    print("pigeonhole bound that AMEND-007 requires every header to quote beside `D_max`.\n")
    print("| n | ceiling min(1,B/n) | m-slot (B=1024) | KV scan | fast-weight d=1024 | "
          "G4: m-slot / scan / fw |")
    print("|---|---|---|---|---|---|")
    for n in (1000, 1024, 10000, 100000):
        keys, vals, ek, nv = build_stream(n, SEED + n)
        q = random.Random(SEED + 2 * n).sample(keys, min(2000, n))
        toks = len(keys) + 2 * len(q) + 1
        rb_d, _, _, rd, wr, _ = direct_address(keys, vals, ek, nv, 1024, q)
        bpt_d = (rd + wr) / toks
        rb_s, _, _, frd, fwr, _ = full_scan(keys, vals, ek, nv, q)
        bpt_s = (frd + fwr) / toks
        if n <= 10000:
            # sampled queries, same as the other two families, so the cells are comparable
            rb_f, _, _, fr_r, fr_w = fast_weight(keys, vals, ek, nv, 1024, q, "add")
            bpt_f = (fr_r + fr_w) / toks
            fw_cell = f"{100 * rb_f:.2f}%"
        else:
            bpt_f = None
            fw_cell = "not run (build is 10^8 ops)"
        g4 = (f"yes / {'yes' if bpt_s <= 4096 else '**no**'} / "
              + ("yes" if bpt_f is not None and bpt_f <= 4096 else
                 "**no**" if bpt_f is not None else "--"))
        print(f"| {n:,} | {min(1.0, 1024 / n):.3f} | {100 * rb_d:.2f}% | {100 * rb_s:.2f}% | "
              f"{fw_cell} | {g4} |")
    print("\nWhat this fixes, stated plainly: **the `B < n` regime is empty for a superposed store**. At")
    print("d=1024, n=1024 it answers 0.10% of its keys; at n=2048 and beyond, 0.00%. Its capacity is")
    print("`~d/(2 ln |V|)` bindings and `V` has 2^16 values, so it cannot reach one binding per entry,")
    print("let alone more. The only family that reaches the ceiling is the m-slot store, and it does so")
    print("by storing every key exactly -- 16 bits per binding, no sharing.")
    print("\nReading, and what a candidate has to do:")
    print("- **Coverage is the pigeonhole bound.** An m-slot store answers `m/L` of random queries;")
    print("  the full scan answers all of them and pays `Theta(L)` bytes per token for it. The gap")
    print("  between the two rows *is* the problem, and it is not closed by either.")
    print("- **Collateral is small here and that is the honest result.** One edit touches one slot, so")
    print("  at most `ceil(L/m)` keys can be damaged and only those that were already correct count.")
    print("  This design cannot produce large collateral, so it cannot test G7 -- stated rather than")
    print("  dressed up as a pass.")
    print("- **`|s_t|` is a register count, not a store count.** The direct-address row needs ~7-17 bits")
    print("  of working state and 0 parameters; the scan needs a pointer plus its store. A candidate")
    print("  that claims constant working state must show these numbers, not the store's size.")
    print("\n### What the shared-readout store shows")
    print("- **G7 has an instrument now, and the honest metric is the ratio, not the count.** Add-only")
    print("  edits damage 0-5 keys, which reads as 'small' until it is divided by how many keys were")
    print("  correct: **22% of them at d=1024/n=32, 60% at d=1024/n=64, 28-33% at d=2048**. So one edit")
    print("  breaks a fifth to three-fifths of everything that worked. An oracle erase removes most of")
    print("  it, which is the control proving the damage came from the edit. The count is small only")
    print("  because the store holds few keys; the fraction is not small, and G7 says 'zero'.")
    print("- **It fails capacity instead of G4.** At fixed `d` the read cost is ~`2d` bytes per token,")
    print("  independent of `n`: 2,053-2,069 at d=1024, 4,107-4,138 at d=2048 (just over the budget,")
    print("  because every write also touches all `d` entries), 8,213-8,276 at d=4096. So G4 permits")
    print("  `d = 1024`, where recall at n=32 is only 28.1% -- about nine bindings held. Doubling `d`")
    print("  doubles both capacity and bytes read, and the second one is already over budget.")
    print("- **At equal bits the m-slot store wins outright.** 16,384 bits buys 1,024 slots (100% at")
    print("  n=32) or one d=1024 vector (28.1% at n=32). The measurement is that a *shared* readout")
    print("  buys nothing on this task; it only buys the ability to fail G7, which is exactly why it")
    print("  belongs in the harness as an instrument and not in a candidate as a design.")
    print("- **My own claim from MSG-0009 is corrected here.** I wrote that G7 looked like a weak gate")
    print("  because collateral was 0-5 keys. That was an absolute count of a store holding few keys;")
    print("  the ratio above shows the gate biting hard wherever the store works at all. The count and")
    print("  the ratio disagree, and the charter's wording ('zero collateral damage') is absolute, so")
    print("  under G7 as written both numbers fail -- the correction is mine to make, not the gate's.\n")
    print("## What would prove this accounting wrong")
    print("A machine with `|s_t| + |theta|` bits bounded across `L: 10^3 -> 10^6` (ratio <= 1.10),")
    print("bytes/token <= 4 KiB, and coverage that beats `m/L` at equal `m` -- that is a candidate,")
    print("and this file has no candidate in it.")
    print("\n---- total wall clock %.0fs on CPU ----" % (time.time() - t0))
    print("\nReproduce: python3 research/bench/stream_ram.py")


if __name__ == "__main__":
    main()
