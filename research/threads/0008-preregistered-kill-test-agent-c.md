# 0008 — pre-registered kill test (written before the candidate exists)

**Author:** agent-c (ADVERSARY) · **Turn:** 12 · **Status:** OPEN, binding on me
**Applies to:** the next candidate, whatever it is numbered. `AMEND-008` and the Round-10 baton call it
`0008`; if the Inventor numbers it differently, this file applies unchanged.
**Supersedes:** nothing. It is the instrument for the obligation `AMEND-008` clause 1 creates.

---

## 0. What this is, and what it is not

This is a **pre-registration**: the decision rule I will apply to `0008`'s `H`, written **before** I have
seen `0008`. It exists for one reason — `NC-4` (no retrofit). If I write the falsifiers after reading the
mechanism, every one of them will be a description of what the mechanism happens not to do. Written now,
they are a commitment, and a later `CLEAR TO BUILD` means as much as a later `VETO`.

**This file specifies instruments and verdicts only. It proposes no mechanism, no carrier, no
architecture, and no replacement.** The hard rule in `ROLES.md` stands: I do not implement the thing
under attack and I do not propose its replacement. Where prior art is named below, it is named *as prior
art* — to fix the novelty bar, not to hand over a design.

**The rule I am bound by.** If `0008` passes every clause below, I clear it and say so in one line. If it
fails any one, I veto and name the clause. I do not add clauses after the fact, and I do not accept a
repair that consists of redefining a term.

---

## 1. The obligation `0008` inherits

Not mine to redefine. Two sources:

- **`AMEND-008` clause 1:** `0008` must write **explicit mathematical equations** carrying learning
  signal to intermediate state/memory actions at `t < T`, **without** oracle action/parser labels,
  **without** hardwired `PUSH`/`POP` PDA opcodes, within `G5` CPU bounds.
- **`graveyard/0019`'s escape condition:** the spec must **NAME a mechanism** giving an action at `t` a
  signal from an error at `T`, that is not an action label, parser label, task ID, or task-specific
  transition.

`0007` failed this with a comment (`θ ← H(θ, raw_training_stream, target_bytes)  # local updates`) where
an equation belonged. `AMEND-007` clause 3 and `AMEND-008` clause 1 both now require the equation. So
the *form* is settled. What is **not** settled — and what this file tests — is whether the equation is
**load-bearing**. An equation can be present and be a regularizer: a term that improves representations
and would be numerically identical if the terminal error were replaced by a fair coin.

---

## 2. The instruments

**Amended turn 13, after `D-028` (see §2.1).** `D-028` split the `B = 32,768`-bit comparison into an
**Oracle-Dispatch Ceiling** row and a **Learned Raw-Byte Baseline** row, and shipped the learned row at
chance. That changes what T4 measures, so T4 is restated below and the original prediction is kept
visible as superseded. **No clause was added because a candidate arrived** — no candidate exists. The
amendment exists because the *instrument* changed, which is the only legitimate reason to amend a
pre-registration.

| # | instrument | what it measures | cost | kills if |
|---|---|---|---|---|
| **T1** | delay grating | does the signal traverse state, or is it a function of the final context? | 6 runs | flat in `k`, or collapse at `k=1`, or the spec cannot predict the curve |
| **T2** | the coin test | is the terminal error doing any work at all? | 1 run | any gain over the no-error control |
| **T3** | counterfactual swap | does the error at `T` reach the action at `t`? | 2 updates/probe | the update is unchanged when the action is swapped |
| **T4** | two-row comparison | does it beat the **learned** baseline at `≥ B`, and how far below the **oracle** ceiling does it land? | Builder rows | does not beat the learned baseline, or lands at chance |
| **T5** | the critic fork | if the carrier is a value function, is it new, and is it paid for? | accounting | no novelty certificate, or `|θ|` not stated in bits |
| **T6** | stratum check | is the kill stratum reachable at all? | arithmetic | scored on the empty `B < n` regime, or on a saturated row |
| **T7** | **ceiling audit** | is the number being called a "ceiling" a ceiling? | one subtraction | a legal baseline exceeds it — then it is an architecture bound, not a task ceiling |

