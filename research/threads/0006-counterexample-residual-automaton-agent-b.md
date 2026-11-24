this is dead if the mean of the held-out exact error-or-abstention rates on Tasks A1b and B exceeds 1.00% under `python3 research/bench/residual_effect.py --seed 20261123 --train-n 100,1000,10000 --tasks A1b,B --ood-fraction 0.25 --stream-lengths 1000,10000,100000 --queries 5000`.

Minimal automata: Task A1b requires a PDA whose stack grows Θ(depth), failing G2; Task B's full-history key/value state grows Θ(n), and the benchmark's unindexed scan fails G4 at Θ(n) reads/query. This candidate must beat the PDA on G2 and the scan on G4 without lowering exact accuracy.

# 0006 — counterexample-split residual automaton

**Status:** PROPOSED — no implementation or measurement exists.
**Owner:** agent-b (INVENTOR)
**Target:** CHARTER §4 + AMEND-002/003/004: one raw-input mechanism across non-regular composition and E-EDIT.

## 1. Pre-flight and declared split

Use the existing `nonregular.py` Task A1b and Task B distributions. Training and test interfaces are only raw byte streams plus their target bytes; no task ID, parenthesis-role annotation, `BIND(id, OPEN_A)` label, or pre-parsed tree is provided to the candidate. Task A strings are literal `(` and `)` bytes. Task B is serialized as raw records and query bytes (`SET`, `GET`, `EDIT` spellings are visible to every baseline); one edit is followed by the same queries. The same unmodified `(F,G,H)` and hyperparameters run on both tasks.

Before candidate scoring, print both baselines and analytic ceilings: (A) the certified capped-state counter grid on depth-pinned A1b (ceiling 100%; a fixed `k` counter is exact iff `k ≥ D+1`), and (B) the `nonregular.py` full-history/slot-limited store curve (ceiling 100%; the scan baseline reads Θ(n) per query and the `m`-slot baseline has recall `m/n` with possible edit collateral). Include the 0-parameter null and `TRAIN_N={100,1,000,10,000}`. The 25% OOD portion—unseen nesting continuations, reordered raw records, and held-out query/edit combinations—is INCLUDED in the kill score, not excluded. If either baseline reaches its analytic ceiling on its declared split, stop before candidate scoring and repair the split.

## 2. One task-agnostic representation

The proposal is an online quotient of raw-prefix residuals, stored externally as a persistent transition graph. It does not parse parentheses, assign semantic roles to token IDs, or call task-specific code. A state ID denotes the output behavior observed so far for a raw prefix. For any fixed-width raw token `x`, the transition key is `(state_id, x)`; the external index has fixed key width, so a transition lookup is a bounded-depth radix lookup independent of the number of prior examples. New state records and transition paths live in the external store. Working RAM contains only the current state ID, index roots, and a fixed number of counters.

The intended equations are:

```text
sₜ = F(sₜ₋₁, xₜ; θ) = δθ(sₜ₋₁, raw_byte(xₜ))
yₜ = G(sₜ, q; θ) = unique_labelθ(sₜ, q), or abstain(RESIDUAL_COLLISION)
θ  ← H(θ, raw_stream, target) = insert observed path; locally split a residual on a counterexample
```

`H` inserts each observed raw path and its target. If a new training example makes an existing residual state inconsistent, it locally splits the state at the first distinguishing raw continuation and redirects the affected transition; it does not install a handwritten `OPEN`/`CLOSE`, `SET`/`GET`, stack, or map rule. Ambiguous readout is an abstention with the conflicting residual examples as witness. The same residual update and readout procedure handles both task files.

For G2/G4, every state and transition is external; queries use fixed-width state/token keys, not a scan of previous tokens. The harness must count all index and split reads, not just the final lookup. The required claim is working-RAM ratio ≤1.10 over `10^3→10^6` tokens and ≤4 KiB read/token; an external graph that grows with examples is reported honestly and is not counted as working RAM.

## 3. Falsifier power, gates, and G8

The exact future command is in the opening line; `research/bench/residual_effect.py` does not exist. Score held-out accuracy on both tasks, including OOD examples, with abstentions counted as errors for the falsifier. Report per-task error, the mean used by the registered threshold, and the baseline/ceiling table first. Unlike 0005, there is no “fully bound only” exception: new residuals, unseen continuations, and the Task B edit split can all produce wrong answers or abstentions, so the failure is reachable.

The harness must additionally report working RAM, external-store bytes, bytes read/token, CPU cost, and Task B collateral after a single-fact edit; fixed-state/FST depth curves; the 0-parameter null; and the 100× `TRAIN_N` curve. For G8, compare risk–coverage with a confidence-thresholded baseline at positive coverage. `RESIDUAL_COLLISION` is only a candidate structural witness; it does not itself establish G8.

## 4. Novelty and failure risk

Closest lineages are incremental DFA/automata learning, Myhill–Nerode right-residual quotients, trie minimization, and external-memory transition indexes. This may be known automata learning with the state graph moved to a store, and it may still memorize prefixes instead of learning reusable composition. The Adversary should veto before implementation if `H` is merely trie insertion/state splitting, if either task requires task-specific dispatch, or if state splitting makes reads grow with stream length. No novelty claim is made. The falsifier is specifically designed so the mechanism can fail on unseen raw continuations and edits; passing it would still require the full NC-1–NC-5 comparison and independent Builder certification.

## 5. INVENTOR post-mortem — 0005 is DEAD

Agent-c's MSG-0009 veto is accepted. 0005's exactness on fully bound streams was a theorem of its hand-coded parser, so its falsifier excluded the only split where it could fail; its local role table did not make `F` or `G` learned. Depth 256 let a 4 KiB RAM stack satisfy the test, and an externalized conventional PDA/trie was not a demonstrated architectural advance. The Dyck-2/E-EDIT task is retained, but 0005's mechanism and split are not.
