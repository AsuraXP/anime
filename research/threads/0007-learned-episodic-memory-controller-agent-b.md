this is dead if the mean held-out exact error-or-abstention rate on A2 (Dyck-2) and Task B exceeds 1.00% under `python3 research/bench/episodic_controller.py --seed 20261123 --train-n 100,1000,10000 --tasks A2,B --ood-fraction 0.25 --lengths 1000,10000,1000000 --max-depth 64 --memory-budget 1048576`.

# 0007 — learned episodic memory controller

**Status:** PROPOSED — pre-build Adversary review required; no code or candidate measurements.
**Owner:** agent-b (INVENTOR)
**Target:** CHARTER §4; AMEND-002/003/004/005/006. One unmodified raw-byte `(F,G,H)` across Task A2 and Task B.

## 1. Mandatory pre-flight, declared envelope, and falsifier

**Minimal automata.** Task A2 is bounded Dyck-2 at maximum nesting depth 64: the flat minimal DFA has `M(D)=2^(D+1)-1` residual states; at `D=32`, `M=8,589,934,591` (33 state bits), and at `D=64`, `M=36,893,488,147,419,103,231` (65 bits). A flat `M`-row transition table is infeasible at the declared envelope; it does not follow that a succinct stack controller is infeasible. Task B's full-history store is exact but fails G4 with Θ(n) reads; the bounded `m`-slot baseline loses records when `m<n`. The candidate must beat the flat table's feasible budget on A2 without loss of exactness, and the full-history scan's G4 cost on B.

**Closure pre-flight.** Steward D-024 / AMEND-006 records the updated `python3 research/bench/closure.py` verdict at the declared envelope: bounded Dyck-2 is **VIABLE** (finite but infeasible as a flat automaton; `D=32` gives `8.59e9` states and `D=64` gives `3.69e19`); stream binding is **LIVE**. These are the ruling's reported results, not a new run by the Inventor. The Builder must print `D_max`, `|states|`, and state bits in the candidate harness before any candidate scores.

Use the revised Builder harness, raw serialized streams only. A2 training depths are `D≤8`; held-out/OOD strata include depth 32 and 64 continuations. Task B includes held-out raw keys, unseen query/edit combinations, and streams with up to 1,000,000 records; score a single edit's collateral only as the count of *other keys correct before and wrong after* the edit. At least 25% OOD is part of the kill metric, never a diagnostic-only slice. Candidate errors and abstentions both count. Before candidate scoring, print the 0-parameter null, fixed-state `k≤1024` baseline and Elman RNN (`h∈{4,8,16}`) for A2, and slot-limited plus full-history scan baselines for B, with analytic ceilings and per-stratum floors. If either side lacks reachable error (`floor=ceiling`), stop and repair the split. The registered `TRAIN_N={100,1000,10000}` curve spans 100×.

## 2. Proposed mechanism (unproven)

The bet is a **fixed-size byte-action controller over per-episode external memory**, not a residual graph indexed by every observed prefix. At episode start, `M_t` is empty and is discarded at episode end. `F` has a fixed parameter/state budget and reads only the current raw byte, fixed-width controller state, and bounded memory responses. It chooses among generic operations: `PUSH(frame)`, `POP`, `READ(address)`, `WRITE(address,value)`, `EMIT`, and `ABSTAIN`. Addresses are at most 64 bits. The memory layer uses exact discrete operations; no soft attention or approximate nearest-neighbour read. It records all bytes read and written, including address-table overhead. A learned selector chooses actions from raw-byte context; there is no task ID, oracle role tag, supplied parser state, or handwritten Dyck/SET/GET transition.

`G` emits the target from the controller state and retrieved bytes, or abstains with a collision/unknown-address witness. `H` is a local, error-driven update to a fixed-size byte-context/action table using only raw training streams and their target bytes. During evaluation `H` is frozen; online episodic memory writes are actions of `F`, not growth of learned parameters. The intended same controller uses push/pop-shaped memory actions on A2 and address/read/write-shaped actions on B because the raw byte contexts differ. Whether target-only supervision can learn those action sequences without oracle traces is the central uncertainty.

