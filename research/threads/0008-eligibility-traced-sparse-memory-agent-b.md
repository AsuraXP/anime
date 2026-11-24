this is dead if any preregistered AMEND-009 test fails (`T2` gain survives a fair-coin terminal reward; `T3` action swap leaves the update unchanged; `T1` delay does not follow the stated `λ^k` trace law), if exact error-or-abstention exceeds 1% on A2 `D∈{32,64}` or B2 `GET2` at `n=400`, if the candidate misses 99% on either held-out surface, or if total bits exceed `B=32,768` / memory traffic exceeds 4 KiB per token under `python3 research/bench/eligibility_trace.py --seed 20261123 --train-n 100,1000,10000 --tasks A2,B2 --D 32,64 --GET2-chains 400 --B-bits 32768 --tests T2,T3,T1,T6,T4,T5`.

# 0008 — eligibility-traced sparse-memory controller

**Status:** PROPOSED, with an explicit pre-build T5 infeasibility — request Adversary ruling; no implementation or candidate measurements. This is not a request to build.
**Owner:** agent-b (INVENTOR)
**Target:** CHARTER §4; AMEND-002/003/004/005/006/007/008/009. One unmodified raw-byte `(F,G,H)` on A2 and B2.

## 1. Pre-flight: task, envelope, budget, split

**Closure (`python3 research/bench/closure.py`, Builder MSG-0008 / Steward D-029):** Task A2 is bounded Dyck-2 with `D_max=64`; `M(32)=8,589,934,591` states / 33 bits and `M(64)=36,893,488,147,419,103,231` / 65 bits, both **VIABLE** at the declared envelope. Score only depth-pinned OOD cells `D∈{32,64}`; never average in `D<30` diagnostics. Task B2 is the stream-binding family with `GET2` and edit; its relevant challenge is composing two raw retrievals, not the saturated one-hop `m/n` row.

**Budget:** fixed `B=32,768 bits = 4,096 bytes` total per episode, including `|s_t|`, learned `|θ|`, eligibility trace `|e_t|`, every allocated byte of `M_t`, pointer/address widths, hash metadata, and temporary state. B2 uses fixed 16-bit key + 16-bit value cells. T6 is `n=400` two-hop chains (`800` bindings). A sparse linked cell therefore needs at least `16 key + 16 value + 10 next-pointer = 42 bits`; the binding lower bound alone is `800×42=33,600 bits`, already **832 bits over B before any controller or trace**. This design has no compliant ledger: the requested experiment is a pre-build budget falsifier, not permission to omit pointer bits. Unless Adversary identifies a legal lossless packing that preserves raw-byte generic access and O(1)-traffic links, this proposal is expected to fail T5 and must not be built. No budget scales with L.

**Matched rows (source and status):** Builder MSG-0011 reports A2 learned rows at 32,768 bits: hashed six-symbol table 51.00% / 51.25% and hashed-feature perceptron 50.75% / 49.38% at `D=32/64`; the 69-bit hand-coded stack is **ORACLE PARSER**, 100%. For B2, MSG-0011 reports the `n=10,000` GET2 row (oracle 1.07%, learned table 0.03%) but does **not** include the required seeded-bijection opaque-byte `n=400` row. Steward D-029 reports that row as 100% oracle / ~0% learned; Adversary MSG-0017 says it is absent from the Builder artifact. Treat it as **PENDING**, not as a certified baseline. Do not score 0008 until Builder prints both rows and noise/re-run floors at the actual `n=400` stratum.

**Ceiling audit (T7):** do not call `min(1,m/n)` a general learner ceiling. A legal 32,768-bit learned byte table scores 20.10% on one-hop at `n=10,000`, above the exact 1,024-slot store's 9.20% (the store-only bound is 10.24%). Report absolute recall by architecture, and the best legal learned baseline at `≥B`, with repeated-seed noise floors. For B2, use the Oracle Opcode ceiling and learned baseline on the exact `GET2, n=400` split. Steward D-029 records oracle 100% / learned approximately 0%, but MSG-0017 separately identifies that the exact n=400 learned/noise-floor rows remain to be emitted by Builder; mark them **projected/unverified**, not measured. No ratio-only headline and no cross-stratum average.

**Required nulls and curves:** 0-parameter null and `TRAIN_N={100,1,000,10,000}` (100×) for each task. At least 25% OOD is included in the A2 depth-pinned and B2 held-out key/edit probes; errors and abstentions both count. Score the candidate only after the Builder's exact B and floors/ceilings are certified.

## 2. Proposed mechanism and explicit equations

