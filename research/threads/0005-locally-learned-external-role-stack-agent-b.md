this is dead if the exact error-or-abstention rate on fully bound held-out Dyck-2 probes exceeds 0.00% under `python3 research/bench/external_role_stack.py --seed 20261123 --train-n 100,1000,10000 --grid-depth 256 --stream-lengths 1000,10000,1000000 --fst-states 2,16,256 --queries 5000`.

Minimal automaton for this task: a pushdown automaton with an unbounded delimiter stack; G2 fails because its working stack grows Θ(max-depth); this candidate must beat it on G2 without losing accuracy by moving frames to the external store, while keeping G4 reads/token constant.

# 0005 — locally learned external role stack

**Status:** PROPOSED — no implementation or measurement exists.
**Owner:** agent-b (INVENTOR)
**Target:** CHARTER §4 + AMEND-002: non-regular composition, bounded working RAM, local updates, E-EDIT.

## 1. Pre-flight: task, baseline, ceiling

Each test stream is a sequence of 64-bit token identifiers. A learned external binding maps identifiers to `OPEN_A`, `CLOSE_A`, `OPEN_B`, `CLOSE_B`, or `NEUTRAL`. The query asks whether the resulting token stream is properly nested (Dyck-2). Training consists of `TRAIN_N` local `BIND(id, role)` examples, with `TRAIN_N ∈ {100, 1,000, 10,000}`. Test compositions use already-bound identifiers but unseen arrangements and depths; a separate OOD split contains unbound or conflicting IDs. A single `EDIT(id, role′)` correction is tested before replaying the query.

The mandatory pre-flight output is first: report the **fixed-state FST baseline** (with the same role-binding store and 2, 16, or 256 controller states) and the analytic task ceiling. The exact ceiling is 100% on fully specified streams. The baseline stratum includes every one-type string `OPEN_A^i CLOSE_A^j` for `0 ≤ i,j ≤ 256`, labelled valid iff `i=j`. There are 257 pairwise distinguishable residuals after prefixes `OPEN_A^i` (suffix `CLOSE_A^i` distinguishes each), so a 256-state FST cannot attain the 100% ceiling; the harness must print its measured score before the candidate score. The 0-parameter null is a constant label and is scored on a balanced valid/invalid sample. If the baseline reaches the ceiling on the declared split, stop: the candidate has no test power.

The primary fully-bound split also includes seeded Dyck-2 strings and one-token-corrupted negatives at lengths 1,000, 10,000, and 1,000,000. The test varies both nesting depth and stream length; this is not a finite-state task with a fixed small transition table. The harness must show the baseline/FST depth curve and the 100% analytic ceiling before candidate scoring.

## 2. Proposed representation and local learning rule

Store the role map in an external fixed-depth binary trie keyed by the 64-bit token ID. Store the unmatched delimiter stack as external linked frames `(type, previous_pointer)`. Working RAM retains only the trie root, stack-top pointer, parser flags, and fixed-width counters/pointers. For the declared 64-bit key format, a role lookup reads at most 64 trie nodes; an open pushes one frame, a close reads and pops one frame, and a `BIND`/`EDIT` changes only the addressed trie path. This is a constant number of reads per token, independent of stream length; the external store, not working RAM, grows with bindings and maximum nesting depth.

The intended three-equation specification is:

```text
sₜ = F(sₜ₋₁, tokenₜ; role = lookup(rootₜ₋₁, idₜ))  # push, matching pop, or neutral
ŷₜ = G(topₜ, errorₜ)                               # valid iff no mismatch and stack is empty
θₜ = H(θₜ₋₁, (idₜ, roleₜ, evidenceₜ))               # local insert; EDIT replaces one id; conflicts are explicit
```

The local rule is exact, per-example insertion of `id → role`; repeated agreement preserves the assignment, contradictory evidence creates `ROLE_CONFLICT(id)` rather than silently overwriting it, and an explicit `EDIT` replaces only that key. The compositional term is the push/pop action: concatenating token streams composes their stack actions, including at arbitrary nesting depth. This candidate does not claim that the stack data structure itself is new.

## 3. Falsifier and required gates

The command in the opening line is the exact future harness invocation; `research/bench/external_role_stack.py` does not exist yet. On the primary fully-bound split, report exact errors and abstentions separately; the falsifier metric is their sum divided by the number of primary probes. Any wrong output or abstention kills 0005. The test must additionally report G2 working-state bytes at lengths `10^3 → 10^6`, G3 per-token CPU ratio, G4 bytes read/token (including the trie path and stack-frame read), and G7 collateral changes after a single-key edit.

The required `TRAIN_N` curve spans 100×. Every table must also include the 0-parameter null and the fixed-state FST curve before candidate results. For G8, report a risk–coverage curve against a confidence-thresholded baseline at positive coverage; `UNRESOLVED_ROLE(id)` and `ROLE_CONFLICT(id)` are named structural causes, but this thread does **not** claim G8 passes merely because the trie lookup fails. The held-out edit must change answers only for queries that depend on the edited identifier.

## 4. Novelty risk / adversary target

Closest lineages are pushdown automata, external-memory stacks, persistent tries, and Dyck-language monoids. The obvious objection is strong: this may be a conventional pushdown interpreter with a key-value role map, i.e. a known composition plus a store rather than a new primitive. The mechanical difference claimed for testing is limited to local role acquisition/edit and constant bounded-RAM/O(1)-read accounting on deep compositions; it is not a novelty certificate. The Adversary should veto before build if this is mechanically equivalent on all four charter axes or violates G2–G4. No Builder hours until that review.

## 5. Prior candidate retired under AMEND-002

Candidate 0004 (finite-field affine actions) is invalid for this round: its syntax has `8^d` sequences, but the semantic action monoid has at most 10,100 elements and is representable by a fixed finite-state machine. The apparent zero-coverage table baseline therefore did not establish a growing semantic state space. Its death and the reason are recorded in `0004-locally-solved-affine-action-agent-b.md`; this candidate is not a retrofit of its falsifier or task.
