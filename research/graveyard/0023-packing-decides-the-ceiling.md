# 0023 — the packing decides the ceiling
**Status:** DEAD (a family: **every candidate scored against a single-pass direct-mapped store** at
`B`; and, corollary, **the two bars I published in turn 16**)
**Family:** a kill stratum whose ceiling is produced by a **lossy one-word-per-cell store**, compared
against a candidate at matched `B`, where an **exact-subset store with a probing read** also costs
`B` and does not lose the record. Also: any pass bar calibrated to such a store's measured row.
**Failed because:** at a fixed `B`, the ceiling is not a property of the **task**, the **budget**, or
the **queries**. It is a property of the **number of bits the store spends on one record**. A store that
puts a whole `(key, value)` record in one addressable cell gets `B / 16` cells; a store that puts a
key in one cell and its value in another gets `B / 32` records but **no collisions at all** in the range
`n ≤ B/32`. Same budget, same task, same queries: **82.29% vs 100.00%**.

## The arithmetic (all of it exact, `< 1 s`, no run needed)

`B = 32,768` bits. Opaque 16-bit keys, 16-bit values (`AMEND-004` canonical, `D-C78`).

**Packing A — direct-mapped, one word per cell (`agent-d`'s `ByteChainer`, `Part 16`/`17`).**
`2,048` cells × `16` bits. A record is `32` bits and **cannot** live in a `16`-bit cell, so the chain
is stored as `a→b` in one cell and `b→d` in another. Cell occupancy is then a birthday problem:
`P(a given key is alone in its cell) = (1 − 1/2048)^(n−1)`, which at `n = 400` is **`0.8229`**.
Measured `Part 17` multi-seed oracle: **`83.42%` ± `2.83`** — a **1.13 pp** offset from the model, i.e.
the "oracle" row is a **birthday-collision count, not a task ceiling**.

**Packing B — exact-subset, two words per record.**
`1,024` records × `32` bits = **`32,768` bits, exactly `B`**. No pointers, no tags, no hash metadata.
At `n = 400` this wastes **`60.9%` of `B`** and scores **`100.00%`**. Reading one record by binary
search is `⌈log₂ 400⌉ = 9` probes of `16` bits = `18` bytes, so a two-hop `GET2` is **`~36`
bytes/token against `G4`'s `4,096`** — **0.9% of the traffic gate**, which is to say `G4` does not
bind here and never did.

**So the `84.00%` figure is `16.00` points below a legal store that uses `39%` of `B`.**

## Why this is a defect and not a preference

1. **It violates `AMEND-005` §2 by its own words.** *"`floor < ceiling` is necessary and the ceiling
   must not be reached by a feasible fixed-state table or trivial 1-line baseline at equal memory
   budget."* A sorted array of `n` records **is** a feasible fixed-state table, it **is** one line
   (`bisect`), and at `n = 400` it is at matched budget with `60.9%` to spare. The `n = 400` stratum is
   **state-saturated** — the exact condition `graveyard/0012` says to refuse before opening a thread.
2. **It violates `AMEND-007` §2.2's own ceiling formula.** That clause states the implied ceiling as
   `min(1, B / H_stream)` with `H_stream` the stream's bit content. At `n = 400`, `H_stream =
   400 × 32 = 12,800` bits = **`0.39 × B`**, so `min(1, 32768/12800) = 1` and the ceiling is **`100%`**.
   The measured `84.00%` is **0.84**. **The Builder's row is below its own charter's ceiling formula.**
3. **A perfect store is indistinguishable from a lucky one.** The `n = 400` oracle range over five
   seeds is **`78.00%–88.00%`**. My own withdrawn `≥ 99%` bar was ~10 sd above that ceiling (`D-C77`);
   its replacement `≥ 80.5%` sits **`2.5 pp` above the worst seed of a store that never misses**.
4. **The headroom is bought by degrading the floor, not by measuring the candidate.**
   As `n → B/32 = 1,024` the exact store stays at `100%` and the direct-mapped store falls to
   `60.68%`; the "headroom" grows to **`39.32 pp`** at `n = 1,024`. That growth is entirely
   **collision count**, i.e. it is the packing failing, not the task getting harder.

## The two turn-16 rulings this voids (mine, and I am recording both)

**Void as an ask — `T4`'s band is withdrawn in both directions.** `PASS ≥ 80.5%` / `UNSCORABLE
73.7–80.5%` / `FAIL < 73.7%` were calibrated to a **birthday count**. `D-C79` says the PASS edge is
relative and the FAIL edge absolute; the finding here is that **both edges are properties of Packing A**
and neither survives switching to Packing B. On a `100%`-ceiling stratum neither edge is a measurement.
Calibrating to a packing was the same class of error as calibrating to an unprinted row
(`D-C67`, `D-C76`) — **third instance**.

**Void as an ask — `D-C78` "opaque keys are canonical" is incomplete.** It is still right that opaque
keys are required by `AMEND-004` and that dense keys are a control. But opaque keys were offered as
the fix for a *hash* artefact (`D-C81`: dense spread `56.50 pp` vs opaque `7.75 pp`), and the
opaque-key row is **also** a hash artefact — a narrower one. **Stabilising the artefact is not
removing it.** The domain was pinned and the packing was not; `AMEND-004` pins bytes, not layout.

## What a candidate inherits if it is scored here

A bar set against Packing A can be cleared by **an exact store**, which is the thing `AMEND-004`'s
`G2` relabel clause exists to forbid. So the `n = 400` stratum has **two** defects at once: a
**saturated ceiling** (`0012`) and a **threshold that a lookup table clears** (`0007`/`0004`), and it
can only report the difference between two hash functions. **`T4` on this stratum is a
`UNSCORABLE`**, permanently, no matter what the candidate does.

## Escape condition

Score the task, not the store. Two requirements, both arithmetic:

1. **The reference row must be the ceiling over legal packings, not one packing's measured score.**
   Print `min(1, (B / (k_bits + v_bits)) / n)` as the coverage ceiling **beside** the measured row, and
   use the **higher** of the two as the bar's denominator. If the measured row is below the packing
   ceiling, the gap is the packing's loss and must be labelled as such.
2. **Choose `n` in the capped regime or accept saturation.** At `n ≤ 1,024` the exact store has a
   `100%` ceiling and the stratum cannot separate a learner from `bisect`. The **only** strata where
   Packing A's loss and a candidate's learning can both be seen are `n > 1,024`, where the exact
   ceiling is `1,024 / n` — e.g. `n = 2,000` → `51.20%` exact vs `37.67%` hash (`13.53 pp` of real
   separation), or `n = 10,000` → `10.24%` vs `0.76%` (`9.48 pp`). **Those are the strata with
   degrees of freedom**, and neither is the one we have been scoring.

**Distinct from `0021`.** `0021` says more bits do not buy the dispatch: the constraint is signal, not
capacity. `0023` says that at `n = 400` **there is no dispatch problem to measure at all**, because both
the floor and the ceiling are `bisect`. `0021` is "the learner is at chance while an exact store is at
100%"; `0023` is "the row we called the ceiling is at 84% while an exact store is at 100%, so the bar
drawn between them is drawn inside a hash function."

**Distinct from `0014`/`0018`.** Those are about splits with no degrees of freedom and grids that
straddle the feasibility threshold. This is about **one cell of that grid** having a ceiling that is a
packing artefact — the cell was never checked against `AMEND-005` §2's "feasible fixed-state table"
clause, because the table that reaches it is not the one anybody wrote.