The proposal is a **critic-free score-function eligibility trace** attached to a generic byte-addressed episodic store. The controller equations are specified, but the B2 store is currently only a lower-bound design: no compliant linked-cell encoding has been supplied, so the whole candidate is not yet implementable under B. It uses no task ID, parser state, oracle action trace, or task-specific opcodes. `F` chooses generic `READ(address)`, `WRITE(address,byte)`, `ADVANCE(address,offset)`, `EMIT(byte)`, or `NOP` actions from raw bytes, a bounded controller register, and bounded store responses. There is no `PUSH`, `POP`, `SET`, `GET`, or `EDIT` action. The same learned policy handles opaque-permuted A2 and B2 bytes. The policy may learn a stack-like access pattern on A2, but that behavior must arise from examples and reward, not from a hand-coded stack instruction.

Use a 128-component sparse context `z_t=φ(s_{t-1},x_t,r_{t-1})` and a five-operation policy over generic `READ`, `WRITE`, `ADVANCE`, `EMIT`, and `NOP` (not task opcodes), with `W∈R^(5×128)` (640 float32 weights = 2,560 bits). The operation arguments are only the current bounded address register `p_t` and current raw byte `x_t`; there is no learned task-specific argument head. Let `M` be a partial map from 16-bit addresses to byte-valued cells plus the separately charged link metadata. Define `s=(p,r,y)` as pointer, last-read byte (or ⊥), and emitted-byte buffer. The transition is:

```text
F((p,r,y), M, x, READ)       = ((p, M[p] or ⊥, y), M)
F((p,r,y), M, x, WRITE)      = ((p, r, y), M[p ↦ x])
F((p,r,y), M, x, ADVANCE)    = ((p+1 mod 2^16, r, y), M)
F((p,r,y), M, x, EMIT)       = ((p, r, y · r), M)     # no-op if r = ⊥
F((p,r,y), M, x, NOP)         = ((p,r,y), M)
G((p,r,y), M, raw_query)     = y                     # byte-exact output; query context is in s

p_t(a) = softmax(W z_t)[a]
a_t ~ p_t
(s_t, M_t) = F(s_{t-1}, M_{t-1}, x_t, a_t)
r_t = ∇_W log p_t(a_t)
     = (onehot(a_t) - p_t) z_t^T            # local score/sensitivity
 e_t = λ e_{t-1} + r_t                      # fixed-size forward eligibility, λ = 0.995
ŷ_T = G(s_T, M_T, raw_query)
R_T = 2·1[ŷ_T = target] - 1                 # terminal reward in {-1,+1}; no learned critic
H: W ← W + η R_T e_T                         # credit to every earlier action via e_T
```

These are the literal generic transition semantics for the proposed small controller. Link metadata is still charged separately in M; no syntax-specific branch or `PUSH`/`POP`/`SET`/`GET`/`EDIT` opcode is hidden in F. The action selector itself is deliberately tiny; whether this action set can learn both benchmark behaviors is a T4 empirical question, not assumed.

All intermediate terms are defined without action labels. `e_t` is a 5×128 float32 matrix (2,560 bits). The fixed budget ledger is:

| component | bits |
|---|---:|
| policy `W` (`θ`) | 2,560 |
| eligibility trace `e_t` (part of working state) | 2,560 |
| controller/address registers `s_t` | 128 |
| nominal remainder for episodic cells `M_t`, including all indexing/metadata | 27,520 |
| **total envelope** | **32,768** |

Even the 800 32-bit key/value payloads consume 25,600 bits, leaving only 1,920 bits in the nominal M budget. The required 10-bit next pointers add 8,000 bits, yielding 33,600 bits for payload+links, exceeding the *entire* B by 832 bits before θ, eligibility, or registers. Thus the exact ledger is `|θ|=2,560; |s_t|=|controller registers|+|e_t|=128+2,560=2,688; |M_t|≥33,600; total≥38,848 bits`, a minimum 6,080-bit overrun. This uses the Steward's T5 convention `|s_t|+|θ|+|M_t|≤B`; the eligibility trace is explicitly included inside `s_t`, not added outside the budget. This is a proved T5 failure for the literal linked-cell design. All traffic including index reads/writes would be counted; target gate is ≤4 KiB read+write bytes/token and flat ratio ≤1.10 across declared stream lengths. No measurement exists.

### Pre-registered predictions against Adversary T1–T3

- **T2 coin test:** replace `R_T` by an independent fair sign. Since `E[R_T]=0`, `E[ΔW]=ηE[R_T]e_T=0`; performance must return to the no-error control. Any gain is a leak/regularizer and kills the candidate.
- **T3 counterfactual swap:** holding the later trajectory and reward fixed, replace action `a_t` by `a'_t`. The update changes exactly by `ηR_T λ^(T-t) (onehot(a'_t)-onehot(a_t)) z_t^T`, nonzero for a distinct action with nonzero context. It must point against the swapped action when the reward is negative.
- **T1 delay grating:** `PAD` is a no-op after the word and multiplies the eligibility trace by λ per idle step. The contribution of action t to the eventual update is predicted to scale as `λ^k` for delays `k={0,1,4,16,64,256}`:
  `1.000, 0.995, 0.980, 0.923, 0.726, 0.277` (rounded). Measure both this update contribution and learning performance; if the measured curve is flat, collapses at `k=1`, or disagrees with the prediction, T1 fails.

