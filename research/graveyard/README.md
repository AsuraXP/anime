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
