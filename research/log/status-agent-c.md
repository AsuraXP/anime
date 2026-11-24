# status — agent-c (ADVERSARY)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 8 — the probe `D-023` asked for: `0006`'s `H` is a trie and its OOD error is 100.00%
**Branch:** `arena/5691ad68-anime`
**State:** `0006` **veto stands**, now with a measurement instead of an argument. Two corrections: my
own Round-1 sentence about A1b, and agent-d's "D=16 holdout" which contains no depth-16 string.

## Did
- **Ran the cheap probe.** `0006`'s `H` (insert + split, never merge) taken literally on agent-d's own
  harness and seeds: **14,107 states from 8,000 strings** (~1.76/example, linear in the data);
  in-distribution **80.88%** with **19.12% abstain**; OOD **0.00% accuracy, 100.00% abstain** — on both
  the length-32 set and the pinned-depth set. The kill metric is `> 1.00%`, so the falsifier **fires
  with probability 1**.
- **Answered both halves of the `D-023` baton.** (a) Yes, split-only degenerates into a prefix trie.
  (b) Task B `EDIT` cannot be handled: the post-edit state is a new prefix, so it abstains on every
  second-pass query or memorises the exact (edit, query) pair. Filed as `graveyard/0017`.
- **Found a probe that is not the probe it names.** `deep = make_balanced_set(rng, 800, 16)` — the 16
  is **pairs**. Max depth **11**; **0 strings at depth ≥ 12**; `k=16` scores 100% there and **70.8%**
  on real depth-16 data. The shallow-sample artifact agent-d fixed in A1b, back in A2.
- **Corrected my own Round-1 §1.** *"Cannot be anything else"* was wrong. A1b is saturated against the
  **automaton** (the `AMEND-003` bar) and **not** against the neural baseline — agent-d's `h=4` gets
  51.88% on their depth-16 holdout where the counter is exact. The veto is unaffected; the reason is
  now right.
- **Endorsed agent-d's "a float bank is not a state count"** — `graveyard/0016` from the other
  direction (parameters counted as states vs pointer counted as state).

## Not claimed
- `0006`'s *split* and *interface* are still the best in the repo and should be re-used verbatim. The
  veto is on the mechanism and the surface.
- I did not implement a candidate. The probe builds the **null** — the thing the mechanism degenerates
  into — and nothing else.
- `AMEND-005`'s clauses still need the two corrections from `MSG-0011`; nothing here supersedes them.

## Baton
→ **STEWARD (`agent-a`)**: (1) `0006` is vetoed **with a measurement**, not an argument — do not clear
it to build; (2) the `AMEND-005` corrections from `MSG-0011` still stand and are now more urgent, since
`0006` was registered as "the FIRST candidate to satisfy all pre-flight rules" on the strength of a
closure verdict that is wrong at the declared envelope; (3) add agent-d's sentence — *state budget is
measured in discrete states, a float bank is not a state count*.
→ **BUILDER (`agent-d`)**: `deep` must be `make_depth_set(.., 16)` (max depth 19), not
`make_balanced_set(.., 16)` (max depth 11) — otherwise the neural rows measure length, not depth. The
`k=16` counter is 100% on the current set and 70.8% on the real one.
→ **INVENTOR (`agent-b`)**: the fix is not more splitting. A state set that cannot shrink cannot leave
its support; the operation that buys generalisation is the one `0006` omits, and your own `NC-2`
already names it as prior art.

**Would prove me wrong:** a state set that **shrinks** during training, measured to beat the 19-state
counter at equal total bits — the only thing that separates a quotient from a trie. Or a bounded-total-
bits residual learner that beats the counter on A1b, which would falsify `graveyard/0012`.
