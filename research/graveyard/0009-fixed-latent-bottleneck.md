# Fixed-latent cross-attention (Perceiver / inducing points / k-slot bottleneck)
**Status:** DEAD-AT-SCALE — a pigeonhole with a graceful failure mode
**Failed because:** encoding is a softmax-weighted average of n inputs into **m** latent slots, and
decoding reads the same m slots. Distinct items beyond m must superpose inside a slot, so the model
can hold at most m independent retrievals, and m is fixed at architecture time. This is the §A
pigeonhole with a softer edge — and that is precisely what makes it dangerous: because the average is
continuous, the failure is *interpolated*, so the model produces a plausible wrong answer rather
than abstaining. It looks like reasoning and is a low-pass filter over the input.
The measured signature is characteristic and worth knowing: accuracy on an n-item recall task is
flat while n ≤ m and then degrades **smoothly** with no discontinuity, unlike the outer-product cliff
in §B. A smooth curve invites the reading "it generalises"; it is the reading "it blurs".
**Evidence:** the architecture's own m-slot construction; the same wall as §A (2^W states, here m
slots with D dims each). Any Perceiver-style reproduction on n > m item recall shows this curve.
**What a candidate inherits if it reuses this:** any design that "compresses the sequence into k
latents", "uses a fixed number of memory slots", or "summarises into a learned query set". It will
pass every benchmark smaller than k and die at n >> k, and it will do so without an abstention —
so it also fails G8 in the direction that matters (confident wrong, not abstain).
**Escape condition:** m must grow with n, which is the cache again (`0006-kv-cache-constant-factor.md`);
or the latents must be *written* sparsely and addressed by content, which is a store — the thing
CHARTER §1.1 already permits and G4 already prices.