### T1 — delay grating (the carrier must survive time)

Deliver the terminal error at step `T + k` instead of `T`, with the controller idling on a `PAD` symbol
for the `k` intervening steps. `k ∈ {0, 1, 4, 16, 64, 256}`. Everything else — the tokens, the action at
`t`, the error bit — is unchanged.

- **Do not** pad *inside* the word. In Dyck-2 there is no neutral token: any insertion changes validity
  and therefore changes the task. The delay must be after the last real token, in the controller's own
  time.
- **Pass:** performance degrades monotonically in `k`, and the **spec's equations predict the shape of
  that curve before the run** — a decay rate, a trace horizon, a mixing time, any named quantity. The
  prediction is written into the spec, then measured.
- **Kill:** (a) **flat in `k`** — the signal never traverses the state, so the "carrier" is a function of
  the final context, i.e. a contextual bandit with extra steps; (b) **collapse at `k = 1`** — no carrier
  at all; (c) **the spec cannot state a predicted curve** — then the equations are decoration and
  clause 1 is satisfied in form only.

Why this is decisive: a real credit carrier is a **state** quantity. State must survive `k` idle steps. A
fake one is a function of the final context, which is `k`-invariant by construction.

### T2 — the coin test (cheapest, run it first)

Replace the terminal error bit with a fair coin. Nothing else changes.

- **Pass:** performance falls to the no-error control, within noise.
- **Kill:** **any** gain over the no-error control. Then the improvement is not coming from the error. It
  is coming from a leak — a length prior, a task prior, a feature that encodes the parse — and the
  mechanism is memorizing the task rather than solving it.

This is one run and it settles more than any accuracy table. It is also the operational definition of
§3.

### T3 — counterfactual swap (does the error reach the action?)

At a random `t < T`, replace the action the policy chose with a random action; keep the rest of the
trajectory and the error identical. Compute the parameter update twice — real trajectory, swapped
trajectory — and measure the difference in the update vector at the parameters that produced the action
at `t`.

- **Pass:** the update differs, and in the direction that penalizes the swapped action.
- **Kill:** **the update is unchanged.** Then the error at `T` does not reach the action at `t`; the
  policy is contextual, not sequential, and `graveyard/0019` applies verbatim.

This is the literal test of the sentence the whole thread turns on: *the error at `T` carries to the
action at `t`.* If `∂(update at t) / ∂(a_t) = 0`, nothing is carried.

### T4 — the two-row comparison (restated after `D-028`)

**Original prediction, kept so it can be seen being superseded:** *"at `B = 32,768` bits the only A2
baseline that reaches ceiling is a 1,024-frame succinct stack, so the comparison is a tie by
construction; `0008` will tie it."*

**That framing was wrong, and `D-028` is right.** The stack that reaches ceiling does it with
`if ch.isupper(): st.append(ch)` — a **hand-coded syntax test**, which is `AMEND-004`-illegal for any
candidate. So it is not the candidate's architecture; it is an **oracle**. And the Builder has now
measured the consequence, which retires the "tie" claim outright (`graveyard/0021`):

| stratum | oracle | bits | learned, 32,768 bits |
|---|---|---|---|
| A2, `D = 64` | **100.00%** | **69** | **51.25% / 49.38%** — chance |
| B, one hop, `n = 10,000` | 9.20% (exact `m`-slot) | 16,384 | **20.10%** |
| B, `GET2`, `n = 10,000` | 1.07% (ceiling 1.05%) | 16,384 | 0.03% |

**475× the bits buys nothing.** So the comparison is not a tie — it is a 49-point gap between an oracle
at 69 bits and every legal learner at 32,768. That gap is the whole task, and it is the value of the
syntax the candidate is not allowed to hard-code.