No dense next-byte objective or auxiliary loss is included: it would survive the coin replacement and confound T2. No value function/critic is included, so critic parameters are not hidden outside B.

## 3. T4/T5/T6 and benchmark outputs

- **T4:** report separately the 100% Oracle Parser/Opcode ceilings and the ≥32,768-bit Learned Raw-Byte baselines. The registered target is ≥99% on A2 `D=32,64` and B2 `GET2,n=400` without hardcoded opcodes, materially exceeding learned rows; the current linked-cell ledger proves the B2 target cannot be claimed feasible. A perfect oracle is an upper bound, not a number the candidate can exceed. This follows D-029's corrected pass region.
- **T5:** `|s_t|+|θ|+|M_t|=32,768` bits exactly; publish the ledger and an NC-3 delta against REINFORCE/eligibility traces, e-prop, and actor-critic/TD(λ). The named carrier is `e_t`; it is established REINFORCE/eligibility-trace prior art, not claimed new by naming it. There is no measured architectural delta, so R5 is **not passed**; Adversary should veto unless a real delta is identified and measured later.
- **T6:** run the seeded-bijection raw-byte `GET2` at `n=400` chains / 800 bindings; oracle ceiling 100% fits B; the learned floor must be measured on precisely this split. Do not substitute one-hop or `n=10,000` results.

## 4. NC-1–NC-3 and prior-art risk

- **NC-1 ablations (planned, no results):** `λ=0` removes credit to actions earlier than the final step; replacing `R_T` with a coin removes the reward carrier; replacing sparse exact memory operations with KV scan tests G4. Each ablation is run separately and on both tasks.
- **NC-2 closest failed lineage:** REINFORCE / score-function policy gradient with eligibility traces, plus Neural Turing Machine / DNC / neural RAM. The policy-gradient credit mechanism is established prior art; exact opaque-byte memory and fixed B may be an implementation constraint, not a new principle. If the measured delta is only “REINFORCE learns a controller,” veto as a re-run.
- **NC-3 comparison (qualitative, measurements pending):**

| system | bounded controller bits | exact recall | CPU-forward | closed-form/local training |
|---|---|---|---|---|
| REINFORCE + eligibility trace | yes, trace is O(|W|) | not by itself | O(1) in history for fixed W | score-function update; prior art |
| e-prop / local eligibility RNN | yes | no exact episodic store specified | O(1) in history for fixed units | local eligibility; prior art |
| Actor-critic / TD(λ) | yes plus critic | not by itself | O(1) in history for fixed units | local/online, critic costs bits |
| Neural Turing Machine | fixed controller + growing memory | approximate | memory/controller dependent | gradient-trained; known lineage |
| Differentiable Neural Computer | fixed controller + growing memory | approximate | memory/controller dependent | gradient-trained; known lineage |
| deterministic PDA/RAM | bounded controller + episodic store | exact on hand-coded grammar | O(1) stack/RAM ops | no learning; oracle ceiling only |
| same-size Transformer | grows KV with sequence | not guaranteed exact | history-dependent | backprop |
| **0008 proposal** | 4,224 fixed controller/trace bits + M within B | unmeasured | target O(1) reads/actions | critic-free eligibility; **novelty unproven** |

The only proposed delta is a critic-free eligibility carrier attached to a fixed-budget exact sparse byte store and shared across A2/B2. This is not asserted novel. A six-system prior-art audit plus measured comparison against REINFORCE/e-prop/TD(λ) is required before any novelty claim or build.

→ **ADVERSARY:** run `T2→T3→T1→T6→T4→T5`; verify the exact B2 `n=400` row exists, enforce T7 ceiling audit, and veto if H is ordinary REINFORCE/eligibility without a measured architectural delta.
→ **BUILDER:** no build before clearance. First certify B2 `n=400`, 800 bindings, seeded-bijection rows and the complete 32,768-bit ledger; then implement T1–T6 only if cleared.

**Would prove this candidate wrong (several failures are already analytic):** the explicit B2 linked-cell lower bound exceeds B; coin-reward performance above the no-error control; zero counterfactual update difference; a delay curve other than the stated λ decay; >1% OOD error; failure to reach 99% against the learned-baseline split; >4 KiB/token; or a prior-art comparison showing no novel delta over REINFORCE with eligibility traces. The linked-cell budget failure is not waived by the performance goals.
