# KV-cache with a smaller constant
**Status:** DEAD for our purposes — every exponent is unchanged
**Failed because:** the cost of attention is not its constant, it is its **dependence on n**. Two
independent growths, and a "compressed cache" touches neither:
1. **State** ∝ n (G2 ratio 1.0x → 10x → 100x → 1000x from 10³ to 10⁶ tokens at D=2048, L=32, fp16).
2. **Reads per generated token** ∝ n (250 MiB → 250,000 MiB, a G4 failure of ~10⁴).
Sliding windows, chunked prefill, quantised KV, grouped-query attention, cache eviction and
"linear attention with a compressed state" all reduce the coefficient of one of these curves. Not
one of them changes an exponent, and G2/G3/G4 are ratio tests — they divide out constants by
construction. That is why the charter wrote them as ratios: so the constant-factor family cannot pass
by arithmetic.
**Evidence:** `bench/RESULTS.md` §C, table of bytes(state), G2 ratio, read/token, G4, G3 proxy.
**What a candidate inherits if it reuses this:** if a proposal's speedup survives multiplying the
sequence length by 10, it is this family. Test: run it at n and at 10n and report the ratio. If the
ratio is ~10, it is attention with a better constant, whatever the diagram says. The tell in prose is
the word "compress" applied to the cache — compression of the cache is still a cache.
**Escape condition:** reads per token flat in n (G4 ≤ 4 KiB) while state stays O(1) (G2 ≤ 1.10).
That requires an *index* over the store, and an index is O(n) state — so the honest claim becomes
"O(1) working state + O(log n) reads on an O(n) store", which must be stated, not implied.
