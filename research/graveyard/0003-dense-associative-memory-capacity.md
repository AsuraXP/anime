# Dense associative memory (outer-product / Hopfield / VSA bundling)
**Status:** DEAD-AT-SCALE — works far below capacity, collapses with a cliff
**Failed because:** storage by superposition makes the readout a sum of crosstalk terms. For
`M = Σᵢ vᵢkᵢᵀ`, reading with query `q` returns `Σᵢ vᵢ(q·kᵢ)`. Exact recovery of item `j` needs
`q·kⱼ ≈ 1` **and** `q·kᵢ ≈ 0 ∀i≠j` — near-orthogonality of the *retrieval* key against every stored
key. Nothing in the write rule enforces that for keys it has never seen, so the interference term
grows with load and the readout loses the ability to tell "retrieved" from "noise".
The tell is not the accuracy drop — it is that **false answers rise in lockstep with load**:
0.0% at load 0.125, 8.3% at 0.375, 34.2% at 0.5, 98.3% at 1.0. A system that is merely low-capacity
would go quiet; this one goes confidently wrong. That is the same defect CHARTER §3 G8 names in a
softmax Transformer, arriving by a different route.
**Evidence:** `bench/RESULTS.md` §B — D=128, ±1 keys/values, closed-form outer-product training,
7 seeds. Exact recall 81.2% → 17.9% → 0.3% → 0.0% across load 0.125 → 0.25 → 0.375 → 0.5.
**What a candidate inherits if it reuses this:** superposition *is* the mechanism, so any binding
scheme (HRR, VSA, hyperdimensional computing, fast-weight sums, linear attention) inherits the
interference floor. Capacity is O(D) and the failure is silent at the operating point where it
starts. "We use a bigger D" is the §C move: the constant changes, the cliff does not.
**Escape condition:** a cleanup memory that maps the noisy readout back to a canonical item. But a
cleanup memory is itself a table of D items addressed by content — the capacity has moved into the
cleanup, it has not vanished, and the cleanup read is O(D) or O(k). So: no escape inside one matrix.
