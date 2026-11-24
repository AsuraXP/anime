# 0021 — capacity cannot buy the dispatch
**Status:** DEAD (a family: "scale the learned controller" — give it more parameters, more slots, more
state, and it will learn the memory operations)
**Family:** learned controllers over external memory whose claim to adequacy is a **bit count** —
NTM / DNC / neural-RAM lineage, and every "give it a bigger `B`" repair.
**Failed because:** the bit count is not the binding constraint. On the tasks where an oracle wins, it
wins at a **fraction** of the learned machine's bits; on the task where a learned machine wins, it wins
by **generalizing**, not by having more bits. In neither case does adding state add score. What is
missing is **signal** (`0019`) and **sparse reads** (`0020`), and neither is bought with bits.

**Evidence** — `agent-d`, turn 11, `bench/`, gate **62/62 in 58.7 s** (`C17` new). Fixed
`B = 32,768` bits, quoted in bits and bytes, seeded-bijection opaque bytes, every oracle row labelled:

| stratum | oracle | bits | **learned, 32,768 bits** | verdict |
|---|---|---|---|---|
| A2, `D = 64` | **100.00%** | **69** (65 stack + 4 flags) | **51.25% / 49.38%** — chance | **475× the bits, zero gain** |
| B, one hop, `n = 10,000` | 9.20% (exact `m`-slot) | 16,384 | **20.10%** (hashed byte table) | the *learned* machine wins — by generalizing |
| B, `GET2`, `n = 10,000` | **1.07%** (ceiling 1.05%) | 16,384 | **0.03%** | composition is where capacity *does* bind |

Read the three rows together, because they are one statement:

1. **A2 is the headline.** A **69-bit** hand-coded syntax test scores **100.00%** at `D = 64`; a
   **32,768-bit** learned table scores **chance**. That is **475× the state for zero points.** The
   learned machine is not capacity-limited — it is *signal*-limited. It has 32,768 bits and no way to
   find out which of its actions helped.
2. **One-hop is the control, and it inverts.** Here the learned machine at 32,768 bits (**20.10%**)
   beats the exact `m`-slot oracle at 16,384 bits (**9.20%**). It is not winning on bits — it has 2× the
   oracle's bits and it beats a **ceiling**, which is only possible if it is doing something the exact
   store cannot: **generalizing past the stored subset**. So the win comes from the *learning rule*,
   and the exact-subset bound `min(1, m/n)` is **not** a ceiling for a generalizing store (D-C61).
3. **`GET2` is where capacity bites, and it bites hard.** Composition squares the per-hop loss: the
   exact store sits **at** its `m²/n²` bound (1.07% vs a 1.05% ceiling) and the learned machine
   collapses to **0.03%**. Nobody under 4 KiB/token survives except an exact store, and the exact store
   that survives costs **40,000 bytes/token** — a `G4` failure by 10×.

**What a candidate inherits if it makes this bet:** a `B` it can quote and a score that does not move.
It will report "32,768 bits of memory" and land at chance on A2, and the post-mortem will blame the
optimizer, the initialization, the learning rate, the depth of the controller — everything except the
absence of a carrier.

**Escape condition:** name the carrier that gives an action at `t` a signal from an error at `T`
(`0019`), and make the read **sparse** — `O(1)` traffic independent of capacity (`0020`). Those two are
exactly what `AMEND-008` now requires of `0008`, and neither is a bit count. **A proposal whose repair
for a low score is a larger `B` has not read this entry.**

**The check (one row, before any build).** Print the **oracle's bits** and the **best legal learned
baseline's score at `≥ 10×` those bits, at the same `B`. If the learned machine is at chance, **the
binding constraint is signal, not capacity** — and the thread is dead no matter how large `B` becomes.
Cost: one row, and the Builder has already run it.

**Why it is not `0019` or `0020`.** `0019` is the *mechanism* of the failure (no carrier → contextual
bandit → zero signal at `t < T`). `0020` is the *traffic* law (capacity `∝ d` and bytes/token `∝ d` are
the same proportionality, so a traffic gate is a capacity gate). **`0021` is the measured consequence:
even when capacity is abundant and traffic is affordable, it buys nothing.** Three different axes —
signal, traffic, capacity — and a candidate must satisfy all three, which is why each has its own file.

**Distinct from `0015`.** `0015` says a *task* is dead when the state count is feasible at the declared
envelope. `0021` says a *learned machine* is dead when the state count is **not** the thing it is
missing. `0015` kills the task; `0021` kills the repair.
