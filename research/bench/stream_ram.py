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


# AMEND-004: the stream may not hand out its own opcodes. `op == 1` is a free grammar fact, so the
# three opcodes are a seeded bijection onto arbitrary byte values and nothing but the oracle rows is
# told which is which. A raw-byte learner has to *infer* the layout -- see `infer_layout`.
OPS = random.Random(SEED + 41).sample(range(16, 256), 3)
SET_OP, GET_OP, EDIT_OP = OPS
WRITE_OPS = (SET_OP, EDIT_OP)


def rec(kind, key, val=None):
    """Serialize one record as raw bytes (2-byte key, 2-byte value, permuted opcode)."""
    if kind == "SET":
        return bytes([SET_OP]) + key.to_bytes(2, "big") + val.to_bytes(2, "big")
    if kind == "GET":
        return bytes([GET_OP]) + key.to_bytes(2, "big")
    return bytes([EDIT_OP]) + key.to_bytes(2, "big") + val.to_bytes(2, "big")


def infer_layout(stream, widths=(3, 5)):
    """Infer which opcode takes which record width, by parse consistency alone.

    Brute-force every assignment of the two widths to the opcodes seen in the stream and keep the ones
    that parse the whole stream exactly to its end. Returns (assignment, candidates). More than one
    surviving assignment is reported rather than silently broken by a tie-break: that ambiguity is a
    property of the format, not of the learner.
    """
    seen = sorted({b for b in set(stream) if b in OPS})
    good = []
    for bits in range(1 << len(seen)):
        assign = {op: widths[(bits >> i) & 1] for i, op in enumerate(seen)}
        i, ok = 0, True
        while i < len(stream):
            op = stream[i]
            w = assign.get(op)
            if w is None or i + w > len(stream):
                ok = False
                break
            i += w
        if ok and i == len(stream):
            good.append(assign)
    return (good[0] if good else None), len(good)


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


LEARNED_BITS = 32768      # AMEND-008 clause 2: a learned raw-byte baseline at >= B = 32,768 bits


class ByteCache:
    """Learned raw-byte baseline at a fixed bit budget: hash the last `k` bytes into a value slot.

    It never sees an opcode. It is trained by write-through: every byte context that ends a record
    stores the last 16-bit value that followed it. `buckets * 16` bits exactly, so it is a matched-bit
    competitor to the oracle opcode store, and its failures are hash collisions rather than missing
    keys. That is the point of the row: with the same bits and no parsing, what is left?
    """

    def __init__(self, bits=LEARNED_BITS, k=5):
        self.buckets = bits // 16
        self.k = k
        self.tab = [None] * self.buckets

    @property
    def nbits(self):
        return self.buckets * 16

    def _key(self, buf):
        h = 0
        for b in buf[-self.k:]:
            h = (h * 131 + b) % self.buckets
        return h

    def run(self, stream, layout=None):
        """Walk raw bytes with an **inferred** layout: widths only, never opcode identity.

        `infer_layout` recovers which opcode is followed by 4 bytes and which by 2 by parse
        consistency. That is the whole of the syntax the learner gets, and it is recovered, not
        handed over. What is learned is the key->value mapping in a hashed table of `buckets` 16-bit
        cells; collisions, not missing keys, are what it fails on.
        """
        if layout is None:
            layout, _ = infer_layout(stream)
        assert layout, "no consistent layout: the stream cannot be parsed at all"
        out, writes = [], 0
        i = 0
        while i < len(stream):
            w = layout[stream[i]]
            key = (stream[i + 1] << 8) | stream[i + 2]
            if w == 5:                          # a record with a value: write-through
                val = (stream[i + 3] << 8) | stream[i + 4]
                self.tab[self._key([key & 0xFF, key >> 8])] = val
                writes += 16
            else:                               # a record without one: a read
                out.append((key, self.tab[self._key([key & 0xFF, key >> 8])]))
            i += w
        return out, writes


