# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 4 — D-020: the P6 test, and the non-regular replacement for digit addition
**Branch:** `arena/154facdf-anime`
**State:** D-020 item 1 done and reproduced; item 2 built, with **one certified table, one withheld
baseline, and one explicit gap**. Sixth self-caught instrument defect of the run, in my own headline
table, fixed in the same turn.

## Did

**Item 1 — `bench/budget.py`** (288 s, seeded, CPU): reproduces the Adversary's P6 attack inside the
certified harness. Published 7.62 / 35.62 / 48.21 / 47.81% at 2k / 10k / 40k / 160k pairs; reproduced
**8.31 / 41.34 / 40.29 / 48.60%**; 0-parameter carry-blind null **30.61%** vs published 30.45%.
Endpoints agree to ~1 point, the middle differs by up to 6 (independent nested pool, different batch
order). The **shape** replicates: ~40 points bought between 2k and 160k, then a plateau. A
single-budget result cannot separate a budget term from a representation term — which is why P6 was
right to attack mine. Rule mechanised as gate **C10**, not remembered as a resolution.

**Item 2 — `bench/nonregular.py`** (295 s, seeded, CPU). Two tasks, each opening with the
**AMEND-003** line (minimal automaton, the gate it fails, what a candidate must beat):

*Task A — Dyck-1 validity, strings that actually reach depth D (A1b):*

| state budget k | D=2 | D=4 | D=8 | D=16 |
|---|---|---|---|---|
| 2 | 63.0% | 51.7% | 54.5% | 54.2% |
| 4 | 97.0% | 66.5% | 54.2% | 54.2% |
| 8 | 100.0% | 100.0% | 74.8% | 51.2% |
| 16 | 100.0% | 100.0% | 100.0% | 70.8% |

0-parameter null **50.7%**. Exact iff `k >= D+1`, collapsing below it — **the first table in this repo
where a baseline sits strictly below its own ceiling**, so a candidate has somewhere to be wrong.
Minimal automaton is a stack PDA; the gate it fails is **G2** (working state grows O(D)).

*Task B — bounded-RAM key store with one edit:* m=64, n=1000 → recall **6.60%**, **934 of 999**
unrelated keys damaged; m=1024 → 100.00%, 0 collateral; n=100,000 at m=1024 → 1.12% recall, 98,877
collateral. Minimal automaton is a full-history store; the gate it fails is **G4** (O(n) reads), and
its bounded form fails **G7**.

**Withheld, on purpose:** the recurrent baseline (A2/A2b/A3) is measured but **not a baseline**. At the
lr where its control task reaches 100%, two of three state budgets emit *identical predictions on all
1,600 test strings* — no state-carrying model can do that. Tanh saturation. Three real bugs were found
in that trainer by this symptom (one-step BPTT, transposed recurrent gradient, in-place mutation
feeding its own gradient) and the fixed one still degenerates. Publishing 51–66% as a capability curve
would have been the fifth unfailable instrument in this repo.

## Not done, and said plainly

- **D-020's "≥3-budget neural baseline curve" is not delivered** for Task A. The bar for the next seat:
  gradient clipping + input normalisation, and the control task must pass at *every* published budget.
  Nothing else in Part 7 depends on it.
- **D-021 (received 12:14 today, after this turn's instrument was built)** adds two items for the
  Builder: ablate `(da+db)/2` and `da*db` out of `act_ord` on `[9]`, and put the 0-parameter
  carry-blind null into the `SYMBOL` tables. **Not done** — two ~5-minute seeded runs were already
  queued and the turn's certified artefact had to land. Carried to Round 5, first item. AMEND-003's
  opening-line requirement *was* adopted here, in both tasks.

## Gates

`certify.py` **20/20** in 55.9 s, including new **C10** (six checks: Part 7 published, 0-parameter null present,
≥3 budgets ≥10×, fixed-state baseline breaks below the state budget, 2-state machine at chance, and
the withheld baseline actually labelled). `--full` now also two-runs `budget` and `nonregular`
(~24 min).. Two runs of each new script are byte-identical modulo
wall-clock lines.

## Baton

1. **agent-c**: the recurrent-baseline degeneracy is checkable in ten lines (`nonregular.py` A2d) — if
   you can make a 4-unit and an 8-unit net agree on 1,600 strings, the row is not measuring state.
2. **agent-a**: A1b is the first falsifiable table we have. Score `0004` against *it*, not against
   digit addition — the ceiling is 100% with a measured breakdown below it.
3. **whoever takes Round 5**: the P8 §2 ablation (`act_ord` without `(da+db)/2` and `da*db` on `[9]`)
   and the `SYMBOL`-table null are unstarted, and neither is blocked on anything.

**What would prove me wrong:** a fixed-state machine scoring above its `k >= D+1` ceiling on A1b, or a
bounded store editing one key at m << n with zero collateral in Task B.
