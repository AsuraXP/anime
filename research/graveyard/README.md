# graveyard/

**Owned by the ADVERSARY.** One file per family of ideas that has already failed, with the
**specific mechanical reason** it failed. Not "this didn't work" — the wall it hit.

Purpose: a new candidate must be checked against this directory *before* it earns implementation
time. Without it, four agents will independently rediscover the same three dead ends, which is the
most expensive possible way to be wrong.

## Format

```
# <family name>
**Status:** DEAD / DEAD-AT-SCALE / PORTED-ELSEWHERE
**Failed because:** <the mechanical reason, one paragraph>
**Evidence:** <paper/result, or our own measurement + command>
**What a candidate inherits if it reuses this:** <the specific property that kills it>
**Escape condition:** <what would have to be true for this to work, if anything>
```

## Seed (written by the Steward, to be attacked and extended by the ADVERSARY)

These are the walls already measured or argued in this repo, not literature summaries:

- **Unbounded exact recall in bounded state** — dead, pigeonhole (`bench/RESULTS.md` §A).
- **Dense associative memory at capacity** — dead above load ≈ 0.125 for exact per-pattern recovery;
  interference is the pigeonhole wall in matrix clothing (§B).
- **Table-of-concrete-operands as "composition"** — dead, 11.8% held-out = chance (§D, D-004).
- **Bigger optimiser as a substitute for the right representation** — dead, 5.9% vs 5.9% (§D).
- **KV-cache with a smaller constant** — dead for our purposes; every G2/G3/G4 curve is unchanged (§C).

An entry that only says "this is hard" is not an entry. It must name the mechanism.

## Index (checked against every new candidate before it earns implementation time)

| File | Family | Mechanism it died on | Re-check trigger |
|---|---|---|---|
| `0001-operand-coverage.md` | restricted operand range | index never saw the digit you test | any "generalises from few examples" claim |
| `0002-bounded-state-exact-recall.md` | unbounded exact recall in W bits | pigeonhole + `q·log₂S` energy | any "bounded state, exact recall" claim |
| `0003-dense-associative-memory-capacity.md` | outer-product / VSA / Hopfield | crosstalk needs near-orthogonal unseen keys; false answers rise with load | any superposition or binding scheme |
| `0004-concrete-operand-table-composition.md` | `T[a][b]` | unseen operand addresses an unwritten row | any index containing the operand *value* |
| `0005-optimizer-substitution.md` | "train it longer / wider" | 5.9% = 5.9%, span is not the problem | any proposal whose fix is the trainer |
| `0006-kv-cache-constant-factor.md` | compressed / sliding / quantised cache | changes the coefficient, not the exponent | any "compress the cache" claim |
| `0007-abstention-by-key-miss.md` | `abstain iff key ∉ table` | a dict clears G8 by construction; measured = ceiling | **any G8 result** |
| `0008-fast-weight-superposition-recurrence.md` | fast weights / linear attention | no "do not disturb" direction; keys not controllable at test | any additive matrix state |
| `0009-fixed-latent-bottleneck.md` | Perceiver / k slots / inducing points | n > m superposes; failure is smooth, so it reads as capability | any "compress into k latents" claim |
| `0010-nearest-neighbour-retrieval.md` | kNN / RAG / vector index | argmax is total (no reject) and reads are O(n) | any "find the closest thing" readout |
| `0011-single-budget-generalisation-gap.md` | a gap measured at one `TRAIN_N` | conflates approximation error with estimation error; the 2,000-pair point rises 40 points with 20x data | **any "representational, not budget" claim** |
| `0012-minimal-automaton-saturation.md` | a benchmark whose minimal automaton clears G2/G3/G4 | if a 1-bit FST or a hash table saturates it, no candidate can score above ceiling | **before opening any thread** — name the automaton and the gate it fails |
| `0013-finite-closure-is-a-finite-automaton.md` | composition closing into a finite family of order M | the composite is one of M states, so an M-state automaton saturates it — **but only if M is feasible** | **the first check of all** — does the *state space* grow with depth? |
| `0014-degenerate-stratum.md` | a kill metric scored on a split with no degrees of freedom | the split decides the number before the run; appeared with both polarities (0003 baseline-crippled, 0005 candidate-crippled) | **before scoring anything** — print the mechanism's floor and ceiling on each split |
| `0015-declared-envelope.md` | a state space counted in the limit instead of at the declared envelope | `closure.py` enumerated Dyck-1 to depth 32 and said `33 states / LIVE`; the harness declares `D ≤ 16`, where the requirement is **19 states = 5 bits** and one fixed machine is exact on the whole grid | **before trusting any `LIVE` verdict** — print `|states|` *at the declared envelope*, with the envelope on the same line |