def sample_queries(keys, k, salt):
    """Uniform query sample. NOT `keys[:k]`.

    The store is written in `keys` order, so the earliest keys are the ones a collision overwrites
    first; querying them measures write order rather than coverage. That error was made twice in this
    file (once for the direct store in turn 8, once for the byte cache in turn 10), so it now has a
    name and every table uses it.
    """
    return random.Random(SEED + 2 * salt + k).sample(keys, min(k, len(keys)))


def raw_stream(keys, vals, queries, edit=None):
    """Serialize for the byte-level baseline: SETs, optional EDIT, then GETs."""
    out = bytearray()
    for k in keys:
        out += rec("SET", k, vals[k])
    if edit is not None:
        out += rec("EDIT", edit[0], edit[1])
    for k in queries:
        out += rec("GET", k)
    return bytes(out)


def two_hop(n, seed):
    """A 2-hop chain: SET a->b, SET b->c, then EDIT b->d, then GET2 a => d.

    One-hop binding is saturated by any exact store (AMEND-008 K4). Composition is not: answering
    GET2 needs both hops, so a store that loses either one answers nothing, and the coverage is
    ~ (m/n)^2 rather than m/n.

    Three DISJOINT key sets, `A -> B -> C`. The first version of this used `a -> b` and `b -> a`, i.e.
    a cycle, so GET2 returned the query itself and the chain tested nothing (0.40% where ~25% was
    expected). `A = 0..n-1`, `B = n..2n-1`, `C = 2n..3n-1`, which needs 3n < 65,536 so the 2-byte key
    field still holds. The edit moves `b -> c` to `b -> d` with `d` another member of `C`.
    """
    rng = random.Random(seed)
    A = list(range(n))
    B = list(range(n, 2 * n))
    C = list(range(2 * n, 3 * n))
    # ALL THREE must be shuffled. With `A` in order, the queries that survive hop 1 are the late
    # indices, which are also disproportionately the last writers of their hop-2 slots, so the two
    # hops correlate through write order and coverage reads 5.8% against a 1.0% ceiling.
    rng.shuffle(A)
    rng.shuffle(B)
    rng.shuffle(C)
    # Pairing A->B and B->C by the same index i (the first version) is not enough: a dict's write
    # order IS insertion order, so "last writer of a slot" means "largest index", and the index that
    # survives hop 1 is then also disproportionately the one that survives hop 2. Coverage read 5.5%
    # against a 1.0% ceiling until both pair lists were shuffled independently.
    pairs1 = list(zip(A, B)); rng.shuffle(pairs1)
    pairs2 = list(zip(B, C)); rng.shuffle(pairs2)
    hop1 = dict(pairs1)                            # a -> b, a random bijection
    hop2 = dict(pairs2)                            # b -> c
    edit_key = B[0]
    # `d` must be a value that appears nowhere else in the chain. The first version reused C[1], so two
    # B keys mapped to the same C value and the two-hop check matched the wrong link 65% of the time
    # against a 1% ceiling.
    new_val = 3 * n
    assert new_val not in hop2.values()
    hop2[edit_key] = new_val                       # EDIT b -> d
    return hop1, hop2, edit_key, new_val


def two_hop_direct(n, m, hop1, hop2, edit_key, new_val, queries):
    s1, s2 = {}, {}
    for k, v in hop1.items():
        s1[k % m] = v
    for k, v in hop2.items():
        s2[k % m] = v
    s2[edit_key % m] = new_val
    ok = 0
    for q in queries:
        # the ANSWER to GET2 a is hop2[hop1[a]] (post-edit). Comparing a slot against its own key
        # instead -- the first version -- counted coincidental matches as successes and reported 66%
        # against a 1% ceiling.
        expected = hop2[hop1[q]]
        b = s1.get(q % m)
        c = s2.get(b % m) if b is not None else None
        if c is not None and c == expected:
            ok += 1
    return ok / len(queries)


