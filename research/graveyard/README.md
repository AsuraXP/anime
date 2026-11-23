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

**Superseded:** `0001-operand-coverage.md` — measurement certified, escape condition refuted (the
"repair" is a 200/200 hand-written adder). Superseded by `0002` + `0007` + `0012`.

**Task-informed encoder (not a family file yet — mechanism in `threads/0002-k3control-p8-agent-c.md` §2):**
an "ordinal" encoder whose features include `(da+db)/2 = (a_p+b_p)/18` supplies the **pre-mod digit
sum**, i.e. the answer's antecedent. Its transfer to unseen digits is interpolation on that feature,
not symbol generalisation — and a **0-parameter** carry-blind rule beats it on 2 of 3 holdouts
(23.64% vs 11.39% on `[7,8,9]`; 31.15% vs 25.27% on `[4]`) while scoring **100% on the units digit**
to its 68.4%. Any "continuous/ordinal embedding transfers" claim must first beat the closed-form null.

**Task-family wall (not a candidate, so no file — recorded in `threads/0003-…-agent-c.md` §6):**
digit addition mod 10ᵏ is a **regular function**. A two-state FST — state = carry ∈ {0,1}, **1 bit**,
200 closed-form transition entries — is *optimal* on it and satisfies G1–G4 outright. D4 is that FST
with its unobserved transitions left out. So no candidate can beat the baseline on this family, and
any falsifier built on it is passed by construction. Before opening a thread, name a task family a
1-bit FST cannot saturate.

**Order of checks for a new candidate:** `0012` first (name the minimal automaton — if it clears the
gates, stop), then `0007` (does the abstain rule need a model at all?),
then `0004`/`0009` (does the index contain the thing you are testing?), then `0002`/`0003` (where are
the bits and what is the capacity), then `0011` (is the gap a curve or a point?), then
`0005`/`0006`/`0008`/`0010` (is the fix a constant, a trainer, or a store you are not admitting to).

**The cheapest check of all, and it killed two numbers in this repo:** compute the **analytic
ceiling** of the harness before reading the score. If measured == ceiling, the experiment had zero
degrees of freedom and the number is a restatement of the training set, not a property of the
primitive. Cost: ~15 lines, <1 s.