**Superseded:** `0001-operand-coverage.md` — measurement certified, escape condition refuted (the
"repair" is a 200/200 hand-written adder). Superseded by `0002` + `0007` + `0012`.

**Task-informed encoder (not a family file — mechanism in `threads/0002-k3control-p8-agent-c.md` §2,
**§2 WITHDRAWN** in §8 of that file):** an "ordinal" encoder whose features include
`(da+db)/2 = (a_p+b_p)/18` supplies the **pre-mod digit sum**, i.e. the answer's antecedent. I claimed
that was the mechanism of its transfer. `agent-d`'s `bench/act_ablate.py` refuted it: deleting the
digit sum costs only **2.45 / 1.18** points against an edge over one-hot of **17.81 / 10.84** — at most
14% of the edge. The digit sum is a contributor, not the explanation; the transfer is carried by the
ordinal encoding of `da` and `db` themselves. **What survives, and is the load-bearing part:** a
**0-parameter** carry-blind rule beats the 1,406-parameter ordinal model on 2 of 3 holdouts
(23.64% vs 11.39% on `[7,8,9]`; 31.15% vs 25.27% on `[4]`) while scoring **100% on the units digit** to
its 68.4%. Any "continuous/ordinal embedding transfers" claim must first beat the closed-form null —
and **a true algebraic identity is not evidence that the term is load-bearing.** That is how §2 died.

**Task-family wall (not a candidate, so no file — recorded in `threads/0003-…-agent-c.md` §6):**
digit addition mod 10ᵏ is a **regular function**. A two-state FST — state = carry ∈ {0,1}, **1 bit**,
200 closed-form transition entries — is *optimal* on it and satisfies G1–G4 outright. D4 is that FST
with its unobserved transitions left out. So no candidate can beat the baseline on this family, and
any falsifier built on it is passed by construction. Before opening a thread, name a task family a
1-bit FST cannot saturate.

**Order of checks for a new candidate:** `0014` (is the kill metric scored on a split where the
mechanism can be wrong?), `0015` (is the state space counted **at the declared envelope**? Dyck-1 is
19 states at `D=16` and unbounded only in a limit nobody runs), `0013` first (does the composite
**state space** grow with depth? digit addition = 2, affine action = 10,100 — both constant, both
dead), then `0012` (name the minimal automaton — if it clears G2/G3/G4, stop),
then `0007` (does the abstain rule need a model at all?),
then `0004`/`0009` (does the index contain the thing you are testing?), then `0002`/`0003` (where are
the bits and what is the capacity), then `0011` (is the gap a curve or a point?), then
`0005`/`0006`/`0008`/`0010` (is the fix a constant, a trainer, or a store you are not admitting to).

**The three checks that have killed every thread so far, all under a second:**
1. **State-space check (`0013`).** Enumerate the composites reachable from the generators. If
   `|states| / |Σ|^depth` ≈ 0, it is a finite automaton and the thread is dead.
2. **Envelope check (`0015`).** Count the states **at the declared envelope**, not at the enumeration
   limit. If the count is feasible there, the task is dead no matter what the family does in the
   limit. Linear-in-the-envelope (`D+3` for Dyck-1) is dead at every runnable depth.
3. **Freedom-to-fail check (agent-d's rule, `0004` §1).** *A measurement must have at least one
   outcome that would embarrass its author.* If the mechanism is exact algebra, the falsifier cannot
   fire and the thread is a tautology. `0002`'s repair, `0003`'s stratum and `0004`'s two-point solve
   all fail this.

**The cheapest check of all, and it killed two numbers in this repo:** compute the **analytic
ceiling** of the harness before reading the score. If measured == ceiling, the experiment had zero
degrees of freedom and the number is a restatement of the training set, not a property of the
primitive. Cost: ~15 lines, <1 s.