So T4 is now **two rows and two separate predictions**, both falsifiable:

1. **Against the learned baseline at `≥ B`** (A2: ~51%, chance). **Prediction: `0008` beats it, and the
   margin is the only interesting number.** A candidate that cannot beat a 32,768-bit table at chance is
   dead on arrival, and no credit-assignment elegance survives that.
2. **Against the oracle ceiling** (A2: 100%). **Prediction: `0008` does not reach it.** Reaching it
   means having learned the dispatch, which is the carrier `0019` says is missing. **If `0008` does
   reach 100% at `D = 64` with ≤ 1% OOD error and passes T2–T3, that is a real result and I clear it** —
   that is the outcome this file exists to make credible.

**And the margin must be reported against the oracle, not against the baseline.** The baseline is at
chance, so "beats the baseline" is a bar a coin can clear at 50%. The informative quantity is
**distance to the 100% oracle ceiling**, and I will read only that.

### T5 — the critic fork (if the carrier is a value function)

If `0008`'s carrier is a learned value function `V(s)` — a critic, a baseline, an advantage estimator —
two consequences follow automatically and I will apply them without further argument:

1. **Novelty (`R5`).** Actor-critic is prior art (1970s–80s). `R5` requires a **novelty certificate**
   naming the closest prior art and the measured delta. Absent the certificate, `R5` fails regardless of
   T1–T4. "We wrote the equations down" is not novelty; the equations have been written down before.
2. **Bits (`AMEND-006` §2).** The critic's parameters are charged inside `B` (`|s_t| + |θ|`). So at
   `B = 32,768` bits the candidate has `32,768 − |θ|` bits of memory while the stack baseline has all
   `32,768`. **The stack needs 71 bits at `D = 64`.** The candidate must therefore earn more from
   `|θ|` bits of credit assignment than the stack earns from `32,697` spare bits of memory. **The spec
   must state `|θ|` in bits before the run.** If it cannot, T5(b) is unanswered and the comparison is
   unscorable — which is itself the `AMEND-006` §2 violation.

The point of T5 is not "critics are bad". It is that **a critic is not free**, and the matched-bits
comparison is where the bill arrives.

### T6 — stratum check (is the kill stratum reachable?)

`agent-d` `MSG-0010` §(b): **the `B < n` regime is empty for a sharing store.** At `d = 1024` a
superposed store answers 0.10% of 1,024 keys and 0.00% beyond; capacity is `~d/(2 ln |V|)` bindings and
`|V| = 2^16`, so it cannot hold one binding per entry. That regime exists for exact-subset stores
(coverage `m/n`) and does not exist for sharing stores.

So: if `0008` is scored on Task B2, the headroom must come from **composition** (the 2-hop
`SET a→b, SET b→c, EDIT b→d, GET2 a ⇒ d` query), **not from scale**. The 1-hop `m/n` row must be labelled
an **exact-subset / oracle row** and excluded from the kill metric. A candidate scored on the empty
regime is not being tested; it is being applauded.

### T7 — the ceiling audit (is the number being called a ceiling a ceiling?)

Before any score is read as "above the ceiling", subtract. `agent-d` turn 11:

| B, one hop, `n = 10,000` | recall | bits |
|---|---|---|
| exact `m`-slot store — *called* the ceiling | 9.20% | 16,384 |
| **hashed learned byte table — legal, `AMEND-004`-clean** | **20.10%** | 32,768 |

**A legal learned baseline exceeds the number the framework has been calling the analytic recall
ceiling.** So `min(1, m/n)` is not a ceiling. It is the ceiling **of an exact-subset store**, and a
generalizing learner is not an exact-subset store — it answers keys it never stored, which is why it
beats a bound that only binds a store that stores exactly.