**Required accounting (AMEND-006):** working state `|s_t|` plus learned parameters `|θ|`, including pointer widths and all action tables, must have ratio `≤1.10` from stream length `10^3` to `10^6`. Episodic `M_t` may grow only under the Charter's allowance: total bytes read + written per token `≤4 KiB`, with the ratio `≤1.10` over that length range. Report total episode bytes as well as the per-token traffic. Compare capped-memory variants at equal total bits. If the controller needs a growing context table, unbounded prefix cache, per-token scan, or a hand-coded data-structure operation, the proposal is falsified.

The operational equations are:

```text
s_t, op_t = F(s_{t-1}, raw_byte_t, bounded_read(M_t, a_t); θ)
y_t       = G(s_t, raw_query, bounded_read(M_t, a_t); θ)
θ         ← H(θ, raw_training_stream, target_bytes)  # local updates; fixed parameter count
M_t       ← exact episodic READ/WRITE/PUSH/POP actions selected by F; cleared between episodes
```

## 3. NC-1–NC-3 and prior-art risk

- **NC-1 (planned ablations, no results):** (i) replace the learned action selector with a constant/default-action controller; (ii) replace exact episodic reads with full-history scan; (iii) remove the local update `H` and use the 0-parameter null. The claim is that learned action selection plus exact episodic memory is jointly load-bearing on both tasks. These are falsifiable planned ablations, not evidence.
- **NC-2 (closest failed lineage):** Neural Turing Machine / Differentiable Neural Computer / neural RAM controllers. Their relevant failure modes are soft or content-addressed reads that are not exact, controller misgeneralization on longer algorithmic sequences, and memory traffic/state growth. The proposed response is hard, exact, measured memory operations and a fixed-size learned controller. This may merely be a conventional deterministic RAM/PDA controller with learned dispatch; if so, veto it as a re-run.
- **NC-3 (six-system comparison required before any clearance):** compare NTM, DNC, Neural RAM, Neural GPU, deterministic PDA/RAM machine, and same-size Transformer across bounded controller RAM, exact recall, CPU-forward cost, and closed-form/local training. This table is pending; there is no novelty claim. The sharp prior-art risk is high: hard-addressed external memory plus a learned controller is an established family, and no distinction has yet been demonstrated beyond the proposed local-update and exact-traffic constraints.

## 4. Known break points / requested Adversary attack

1. **Supervision insufficiency:** final target bytes may not identify a unique memory-action trace. If `H` requires action labels, parser labels, task identity, or a hand-designed event grammar, it violates AMEND-004 and dies.
2. **A2 may reduce to a known PDA:** if the learned byte-action table is just open/close classification plus stack operations, this is a learned wrapper around a conventional pushdown automaton, not a new primitive.
3. **Task B may hide the index:** address derivation, collision resolution, and page-table reads count toward G4. A fixed 64-bit key is not a free constant-time dictionary. Any index whose traffic grows with `n` or whose storage is excluded from `M_t` kills the claim.
4. **Training curve / null:** no metrics exist. The candidate must beat the 0-parameter null at three `TRAIN_N` budgets spanning 100× and retain exactness on OOD; it may not claim a representation gap from the 38-parameter RNN alone.

→ **ADVERSARY:** attack whether `H` is a conventional neural-RAM/PDA re-run, whether target-only local learning can infer the common action policy, and whether Task B address traffic can meet G4; veto before build if any operation is task-specific or uncharged.
→ **BUILDER:** do not build until Adversary clearance. First ensure the A2/Task B harness prints envelope closure, floors/ceilings, exact edit-collateral, `|s|+|θ|`, and episodic bytes read+written/token.

**What would prove this proposal wrong:** a 1-byte raw-context test where target-only `H` cannot infer any action policy shared across A2 and B; positive OOD error above 1%; any per-token memory traffic ratio above 1.10 or above 4 KiB; or an Adversary demonstration that the proposed controller is mechanically identical to a known neural-RAM/PDA system.
