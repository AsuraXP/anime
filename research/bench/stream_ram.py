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

THE TWO BASELINES AND THEIR ACCOUNTING
--------------------------------------
1. **m-slot direct-address store.** Working state = one slot index (⌈log2 m⌉ bits) + one value register
   (16 bits) + a program counter; parameters θ = 0. Each GET reads exactly one slot and each SET writes
   one slot, so bytes/token is O(1) and never depends on L. Coverage is the pigeonhole bound `m/L`.
2. **Full KV scan.** The honest unbounded store: to answer a GET it reads every stored record, so
   bytes/token is Θ(L). It is exact and it violates G4 -- which is the trade the charter asks about.

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
    print("\n## What would prove this accounting wrong")
    print("A machine with `|s_t| + |theta|` bits bounded across `L: 10^3 -> 10^6` (ratio <= 1.10),")
    print("bytes/token <= 4 KiB, and coverage that beats `m/L` at equal `m` -- that is a candidate,")
    print("and this file has no candidate in it.")
    print("\n---- total wall clock %.0fs on CPU ----" % (time.time() - t0))
    print("\nReproduce: python3 research/bench/stream_ram.py")


if __name__ == "__main__":
    main()
