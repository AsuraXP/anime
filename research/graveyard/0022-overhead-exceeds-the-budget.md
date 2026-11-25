# 0022 — overhead exceeds the budget
**Status:** DEAD (a family: "sparse linked cells at a fixed bit budget" and "a full eligibility trace as
the credit carrier")
**Family:** any design whose *bookkeeping* — next-pointers, occupancy tags, hash metadata, a
per-parameter eligibility trace — is charged against the same `B` as the payload, and is discovered to
cost more than the payload leaves room for.
**Failed because:** at a fixed `B`, the allowance for overhead is **`(B − payload − controller) / n` per
cell** — a number nobody prints until it is negative. Two independent instances, both arithmetic:

**Instance 1 — the per-cell pointer (agent-b `0008`, turn 14).** A sparse linked cell is
`16-bit key + 16-bit value + 10-bit next-pointer = 42 bits`; at `n = 400` two-hop chains that is
`800` bindings, so **`800 × 42 = 33,600 bits`**, already **832 bits over `B = 32,768` before any
controller or trace**. The pointer alone is `800 × 10 = 8,000 bits` = **24% of `B`**, and it is the price
of the `O(1)`-traffic reads that `0020` demands. **So `0020`'s escape condition and `B` are in tension,
and the pointer is where the tension is paid.**

**Instance 2 — the full eligibility trace.** `0008`'s carrier is `e_t = λ e_{t−1} + ∇_W log π(a_t|s_t)`,
a matrix the same shape as `W`. **A full eligibility trace costs exactly `|θ|` bits** — it doubles the
controller. With `W ∈ R^(5×128)` at float32 that is **`640 × 32 = 20,480` bits**, so `θ + e_t =
40,960` bits and the controller alone is **`1.25 × B`**, before one byte of memory.

**And the ledger that reported this was itself wrong, in the direction that flattered it.** `0008`
budgeted `θ = 2,560` bits and `e_t = 2,560` bits for *"640 float32 weights"* — that is **640 × 4**, i.e.
**bytes**, not bits. The correct figure is **8× larger**. So the published ledger said **38,848 bits
(1.19× B)**; the corrected ledger is **≥ 74,688 bits (2.28× B)**. The overrun was understated **8× on
the two largest components** — the same unit confusion as `0007`'s `--memory-budget 1048576` (D-C46) and
`B` quoted in slots (D-C53), in the one place where it hid a factor of two.

**Third defect, independent of arithmetic:** `0008`'s state `s = (p, r, y)` where `EMIT` does
`y ← y · r`. **`y` grows by one byte per `EMIT`**, so `|s_t| = O(T)` — at `D = 64` up to
**`128 bytes = 1,024 bits`** — while the ledger budgets **128 bits** for the whole of `s_t`.
**That is an `R2`/`G2` violation as written**: the working state is not `O(1)` in sequence length. Either
`y` is bounded explicitly or it is charged, and neither is done.

**What a candidate inherits if it makes this bet:** a ledger that balances on paper and a build that
cannot be run, discovered after the implementation hours are spent. `0008` is the good case — the
Inventor found the overrun **before** building, which is the entire point of `AMEND-009`'s `T5`.

**Escape condition:** print the overhead **before** the payload. Two lines, both cheap:
`(B − payload − controller) / n` — if it is smaller than the per-cell overhead the encoding needs, the
encoding is dead, not the task. And `|e_t|` against `|θ|` — if the carrier is a full trace, the
controller costs twice what the policy costs, and that is a design decision that must be made
explicitly rather than discovered.

**The check (two subtractions, before any build).**
1. **Per-cell overhead:** `(B − payload − controller) / n` vs the per-cell metadata cost. `0008`: `2.4`
   bits/cell available against `10` needed — dead by **4.2×**.
2. **Carrier cost:** `|e_t| / |θ|`. A full trace gives `1.0`, i.e. the carrier doubles the controller.
   Any carrier with `|carrier| ≥ |θ|` must be justified against the memory it displaces.

**Why it is not `0020` or `0021`.** `0020` says traffic and capacity are the same knob. `0021` says
capacity is not the binding constraint. **`0022` says the bookkeeping is charged against the same budget
as the payload and can exceed it** — a third axis, and the only one that is invisible until you do the
subtraction. A candidate can satisfy `0020` (sparse reads) and `0021` (plenty of bits) and still die here,
because the bits it has are already spent on pointers and traces.

**Distinct from `0016`.** `0016` is a *state* argument: the mechanism writes `Ω(L)` bits and calls them
external. `0022` is a *ledger* argument: the mechanism writes a bounded number of bits and they do not
fit. One is about growth, the other about arithmetic at a fixed `n`.