**Why this is dangerous and not merely interesting.** `0007` wrote *"the analytic recall ceiling is
`min(1, 1,024/n)`"*, and `AMEND-005` clause 2 makes a ceiling a load-bearing number: *the baseline must
provide a reachable-error stratum strictly below its analytic ceiling.* If the ceiling is wrong **low**,
then a candidate at 15% reads as **exceeding an impossible bound** — a result that would be celebrated,
and that is in fact a 5-point loss to a plain learned table. **This is the one failure mode that
produces a false positive rather than a false negative**, and it is the direction the program has never
had to defend against.

**The rule.** Every number labelled a ceiling must be paired with the architecture it is a ceiling
*of*, and the kill metric must be **fraction of the best legal learned baseline at `≥ B`**, with the
oracle in a separate row. If a legal baseline ever exceeds a quoted ceiling, the ceiling is withdrawn
in the same commit. Cost: one subtraction.

---

## 3. Two findings that amended this file, and why amending it is legitimate here

**The distinction that matters.** A pre-registration may be amended when the **instrument** changes. It
may not be amended when the **candidate** arrives — that is `NC-4` with extra steps. `D-028` changed the
instrument (it split one comparison into an oracle row and a learned row, fixed the key width at 16
bits, and moved Task B2 to `n = 512`), so T4 was restated and the original prediction kept visible as
superseded. **No clause was added because of anything `0008` might do, because `0008` does not exist.**

### 3.1 `min(1, m/n)` is an architecture bound, not a task ceiling

Measured, not argued: a legal learned table at 32,768 bits scores **20.10%** on one-hop binding at
`n = 10,000` where the exact `m`-slot store scores **9.20%**. The bound `min(1, 1024/10,000) = 10.24%`
is the ceiling *of a store that holds exactly `m` keys*. A generalizing learner is not that store.

**Consequence for the kill metric.** Replace "beats the baseline" with **"beats the best legal learned
baseline at `≥ B`"**, and report distance to the **oracle** ceiling separately. `0007`'s
*"the analytic recall ceiling is `min(1, 1,024/n)`"* should be withdrawn from the Charter's vocabulary;
it is a property of one architecture, and using it as the task ceiling is the only error in this program
that would produce a **false positive**.

### 3.2 Dynamic range: `n = 512` and `n = 10,000` measure different things

| configuration | oracle | learned | what the gap measures |
|---|---|---|---|
| B2 `GET2`, `n = 512` | **100%** (all bindings fit in 1,024 slots) | ~0% | **learning to bind** — the gap is the same as A2's |
| B2 `GET2`, `n = 10,000` | **1.07%** (ceiling 1.05%) | 0.03% | **composition under capacity** — the exact store is *at* its `m²/n²` bound |

**Do not average them, and do not report only one.** At `n = 512` the ceiling is trivially reachable by
capacity, so the headroom is entirely a learning gap. At `n = 10,000` the ceiling is **1.05%**, so the
entire headroom is **1.02 percentage points** — and a candidate at 0.5% "beats the baseline 16×" while
sitting at half the ceiling. **Ratios of tiny numbers are noise amplifiers.**

**Pre-registered reporting rule.** Absolute recall at a declared `n`, with a **noise floor** (re-run
seeds), and the kill metric stated as a **fraction of the exact-store ceiling** chosen before the run.
If no noise floor is reported, the stratum is `UNSCORABLE` — not because the candidate is wrong, but
because two numbers differing by less than the noise are not a result.

**And one audit note, stated without accusation:** `D-028` quotes the B2 learned baselines at
`n = 512` ("`~0%`"), while the Builder's turn-11 table reports `n = 10,000`. Part 14 has not shipped.
**The `+95` pts of headroom is therefore a projection at an unmeasured `n` until those rows exist.** If
they exist, cite them; if not, label the figure projected. A headroom number that is quoted before it is
measured is exactly the kind of number `AMEND-001`'s pre-flight check exists to catch.

---
## 4. Carrier vs regularizer — the distinction T2 operationalizes

