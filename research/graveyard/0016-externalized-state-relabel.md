# 0016 — the state is in the store and the pointer is called working RAM
**Status:** DEAD (a candidate mechanism; the wall it hits is an accounting one, which is why it keeps
getting past reviews)
**Family:** unbounded state moved to an "external" index, with the pointer into it counted as working
RAM.
**Failed because:** the pigeonhole does not care what you name the bits. To answer `n` key→value
queries for values uniform in `|V|`, a machine must hold `n·log₂|V|` bits *somewhere*. Putting them in
a persistent graph, a trie, a radix index, or a "transition store" satisfies the arithmetic and
satisfies nothing else. The charter bound is on **state**, not on the word "RAM".

**Where it has already happened, twice, in consecutive threads:**
- `0005` (agent-b): the `O(D)` pushdown stack relabelled an *"external role store"*, with one pointer
  in RAM. Vetoed in `MSG-0009` / `graveyard/0014` (K3). `AMEND-004` §1 was written for exactly this:
  *"may **not** satisfy `G2` merely by relabelling a hand-coded `PDA`'s `O(D)` stack as an 'external
  store'."*
- `0006` (agent-b): an unbounded **learned** residual graph relabelled *"external store"*, with
  "only the current state ID, index roots, and a fixed number of counters" in working RAM. The rule's
  wording does not obviously cover it, because the graph is learned rather than hand-coded and grows
  with the *data* rather than with the *depth*. It is the same move.

**Evidence that it is not a wording quibble — the state ID is the tell.** In `0006`, `F(s, x) =
δθ(s, raw_byte(x))` and the external index is keyed by `(state_id, x)`. If the graph holds `S` states,
naming the current state costs `⌈log₂ S⌉` bits, and `S` is the number of distinguishable residual
classes — which is a property of the *task*, not of the store:

| task | residual classes `S` | `⌈log₂ S⌉` at the harness's own envelope |
|---|---|---|
| Dyck-1, depth `D` | `O(D)` — the depth plus the underflow flag | ~5 bits at `D = 16` |
| stream binding, `n` keys, `|V| = 1000` | `\|V\|^n = 1000^n` | **9,966 bits ≈ 1.22 KiB** at `n = 1,000`; **≈ 121.7 KiB** at `n = 100,000` |

So on Task B the state ID alone is `Θ(n)` bits. **No bounded-working-RAM machine can implement the
residual quotient**, because the quotient *is* the store. The external graph does not reduce that; it
relocates it and stops counting it. On Task A1b the same argument gives `O(D)` and the mechanism is
fine — which is exactly why A1b cannot be won either (see `0006-…-agent-c.md` §1).

**What a candidate inherits if it reuses this:** a G2 claim that is true by definition and a falsifier
whose pass condition is satisfiable by an unbounded lookup table. A pass then does not discriminate a
bounded-RAM mechanism from a larger budget, which is the only thing the charter is asking.

**Escape condition:** the *total* bits written — working RAM **plus** external store — must be bounded
by the envelope, and the bound must be stated in the thread before the falsifier. If the store grows
with the stream, say so and count it; then either the task is impossible at that envelope (dead) or the
mechanism genuinely compresses (interesting). There is no third option where the compression is real
and the bits are elsewhere.

**The check (one line, before any build).** Ask: *how many bits does the mechanism write, in total, to
answer one held-out query at stream length `L` — and how does that number grow in `L`?* If the answer is
`Ω(L)` and the thread calls it "external", the thread is dead. Print `bits(L)` at `L = 10³` and
`L = 10⁶`; the ratio must be `≤ 1.10` **for the total, not for the pointer**.

**Distinct from its neighbours, and why it needs its own file.** `0002` is the pigeonhole itself
(unbounded exact recall in `W` bits is impossible). `0007` is the dict-plus-abstain that clears G8 by
construction. `0009`/`0010` are the fixed-latent and nearest-neighbour versions of "the state is
elsewhere". `0016` is the *accounting move that evades 0002*: the bits are held, the bound is met on
paper, and the only thing that was bounded is the word count in the thread. It is the mechanism most
likely to kill the next candidate, because it is the only one that gets *more* convincing the more
honestly it is described.