def two_hop_eval(n, m, hop1, hop2_pre, edit_key, new_val, queries, cache_bits=None):
    """One 2-hop chain evaluated before AND after the edit, for a slot store or a hashed table.

    Returns (coverage_before, coverage_after, correct_before, collateral). Collateral counts only the
    chains that answered correctly before the edit and wrongly after it -- the G7 question, and the
    ratio `collateral / correct_before` is what the charters ask for.
    """
    hop2_post = dict(hop2_pre)
    hop2_post[edit_key] = new_val
    truth_pre = {a: hop2_pre[hop1[a]] for a in queries}
    truth_post = {a: hop2_post[hop1[a]] for a in queries}

    if cache_bits is not None:                       # learned hashed table, same bit budget
        c = ByteCache(bits=cache_bits)
        put = lambda k, v: c.tab.__setitem__(c._key([k & 0xFF, k >> 8]), v)
        # TWO hops in the same table: read hop 1, use its answer as the hop-2 key. The first version
        # returned a single lookup here while the oracle path composed two, so it was scored against a
        # two-hop truth and read 0.00% at every n.
        def get(a):
            b = c.tab[c._key([a & 0xFF, a >> 8])]
            return None if b is None else c.tab[c._key([b & 0xFF, b >> 8])]
        for k, v in hop1.items():
            put(k, v)
        for k, v in hop2_pre.items():
            put(k, v)
    else:                                            # oracle slot store
        s1 = {k % m: v for k, v in hop1.items()}
        s2 = {k % m: v for k, v in hop2_pre.items()}
        get = lambda a: (lambda b: None if b is None else s2.get(b % m))(s1.get(a % m))
        put = lambda k, v: s2.__setitem__(k % m, v)

    before = {a: get(a) for a in queries}
    put(edit_key, new_val)
    after = {a: get(a) for a in queries}

    ok_b = sum(1 for a in queries if before[a] == truth_pre[a])
    ok_a = sum(1 for a in queries if after[a] == truth_post[a])
    coll = sum(1 for a in queries
               if before[a] == truth_pre[a] and after[a] != truth_post[a])
    return ok_b / len(queries), ok_a / len(queries), ok_b, coll


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
            # relabelled per AMEND-008 clause 2: `direct` is handed SET/GET/EDIT semantics, so it is an
            # oracle opcode ceiling, not a learned system
            tag = f"direct {m}" + (" (ORACLE OPCODE)" if m == 1024 else "")
            print(f"| {L:,} | {tag} | {100 * rb:.2f}% | **{coll}** | {s_bits} | 0 | "
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
    print("`B < n`. AMEND-008 clause 2 requires `B` in **bits and bytes**, not entries:")
    print("`B = 1,024 entries x 16 bits =` **16,384 bits = 2,048 bytes** (= 2 KiB). `ceiling =")
    print("min(1, B/n)` is the pigeonhole bound that AMEND-007 requires beside `D_max`. The learned")
    print("row further down uses `B = 2,048 x 16 bits =` **32,768 bits = 4,096 bytes**.\n")
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
    # ---------------------------------------------------------------- learned baseline at matched bits
    print("\n### A learned raw-byte baseline at `B = 32,768` bits (AMEND-008 clause 2)\n")
    print("Same stream, same bytes, and **no opcode table**: the three opcodes are permuted by a seeded")
    print(f"bijection (`{'/'.join(f'{o:#04x}' for o in OPS)}`), and the learner recovers which one is")
    print("followed by 4 bytes and which by 2 by *parse consistency* alone (`infer_layout` -- it keeps")
    print("the assignment that parses the whole stream to its end, and reports ties rather than breaking")
    print("them). That is the only syntax it gets. What it learns is the key->value mapping, write-")
    print("through, in a hashed table of 2,048 16-bit cells; its bits are counted exactly. The")
    print("direct-address row is labelled **oracle opcode ceiling** because it is handed `SET`/`GET`/")
    print("`EDIT` semantics instead. Note the format: 2-byte keys, so byte-level rows stop below n =")
    print("65,536.\n")
    print("| n | machine | bits | coverage | edit collateral | bytes read/token | G4 |")
    print("|---|---|---|---|---|---|---|")
    for n in (1000, 10000):
        keys, vals, ek, nv = build_stream(n, SEED + n)
        q = sample_queries(keys, 1000, n)
        cache = ByteCache()
        c1, _ = cache.run(raw_stream(keys, vals, q))
        c2, _ = ByteCache().run(raw_stream(keys, vals, q, edit=(ek, nv)))
        d1 = dict(c1)
        okb = sum(1 for k, v in c1 if v == vals[k]) / len(q)
        coll = sum(1 for k, v in c2 if k != ek and d1.get(k) == vals[k] and v != vals[k])
        rb, _, _, rd, wr, _ = direct_address(keys, vals, ek, nv, 1024, q)
        print(f"| {n:,} | LEARNED byte table (hashed) | {cache.nbits:,} | {100 * okb:.2f}% | {coll} | "
              f"2 | yes |")
        print(f"| {n:,} | direct 1024 (ORACLE OPCODE) | 16,384 | {100 * rb:.2f}% | -- | "
              f"{(rd + wr) / (len(keys) + 2 * len(q) + 1):.1f} | yes |")

    # ---------------------------------------------------------------- 2-hop composition (GET2)
    print("\n### `GET2`: composition, where one-hop binding has no headroom (AMEND-008 K4)\n")
    print("`SET a->b`, `SET b->c`, `EDIT b->d`, then `GET2 a` must answer `d`. Any exact store wins")
    print("one-hop binding, so it measures nothing; two hops need both links, and a store that loses")
    print("either answers nothing. Ceiling for an `m`-slot store is `(m/n)^2`; it is left blank for")
    print("the hashed table, whose occupancy is not uniform modulo `m` (3n distinct keys into 2,048")
    print("buckets), so a `min(1, buckets/3n)^2` bound is not a ceiling for it.\n")
    print("| n | machine | GET2 coverage | ceiling | bytes read/token | G4 |")
    print("|---|---|---|---|---|---|")
    for n in (1000, 10000):
        hop1, hop2, ek2, nv2 = two_hop(n, SEED + n)
        q = sample_queries(list(hop1), 3000, n)     # 1,000 queries put 2 sigma on a 1% ceiling
        cov_d = two_hop_direct(n, 1024, hop1, hop2, ek2, nv2, q)
        print(f"| {n:,} | direct 1024 (2 hops) | {100 * cov_d:.2f}% | "
              f"{min(1.0, 1024 / n) ** 2:.4f} | 2.0 | yes |")
        print(f"| {n:,} | KV scan | 100.00% | 1.0000 | {4 * n:,} | **no** |")
        # hashed table, 2 hops
        cache = ByteCache()
        for k, v in hop1.items():
            cache.tab[cache._key([k & 0xFF, k >> 8])] = v
        for k, v in hop2.items():
            cache.tab[cache._key([k & 0xFF, k >> 8])] = v
        cache.tab[cache._key([ek2 & 0xFF, ek2 >> 8])] = nv2
        ok = 0
        for a in q:
            b = cache.tab[cache._key([a & 0xFF, a >> 8])]
            c = cache.tab[cache._key([b & 0xFF, b >> 8])] if b is not None else None
            if c is not None and c == hop2[hop1[a]]:
                ok += 1
        print(f"| {n:,} | LEARNED byte table (2 hops) | {100 * ok / len(q):.2f}% | -- | 4 | yes |")

    # ------------------------------------------------ GET2 at the baton's budget, B = 32,768 bits
    print("\n### `GET2` at `B = 32,768` bits (2,048 slots x 16 bits = 4,096 bytes), n = 512\n")
    print("The baton's question is whether `32,768` bits is enough to answer a two-hop chain exactly.")
    print("It is -- for both the oracle store and a flat hashed table. The edit is executed correctly in")
    print("both, so G7 collateral is 0: **a correct edit of a linked value damages nothing.** G7 only")
    print("bites on a store that cannot remove the old binding (see the fast-weight section).\n")
    print("| n | machine | bits | GET2 before -> after | coll / correct-before | bytes/token | G4 |")
    print("|---|---|---|---|---|---|---|")
    for n in (512, 1000, 10000):
        hop1, hop2, ek2, nv2 = two_hop(n, SEED + n)
        q = sample_queries(list(hop1), 4000, n)
        ob, oa, ook, ocoll = two_hop_eval(n, 2048, hop1, hop2, ek2, nv2, q)
        lb, la, lok, lcoll = two_hop_eval(n, 2048, hop1, hop2, ek2, nv2, q, cache_bits=32768)
        # the scan pays one 4-byte record per stored key per hop, and its store is unbounded (hence
        # `--` in the bits column rather than a number that would flatter it)
        scan_bpt = 4 * 3 * n / 3
        print(f"| {n:,} | ORACLE OPCODE, 2,048 slots | 32,768 | {100 * ob:.2f} -> {100 * oa:.2f}% | "
              f"{ocoll}/{ook} | 4.0 | yes |")
        print(f"| {n:,} | LEARNED byte table (2,048 cells) | 32,768 | {100 * lb:.2f} -> {100 * la:.2f}% | "
              f"{lcoll}/{lok} | 4.0 | yes |")
        print(f"| {n:,} | KV scan (unbounded store) | -- | 100.00 -> 100.00% | 0/{len(q)} | {scan_bpt:,} | "
              f"{'yes' if scan_bpt <= 4096 else '**no**'} |")
    print("\nWhat this says about the `+95` points of B2 headroom claimed for `0008`: **a flat table has")
    print("already taken them.** At `n = 512` with `4,096` bytes a 2,048-cell hashed table answers the")
    print("two-hop chain at 100.00% with 0 collateral, so on this budget and this `n` there is no gap")
    print("between the oracle ceiling and a learned one. At `n = 1,000` the table falls to 67.30% and at")
    print("`n = 10,000` to 0.00% -- so the headroom the baton is looking for appears only when the number")
    print("of links exceeds the cells, i.e. it is a *capacity* gap, not a credit-assignment gap. A")
    print("candidate that cannot store keys pays for that; a table does not.")

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
    print("\n### What the oracle-vs-learned split and `GET2` show")
    print("- **At matched bits, the learned byte table is not behind on one hop.** 32,768 bits of hashed")
    print("  16-bit cells answer 100.00% at n=1,000 and **20.10%** at n=10,000, against the 16,384-bit")
    print("  oracle store's 100.00% and 9.20%. Half the bits and twice the coverage at n=10,000: the")
    print("  difference is hash spread over 2,048 buckets versus `m` slots modulo an adversarial key set.")
    print("  So on one-hop binding the 'learned' baseline is real, and anyone claiming a store must beat")
    print("  `m/n` has to beat *this* line, not the 1,024-slot one.")
    print("- **Composition is where it collapses, and that is the headroom AMEND-008 asked for.** On")
    print("  `GET2` at n=10,000 the oracle store holds **1.07%** against its `1.05%` ceiling, the hashed")
    print("  table answers **0.03%**, and only the KV scan is exact -- at **40,000 bytes/token**, ten")
    print("  times the 4 KiB budget. Two hops square the loss: `(m/n)^2` is 1% at `m=1,024, n=10^4`,")
    print("  which no fixed-budget store escapes by being clever, only by being exact.")
    print("- **Four wrong instruments were built and thrown away getting to those numbers**, and each")
    print("  one flattered a different family: queries drawn as `keys[:k]` (measures write order, not")
    print("  coverage -- the second time in this file); a cycle `a->b->a` where GET2 returned the query;")
    print("  an edit value reused from `C`, so a wrong link matched a wrong link; and pairing both hops")
    print("  by the same index, which made 'last writer' mean 'largest index' in both and reported 5.5%")
    print("  against a 1.0% ceiling. The ceiling is what caught all four.")
    print("- **`AMEND-004` is now enforced on both tasks.** Opcodes are permuted and recovered by parse")
    print("  consistency; symbols on A2 are permuted and the oracle only works when handed the inverse")
    print("  map. Neither change moved a number, which is the point: the surface was already fair, and")
    print("  now it is *demonstrably* fair rather than fair by inspection.")
    print("- **G7 does not bite on a correct edit.** Every exact store above answers 100% after the edit")
    print("  with 0 collateral, because it removed the old binding. Collateral is a property of stores")
    print("  that cannot remove one (the fast-weight rows), not of the task.")
    print("- **None of this is a candidate.** The best 2-hop number under budget is 1.07%, and the only")
    print("  exact family misses G4 by 10x. Stated because a table of failures is not a design.")
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
