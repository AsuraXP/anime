# Fast weights / linear attention / "state as a sum of outer products"
**Status:** DEAD-AT-SCALE (capacity O(D), silent at the operating point)
**Failed because:** the state update `Wₜ = Wₜ₋₁ + vₜkₜᵀ` is a linear associative memory in recurrence
clothing, and it inherits `0003-dense-associative-memory-capacity.md` exactly. Two mechanisms make
it worse than the static case:
1. **No "do not disturb" direction.** A rank-1 write perturbs *every* previous read at once, because
   `Wkⱼ` changes by `v(kⱼ·kₜ)` for all j. There is no way to write item t without moving items 1..t-1.
   The delta rule fixes this by writing the *residual* instead of the value — and that costs an
   O(k) read of prior content per write, i.e. exactly the O(n) per-token read that G4 forbids.
2. **Keys are learned, not chosen.** Exact recall requires `q·kᵢ ≈ δᵢⱼ`, i.e. near-orthogonal keys.
   A gradient can push observed keys apart, but it cannot push apart a key it will meet *after*
   training. So the interference floor is set by the key distribution at test time, which the model
   does not control.
**Evidence:** literature and our own §B wall — the capacity of a D-dimensional linear associative
memory is O(D) patterns at exact recovery, and the measured cliff is 81.2% at load 0.125 to 0.3% at
0.375. Fast-weight papers report the same shape: near-perfect inside the trained length, monotone
degradation beyond it. The degradation is usually plotted as "length generalisation", which is the
same number under a kinder name.
**What a candidate inherits if it reuses this:** any "O(1) state, no cache" recurrence whose state is
a matrix or a set of slots updated additively. It will look excellent on sequences at or below the
training length and fail monotonically beyond it, and the failure will be *smooth*, which makes it
read as a capability rather than a wall. This is the family most likely to be mistaken for a
survivor.
**Escape condition:** none inside one additive matrix. The two known repairs — delta-rule writes and
sparse/orthogonal keys — each reintroduce either O(k) reads or an external cleanup structure. Report
length-generalisation curves at 1×, 3×, 10× the trained length *before* claiming the state is
bounded; a flat curve at 1× is not a result.
