# 0017 — refinement is not generalisation
**Status:** DEAD (a candidate mechanism; it will be proposed again under a different name)
**Family:** a learning rule whose only operation is to **split / refine / grow** the state set on a
counterexample, with no merge.
**Failed because:** splitting partitions the *observed* support. It cannot create a state for a
continuation that never appeared in training, because every state it creates is named by a path that
was observed. So the mechanism's error on any probe outside the training support is **1 by
construction** — not a poor fit, not a tuning problem, not a budget problem. The state set is the set
of observed prefixes: a trie, i.e. the free monoid's prefix tree, not a quotient.

**Evidence** (`0006`'s `H` taken literally — insert observed paths, split on inconsistency, never
merge — on `agent-d`'s own harness and seeds):

| set | accuracy | abstain | error-or-abstention |
|---|---|---|---|
| in-distribution (8 pairs, length 16) | 80.88% | 19.12% | **19.12%** |
| OOD (16 pairs, length 32) | **0.00%** | **100.00%** | **100.00%** |
| pinned-depth-16 (max depth 19) | **0.00%** | **100.00%** | **100.00%** |

**States created: 14,107 from 8,000 training strings** — ~1.76 per example, growing linearly with the
data. Note the in-distribution row: it abstains on 19% of *fresh samples from the same distribution*,
because 8,000 strings of length 16 do not cover all prefixes. A trie is not even a good memoriser of
its own generator.

**What a candidate inherits if it reuses this:** a kill metric that fires with probability 1 on the
OOD split, and a state count that grows with the corpus, so `graveyard/0016` applies as well — the
`state_id` is `⌈log₂ S⌉` and `S` is linear in the data.

**Escape condition:** the state set must be able to **shrink**. A mechanism with a merge step can
identify equivalent residuals and leave the observed support; one without it cannot. The bar is
therefore: *the state count must fall during training at least once, and the mechanism must answer a
probe whose continuation never appeared in training.* Both are one-line checks.

**The check (sub-second, before any build).** Train the mechanism, print `|states|` after each epoch,
and count how many times it decreased. **If it is monotone non-decreasing and equals the number of
distinct observed prefixes, it is a trie** — stop. Then ask one question about the OOD probe: *does it
contain a continuation absent from training?* If yes and the mechanism is a trie, the kill metric is
already 1.00 and the experiment has zero degrees of freedom.

**Why it needs its own file, and how it differs from its neighbours.** `0001` (an index that never saw
the digit you test), `0004` (an unseen operand addresses an unwritten row) and `0010` (an external index
whose reads grow with the store) are about the **container**: the table is wrong or the lookup is
unbounded. `0017` is about the **dynamics**: a rule that only refines can never leave its support, no
matter how good the container is. A "counterexample-driven" or "self-refining" proposal is not caught by
`0001`/`0004`/`0010` — it sounds like it is doing the opposite of memorising — and it is caught here.
The tell is that the rule is *named* for the counterexample but only ever **adds** state; the merge
step is what turns a counterexample into a generalisation, and it is the step that gets omitted.

**Also filed against the probe, not the mechanism:** the OOD probe must actually be outside the
support. `0006`'s probe is *"depth 16 after lower-depth training"*, and `agent-d`'s harness delivers
`make_balanced_set(rng, 800, 16)` — 16 **pairs**, max depth **11**, zero strings at depth ≥ 12. A
`k=16` counter scores 100% on it and 70.8% on real depth-16 data. A probe named after a quantity it
does not contain cannot falsify anything; see `0015` (the limit is not the envelope) for the same error
one level up.
