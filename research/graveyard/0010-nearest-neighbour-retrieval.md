# Nearest-neighbour retrieval as "bounded state + store"
**Status:** DEAD on G4 and on G8, in opposite directions
**Failed because:** retrieval returns `argmax_sim(q, items)`, not the item. Two mechanisms, one per
gate:
1. **G8 fails.** Similarity has no "no basis" region. An out-of-distribution query still has a
   nearest neighbour, and it is returned at full confidence — the argmax is a continuous function of
   the query with no reject option. This is the same defect as softmax over logits: the space is
   total, so there is no input on which the system has no opinion. Every "RAG with a nicer index"
   proposal inherits it, and CHARTER §5 lists that family as a non-goal.
2. **G4 fails.** Cost per token is an O(n) scan or an O(log n) index traversal, and the index is O(n)
   state. "Constant RAM" is true and irrelevant: the reads are what the charter measures, and the
   reads grow. A hierarchical index (IVF, HNSW) reduces the constant and adds a *training-time*
   structure that must be rebuilt as the store grows — which is a cache with a build step.
**Evidence:** the argmax construction; `bench/RESULTS.md` §C is the same accounting with the store
relabelled. There is no measured table here because the argument is structural: an argmax over a
finite set is total on its domain, so 0 wrong on unattemptable inputs is unreachable by
construction, not by tuning.
**What a candidate inherits if it reuses this:** any candidate whose readout is "find the closest
stored thing". It will fail G8 in the confident-wrong direction (worse than abstaining) and G4 in the
O(n) direction. If it also claims exact recall, note that exactness here means *the nearest item is
the right item*, which is a statement about the embedding, not about the mechanism.
**Escape condition:** a calibrated reject region requires a density or a margin, and a density over
an O(n) store is another O(n) structure. So the repair costs what the cache costs. This is why the
charter's "bounded working state + addressable store" is the *only* framing that survives: it admits
the store, and then the honest question is reads per token, not RAM.
