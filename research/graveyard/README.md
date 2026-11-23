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

**Order of checks for a new candidate:** `0007` first (does the abstain rule need a model at all?),
then `0004`/`0009` (does the index contain the thing you are testing?), then `0002`/`0003` (where are
the bits and what is the capacity), then `0005`/`0006`/`0008`/`0010` (is the fix a constant, a
trainer, or a store you are not admitting to).

**The cheapest check of all, and it killed two numbers in this repo:** compute the **analytic
ceiling** of the harness before reading the score. If measured == ceiling, the experiment had zero
degrees of freedom and the number is a restatement of the training set, not a property of the
primitive. Cost: ~15 lines, <1 s.
