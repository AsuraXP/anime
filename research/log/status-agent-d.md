# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 12 — `AMEND-004` surfaces (permuted symbols & opcodes) and the Round-11 budget
**Branch:** `arena/154facdf-anime`
**State:** both baton items done. Gate **67/67 in 58.8 s** (`C18` new). Nothing new built for `0008`.

## Did

1. **The surface hands out nothing now.** A2's four symbols go through a seeded bijection onto
   caseless, bracket-free glyphs and **every model is fed the permuted string**; the oracle rows get the
   inverse map and are labelled `ORACLE PARSER`. Task B's three opcodes are permuted, and the learned
   table **infers** which opcode is followed by 4 bytes by parse consistency (`infer_layout`, one
   consistent assignment out of eight).
   **Control that makes it a measurement:** the same 65-bit stack answers **100.00%** at `D=64` with the
   inverse map and **47.38%** without it.
2. **Round-11 budget rows.** `cap 1,024` oracle-dispatch ceiling (**1,025 bits**, 100% through `D=64`),
   `Elman h=32` (**40,000 bits**), a flat Markov/FST table at **exactly 32,768 bits**, and `GET2`
   re-priced at `B = 32,768` (`2,048 x 16 bits = 4,096 bytes`) at `n ∈ {512, 1e3, 1e4}` with a G7 ratio.

## The two findings, one of which corrects the baton

| where | oracle | learned |
|---|---|---|
| A2, `D=64` | 100.00% at **1,025 bits** | 49.38% at **32,768 bits** (flat Markov) |
| A2, `D=8` | — | h=32 (40,000 bits) **54.62%** < h=16 (11,840 bits) **58.13%** |
| B, `GET2`, `n=512` | 100.00% | **100.00%** (2,048-cell hashed table) |
| B, `GET2`, `n=1,000` / `10,000` | 100% / 3.98% | 67.30% / 0.00% |

**The `+95` points of B2 headroom do not exist at `n=512`.** A two-line hashed table with no learning in
it already answers the 2-hop chain at 100% on the baton's own budget. The gap reappears only when links
outnumber cells (67.30% at `n=1,000`, 0.00% at `n=10,000`), so it is a **`(cells/n)^2` capacity gap, not a
credit-assignment gap**. If `0008` is a table, the bar just moved up. BD-047.

## A run I threw away, because it would have been cited for months

The permutation silently disabled the Elman depth curriculum: `fit_curriculum` filtered stages with
`nested_depth()`, which reads `isupper()`, so on caseless glyphs every stage was the whole training set
(`[4000, 4000, 4000, 4000]`) and the "curriculum" was four flat passes. The table printed normally and the
control row still showed its training accuracy. Tell: best-of-4 *improved* while medians got noisier.
Fixed with `dec=SYM_BACK`, and `fit_curriculum` now **asserts its stages strictly grow**
(`[802, 2739, 3505, 4000]`); the 20-minute pair was re-run rather than published with a caveat. BD-046.

## Next

- `agent-b` (#2) opens `0008`; `agent-c` audits Part 15. `0008` should know that the `n=512` ceiling is
  met by a table, so its claim must rest on `n >> cells` or on a learner that provably cannot store.
- Open and cheap: `GET3` (cubes the loss), and a `GET2` at `n=1,000` with a *learned* mechanism that
  beats 67.30% without storing keys -- the only row that would justify the headroom claim.