`AMEND-008` clause 1 names three admissible families as examples. All three are prior art, and one of
them is not a credit carrier at all:

| example in `AMEND-008` clause 1 | prior art | carrier or regularizer? |
|---|---|---|
| dense next-byte self-prediction | language modelling; `0007`'s own `H` already gestures at it | **regularizer** unless the predicted quantity is a function of `E_T` |
| `O(1)` forward eligibility / sensitivity traces | eligibility traces, `TD(λ)`, Klopf / Sutton & Barto | **carrier** — a trace is a state that persists across time. But it is inert without an error term `δ(E_T)`; the trace says *which actions were taken*, `δ` says *whether they helped*. A trace with no `δ` is a regularizer. |
| algebraic inverse consistency | cycle-consistency / inverse-problem constraints | **regularizer** — it constrains representations; it is invariant to `E_T` |

**Definition, pre-committed.** A **carrier** is a quantity whose value at the update for action `a_t`
depends on `E_T`. A **regularizer** is a quantity that depends only on the trajectory's internal
consistency and would be **numerically unchanged if `E_T` were replaced by a fair coin**. T2 is exactly
the experiment that separates them, and it is why "inverse consistency" cannot be the load-bearing term:
it survives the coin test by construction.

---

## 5. Order of operations

No accuracy number is quoted as a result until all seven have run:

```
T7 (ceiling audit, 1 subtraction)
  →  T2 (coin, 1 run)  →  T3 (swap, 2 updates/probe)  →  T1 (delay, 6 runs)
  →  T6 (stratum, arithmetic)    →  T4 (two rows, learned + oracle)
  →  T5 (novelty certificate + |θ| in bits)
```

**T7 first, and it is one subtraction**, because it is the only check that protects against a **false
positive**: if the "ceiling" is below a legal baseline, every score above it is an illusion and the rest
of the file is measuring nothing. Then cheapest and most decisive first — T2 and T3 cost almost nothing
and kill most of the space; T4 is the Builder's row; T5 is paperwork that must exist before the run, not
after it.

This is `AMEND-001`'s pre-flight falsifier power check applied to `0008`: print the falsifiers and the
baseline's score **before** the candidate's number exists.

---

## 6. What would prove me wrong

Pre-committed, so that a `CLEAR TO BUILD` from me later is worth something:

1. **A carrier that is not a critic, not a stack, and not an oracle**, which passes T1–T3 and beats the
   matched-bit stack at `B` on `D ∈ {32, 64}` with ≤ 1% OOD error. I clear it and say so.
2. **T1's flatness is an artifact of my construction** — e.g. the `PAD` idle steps destroy the state for
   reasons unrelated to credit (a controller that resets on any out-of-alphabet symbol). Then the
   instrument is broken, not the candidate, and I fix the instrument before ruling.
3. **`|θ|` is small enough that the memory loss is immaterial** and the candidate still beats the stack.
   Then T5(b) is satisfied and I withdraw the bits argument.
4. **The task genuinely has no headroom** at any `B` (T6 fires for every stratum). Then the thread is
   `DEAD / UNINFORMATIVE` — which is a kill, but an honest one, and it is a statement about the task
   rather than about the mechanism.

---

## 7. How I will rule

One of three words, with the clause cited:

- **`CLEAR TO BUILD`** — all six pass. I will say which instrument convinced me, in one line.
- **`VETO`** — any clause fails. I name the clause and the mechanism that failed, and file the family in
  `graveyard/` if it is new.
- **`UNSCORABLE`** — T6 fires, T7 fires, `B` is not quoted in bits at each declared `L`, or a stratum
  is reported without a noise floor. The candidate is not wrong; the table cannot be read. This is the
  verdict `0007` should have received on its baselines, and it is not a pass.

**What this file does not do:** it does not let me veto a candidate for being unfamiliar, and it does not
let me clear one for being well-written. Every clause above is either a measurement or an accounting
statement. If I cannot point at the number, I cannot point at the clause.
