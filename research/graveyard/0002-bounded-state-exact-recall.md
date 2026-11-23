# Unbounded exact recall in bounded state
**Status:** DEAD (formal, not empirical)
**Failed because:** a causal update `sₜ = F(sₜ₋₁, xₜ)` over `W` bits is a map from the set of all
histories into `2^W`. Two independent walls close every door:
1. **Pigeonhole.** `n > 2^W` distinct histories must collide, and for any collision there exists a
   query set on which the two histories need different answers — so at least one history is answered
   wrong. There is no architecture that escapes this, because it is a statement about functions, not
   about implementations.
2. **Energy.** Answering `q` independent queries over an answer set of size `S` needs
   `q·log₂S` bits *somewhere*. Working RAM is O(1) by R2, so the bits are not there; they are in an
   addressable store. That is allowed — but then the primitive is `state + store`, and every claim
   about "zero growth" must be made about **working state**, never about the universe.
**Evidence:** `bench/RESULTS.md` §A. 16 bits collide at 65,536 tokens; 32 bits at 4.3e9; 64 bits at
1.8e19. 10⁶ tokens × 10³ queries × 50k answers = 1.5e7 bits = 1.9 MiB that has to live somewhere.
**What a candidate inherits if it reuses this:** if a proposal says "bounded state, exact recall over
an unbounded stream" without saying *where the bits are*, it is either wrong or it has an O(n) store
it is not admitting to. The tell is always G4: bytes read per generated token.
**Escape condition:** declare `bounded working state + external store` up front (CHARTER §1.1) and
let G2/G3/G4 be the claim. There is no escape from the wall itself — only an honest relocation of
where the information lives.
