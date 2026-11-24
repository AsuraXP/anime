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

## 2. The six instruments

| # | instrument | what it measures | cost | kills if |
|---|---|---|---|---|
| **T1** | delay grating | does the signal traverse state, or is it a function of the final context? | 6 runs | flat in `k`, or collapse at `k=1`, or the spec cannot predict the curve |
| **T2** | the coin test | is the terminal error doing any work at all? | 1 run | any gain over the no-error control |
| **T3** | counterfactual swap | does the error at `T` reach the action at `t`? | 2 updates/probe | the update is unchanged when the action is swapped |
| **T4** | matched-bit stack | does it beat the machine that already solves the task at `B`? | Builder row | it ties the stack, or loses to it |
| **T5** | the critic fork | if the carrier is a value function, is it new, and is it paid for? | accounting | no novelty certificate, or `|θ|` not stated in bits |
| **T6** | stratum check | is the kill stratum reachable at all? | arithmetic | scored on the empty `B < n` regime, or on a saturated 1-hop row |

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

### T4 — the matched-bit stack (my Round-2 kill, pre-committed as a prediction)

At `B = 32,768` bits, quoted **in bits at each declared `L`**, the A2 baseline set must include a
**1,024-frame succinct stack**. Not because I like stacks: because `M(D) = 2^(D+1) − 1` is exponential in
`D` while `B` is fixed, so at `B` there are exactly two kinds of machine — one that is below ceiling by
construction (flat, `2^15` states exact only to `D = 14`, at chance at `D = 32, 64`; `graveyard/0014`) and
one that is at ceiling by construction (a stack). **A baseline at `B` that is neither does not exist.**

- **Pre-registered prediction, stated now so it is falsifiable: `0008` ties the stack.**
- If it ties: it is a stack in disguise (→ `graveyard/0018` + `0007` renamed), or the task is saturated
  (→ the row is uninformative, `AMEND-005` clause 2).
- If it loses: it is dead on accuracy, and no amount of credit-assignment elegance matters.
- `AMEND-008` clause 2 already requires a learned row at `≥ B` bits. **T4 says that row must be the
  stack**, because a flat learned row at `B` is at chance by construction and an unmatchable baseline is
  not a baseline.

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

---

## 3. Carrier vs regularizer — the distinction T2 operationalizes

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

## 4. Order of operations

No accuracy number is quoted as a result until all six have run:

```
T2 (coin, 1 run)  →  T3 (swap, 2 updates/probe)  →  T1 (delay, 6 runs)
                  →  T6 (stratum, arithmetic)    →  T4 (matched-bit stack)
                  →  T5 (novelty certificate + |θ| in bits)
```

Cheapest and most decisive first. T2 and T3 cost almost nothing and kill most of the space; T4 is the
Builder's row; T5 is paperwork that must exist before the run, not after it.

This is `AMEND-001`'s pre-flight falsifier power check applied to `0008`: print the falsifiers and the
baseline's score **before** the candidate's number exists.

---

## 5. What would prove me wrong

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

## 6. How I will rule

One of three words, with the clause cited:

- **`CLEAR TO BUILD`** — all six pass. I will say which instrument convinced me, in one line.
- **`VETO`** — any clause fails. I name the clause and the mechanism that failed, and file the family in
  `graveyard/` if it is new.
- **`UNSCORABLE`** — T6 fires, or `B` is not quoted in bits at each declared `L`. The candidate is not
  wrong; the table cannot be read. This is the verdict `0007` should have received on its baselines, and
  it is not a pass.

**What this file does not do:** it does not let me veto a candidate for being unfamiliar, and it does not
let me clear one for being well-written. Every clause above is either a measurement or an accounting
statement. If I cannot point at the number, I cannot point at the clause.
