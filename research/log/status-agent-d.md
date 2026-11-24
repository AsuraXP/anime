# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 11 — `AMEND-008` clause 2: oracle ceilings separated from learned baselines
**Branch:** `arena/154facdf-anime`
**State:** both asks done. Gate **62/62 in 58.7 s** (`C17` new). Nothing new built for `0007`.

## Did

1. **Labelled every oracle row.** `dyck2.py` stacks are **`ORACLE PARSER`** (hand-coded `push`/`pop`;
   cap 64 = 65 stack bits + 4 flags = **69 bits**, exact through `D=64`). `stream_ram.py`'s `direct 1024`
   is **`ORACLE OPCODE`** (handed `SET`/`GET`/`EDIT`).
2. **Learned baselines at `B >= 32,768` bits**, with bits *and* bytes quoted everywhere:
   `16,384 bits = 2,048 bytes` for the m-slot store, `32,768 bits = 4,096 bytes` for the learned rows.
   On A2: a hashed 6-symbol context table and a hashed-feature perceptron. On Task B: a hashed
   byte-level table, plus a **`GET2`** block (one-hop binding is saturated, so it measured nothing).
3. **Found the headroom `AMEND-008` asked for — in both directions.**

| where | oracle | learned, 32,768 bits |
|---|---|---|
| A2, `D=64` | **100.00%** at 69 bits | 51.25% / 49.38% (chance) |
| B, one hop, `n=10,000` | 9.20% at 16,384 bits | **20.10%** |
| B, `GET2`, `n=10,000` | **1.07%** (ceiling 1.05%) | 0.03% |

So 475x the state buys nothing on A2, and *half* the state loses on one-hop binding — the learned
table is the honest bar there. Composition (`GET2`) then squares the per-hop loss and nobody under
`4 KiB`/token survives it except an exact store, which costs **40,000 bytes/token** (G4 fail, 10x).

## Four instruments lied on the way, and are logged as such

`keys[:k]` queries (second occurrence — now a named helper) · a `GET2` cycle `a->b->a` · an edit value
reused from `C` · both hops paired by index. Reported 0.00%, 0.40%, 65.20%, 5.50% respectively; the
pigeonhole bound caught all four. BD-042..BD-044.

## Next

- Baton passes to `agent-a` (#2). `0008`'s clause 1 (credit-assignment equations) is **not mine to
  fill** — the bench can only measure what it is given, and a learned counter above chance at `D=64`
  is the row that would move this file.
- Untested and cheap: `GET3` (depth-3 composition, cubes the loss) and a trained-embedding store at
  `4,096 bytes` as a harder matched-bit baseline.
