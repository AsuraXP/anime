# 0020 — capacity is the budget
**Status:** DEAD (a store family; it fails at the gate rather than at the accuracy, which is why it looks
like a tuning problem right up until it is not)
**Family:** superposed / holographic / fast-weight / vector-symbolic stores — any store whose **read
touches every element**, so that per-token traffic scales with the dimension that also sets capacity.
**Failed because:** for such a store, **capacity ∝ dimension** and **bytes read per token ∝ dimension**
are the *same proportionality*. So a traffic gate is a capacity gate. Fix the traffic budget and you
have fixed how many bindings the store can hold, which fixes recall. **The score is decided by the gate,
not by the mechanism** — and no amount of cleverness in the binding scheme changes it, because the
binding scheme is not the thing that is being bounded.

**Evidence** — `agent-d`, turn 9, `bench/stream_ram.py`, superposed store
`s = Σ_k ψ(v_k)·φ(k)` with ±1 key codes and 16 block-coded value bits, 0 parameters, pair-identical
runs, `certify.py` **51/51**:

| `d` | `n` | recall | collateral (add / oracle / recalled) | bytes/token | G4 |
|---|---|---|---|---|---|
| 1024 | 32 | 28.1% | 2 / 1 / 1 | 2,069 | yes |
| 2048 | 64 | 28.1% | 5 / 0 / 2 | 4,117 | **no** |
| 4096 | 128 | 35.2% | 3 / 1 / 4 | 8,213 | **no** |

**At equal bits the table wins outright.** 16,384 bits buys either **1,024 slots** (100% recall at
`n = 32`) or **one `d = 1024` vector** (28.1%). That is a **~114× capacity difference at identical
bits.** `agent-d`'s own words: *"At equal bits the m-slot store wins outright. A shared readout buys
nothing on this task except the ability to fail G7."*

**And the budget and the capacity are the same number.** At `d = 1024` the store reads ~2 KiB/token and
holds about **nine** bindings. The 4 KiB `G4` budget admits `d = 1024` and nothing larger
(`d = 2048` → 4,117 B/token, over). Doubling `d` doubles capacity *and* doubles the traffic, so **the
gate and the capacity move together and neither can be traded for the other.** To hold 1,000 bindings at
this efficiency would need ~222 KiB/token — **56× over budget.**

**What a candidate inherits if it reuses this:** a `G4` pass that caps it at ~9–18 bindings, and a
recall ceiling of roughly `9/n`. It will look like a *capacity* failure — "superposition holds few
bindings" — when it is a *gate* failure: the traffic budget is the capacity.

**Escape condition:** the read must **not** touch every element. A store whose per-token traffic is
independent of its capacity — an addressed table, a tree, a hash index with bounded probe count — has
capacity `B / bits_per_record` and traffic `O(1)`. Those are the stores that can actually compete, and
they are the ones `0007` already names (`READ(address)`, `WRITE(address, value)`). **So the escape is to
not superpose.**

**The check (one line, before any build).** For the proposed store, print **capacity** and **bytes per
token** as functions of the same parameter. If both are `Θ(d)` — or `Θ(anything)` of the same variable —
the gate fixes the score and the thread is dead. Cost: two columns.

**Why it is not `0003`.** `0003-dense-associative-memory-capacity` says superposition fails because
crosstalk rises with load — an *accuracy* statement. `0020` says it fails because the read cost and the
capacity are the same knob — a *gate* statement. They are different failures with the same symptom, and
they need different fixes: `0003` wants better codes, `0020` says no code helps. A candidate that
"reduces crosstalk" still dies here.

**Distinct from its neighbours.** `0002` is the pigeonhole (bits bound capacity). `0006` is a
constant-factor fix that does not change the exponent. `0020` is the **coupling**: when the resource a
gate bounds is the same resource that buys capacity, the gate is the specification. It also explains why
`G7` is a weak gate on this task while `G4` bites — `agent-d` measured collateral at 0–5 keys wherever
the store works, growing only where recall has already collapsed.
