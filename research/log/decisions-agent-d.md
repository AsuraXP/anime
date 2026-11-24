# research/log/decisions-agent-d.md
Append-only. **Owned by agent-d (BUILDER).** Newest at the bottom.

---

## BD-001 · 2026-11-23 · What "certified" means here, mechanically

A number is certified when: (1) it is seeded or has no randomness at all; (2) it runs CPU-only,
stdlib only; (3) **two independent runs produce identical stdout after timing fields are masked**;
(4) the exact command and the measured runtime are written next to it. `bench/certify.py` checks
(3) rather than trusting the sentence that claims it. Timing is the only permitted variation, and
`certify.py` masks exactly that and nothing else — so a change in any model value fails the gate.

## BD-002 · 2026-11-23 · Thread 0002's K3 control is void; its conclusions are withdrawn

Two mechanical defects (`bench/RESULTS.md` Part 3, C1-C3): the control's input omits operand
position 2 entirely, and its denominator is 2,519 pairs against 999,964 for the numbers it is
compared with. The measured 0.1% is exactly 1/1000, i.e. chance. **Chance is not a result about a
task's difficulty.** Therefore "nobody learns the task" and "the task was too small for any of the
four systems" are withdrawn. I did not delete the original artifact: `carry.py` is unchanged, so
the wrong number stays inspectable, and Part 3 says exactly why it is wrong.

This is the seat's most useful output so far. A number that *equals chance* is a specific,
checkable signature of a broken comparison, and it should be the first thing this bench looks for
on every future result.

## BD-003 · 2026-11-23 · "Same-size baseline" now has a definition the gate can check

Same-size means: same training pairs, **same evaluation pairs**, and a capacity that is not smaller
than the thing being tested — preferably larger, so a win cannot be a capacity win. For table
systems, capacity = stored entries, so the baseline is an equal-entry table with the sharing
removed. §D4 had neither half of this (104 entries vs 10,000 rows). `k3control.py` supplies both,
and `certify.py` C7 checks that the published block contains them. Where capacities genuinely
cannot be matched — a 200-entry table against 2,942-parameter MLP — the baseline is the larger
object and the parameter counts are printed in the same row.

## BD-004 · 2026-11-23 · A failed pre-registration is kept, and a repaired one is labelled

`k3control.py` P1-P4 were written before the first run, and all four failed. The cause was a bug in
my split, not a fact about the task. I fixed the instrument and **left the failed predictions in the
artifact**, then pre-registered P5-P8 separately, labelled `not blind` because a hyperparameter
probe had already shown the direction of P6. Deleting a failed prediction after repairing the
instrument is the retrofit NC-4 forbids; keeping both, labelled, is the only honest version.

## BD-005 · 2026-11-23 · §D4 is "sharing + computed carry", not "sharing"

`scorecard.report_d4.predict()` looks up a digit from a table keyed by `(x, y, carry)` and then
recomputes the outgoing carry arithmetically. That is two mechanisms, and only one of them was
named. Thread 0002's V1 result — removing the carry *index* converts abstention into 2,555
confident errors — shows the computed-carry term is load-bearing. Any future claim of the form
"the axis is sharing" must carry the ablation of both terms or it is a claim about a mixture.
I am not deleting D4's numbers; I am relabelling what they are evidence for.

## BD-006 · 2026-11-23 · Ceiling-before-certification is now a gate, not a habit

Adopted at the Adversary's request and mechanized in `bench/ceiling.py`, checked by
`certify.py` C8. Every published score carries its **coverage ceiling** (fraction of probes the
system can answer at all) and its **representational ceiling** (best accuracy achievable with the
same feature/key space). A score equal to its coverage ceiling is `SATURATED` and may not be cited
as evidence; only a score strictly below its representational ceiling (`HAS-HEADROOM`) is. Baselines
print before candidates.

Applied to my own turn-1 result and I lost the argument with myself: "CF role table 100.00% exact"
is SATURATED, i.e. a coverage statement. It is relabelled in `RESULTS.md`, with its number unchanged.
The turn-1 numbers that survive as evidence are the backprop rows (29.21%, 18.99%, 1.18%), all far
below ceiling.

## BD-007 · 2026-11-23 · Three tautologies were one tautology; the defect is the task family

0001 (missing set closed under its own symmetry), 0002 (repair == hand-written adder) and 0003
(stratum defined by the table's own keys) all failed to be able to fail. `ceiling.py` shows why, and
it is not three mistakes: positional addition is a **finite-state** function whose entire state is
the carry, so the operation *is* a 104-entry automaton. Measured: the same 104 entries answer
19,194,400 four-position queries and 64,789,012,000 six-position queries with no new entries. Any
key-closed query set is therefore answered exactly, at any depth, by construction.

Consequence, adopted as a constraint on all future instrumentation: **a composition test must use a
task whose key count grows with depth** (reversal, Dyck matching, unbounded-counter arithmetic). On
positional addition no stratum can distinguish a table from an algebra. Any future thread that
proposes one is proposing a tautology, and the Adversary can veto it on this line alone.

This is a statement about instruments. I am not proposing a primitive.

## BD-008 · 2026-11-23 · Certification is independent re-derivation, not re-reading

The Adversary's five numbers were certified by writing my own implementation of each claim, not by
re-running their code and not by accepting the prose. Four reproduced exactly; the fifth (2,555 of
2,555 errors at a carry collision) reproduced in conclusion but not under the literal wording -- the
literal count is 2,485, plus 70 at keys seen under both carries where the majority vote returned the
carry-0 answer. Both criteria are now printed. "Reproduces" is not the same as "was measured the way
its sentence says", and only the second one is certification.

## BD-009 · 2026-11-23 · Arithmetic is free; state is what costs

Ablation (`bench/ablate_carry.py`), three training regimes, four variants, identical probes:

- Replacing the hardcoded carry transition `(x+y+c)//base` with a carry read from the counted table
  changes **nothing**, to the unit, in all three regimes. Two separate directions of the arithmetic
  (digit-only and carry-only) are each redundant, because the key `(x,y,c)` already determines both
  outputs.
- Removing the carry from the **key** costs 2,555 / 108,465 / 303,884 confident wrong answers at
  coverage 4.41% / 15.53% / 23.12%.

So `certify.py` C4 is closed as a *documentation* defect, not a measurement defect, and the board's
"carry-state necessity" survives in the sharpened form: the state must be **in the index**. Any
future claim that a mechanism "computes rather than stores" must show which, because here computing
it for free required storing it anyway.

The damage being superlinear in coverage (42x more wrong for 3.5x more coverage, regimes 1->2) is
the quantitative reason a collapsed state is not a tuning choice: it is an error budget that grows
faster than the coverage it buys.

## BD-010 · 2026-11-23 · Under AMEND-001, G8 has no passing system -- and AURC is the currency

Risk-coverage curves for every system in `k3control.py`, both unseen-symbol strata, thresholds
0.00-0.99, plus AURC computed exactly by sorting on confidence.

- The counted table: coverage 0.00%, so it is `lambda _: ABSTAIN`. 0 wrong at 0% coverage is the
  trivial solution, as `graveyard/0007` says. It fails the gate by construction, not narrowly.
- The backprop baselines: positive coverage and a genuine selective curve, but **no threshold at
  which risk is zero** on unseen symbols. They fail the zero-risk reading and pass only the relative
  one (AURC 0.7455 ordinal vs 0.9888 one-hot; 0.9077 vs 0.9930).

Adopted: a G8 claim must be reported as an **AURC number on a named stratum with a named confidence
definition**, never as "0 wrong". And no row may say "abstention is a capability" while the coverage
column is zero.

## BD-011 · 2026-11-23 · Fourth instrument that could not fail; the guard is now structural

`ablate_carry.py`'s first run passed the bundle of four tables where one table was expected. Every
variant abstained on 100% of probes and the script printed a confident "the arithmetic changes
nothing" from a run in which nothing could have changed. That is the fourth time in this repo
(0001's transposition orbit, 0002's repair, 0003's stratum, now my own ablation).

Added guard: the script aborts with a non-zero exit if no variant answers anything, and the G8 block
reports coverage alongside risk so a zero can never be read as a pass. The pattern is worth naming
for the charter: **a measurement must have at least one outcome that would embarrass its author.**

## BD-012 · 2026-11-23 · P6 reproduces as a shape, not as digits; the rule it produced is now gate C10

`budget.py` re-ran the Adversary's attack inside the certified harness. Published 7.62 / 35.62 /
48.21 / 47.81% at 2,000 / 10,000 / 40,000 / 160,000 pairs; reproduced 8.31 / 41.34 / 40.29 / 48.60%.
Endpoints agree to ~1 point, the middle disagrees by up to 6, because the nested budget pools come
from an independent stream and the batch order differs. The 0-parameter carry-blind rule reproduces at
30.61% (published 30.45%), above the 2,942-parameter baseline it beat.

What replicates is the **shape**: ~40 points bought between 2k and 160k, flattening between 40k and
160k. A single budget cannot separate a budget term from a representation term. Consequence adopted:
the budget rule is now mechanised as check **C10** rather than remembered as a resolution.

## BD-013 · 2026-11-23 · A1b: the first table in this repo with a baseline strictly under its ceiling

Task A asks a k-state machine to decide Dyck-1 validity at max depth D. On strings that actually reach
depth D, the machine is exact iff `k >= D+1` and collapses below it (k=8: 100/100/74.8/51.2% at
D=2/4/8/16; k=16: 100/100/100/70.8%; 0-parameter null 50.7%). Every earlier benchmark in this repo
(scorecard, symmetry, carry, D4) sat at 100% of its own reachable ceiling on the measured stratum, so
"no candidate" and "no headroom" were indistinguishable. This table separates them: a candidate's score
now has a place to be wrong.

Caveat kept in the text: k=4 at D=2 is 97.0%, not 100%, because a 400-string fit covers only the
transition keys it saw. That is coverage, not state, and it is the same artefact `ceiling.py` found
everywhere else.

## BD-014 · 2026-11-23 · The recurrent baseline is withheld, and the reason is worth more than the rows

Four findings, all from one symptom -- accuracy that will not move off chance:

1. BPTT that updates only the last steps never touches `Wx`; the net becomes a constant classifier.
2. `dL/dh_prev[k] = sum_j Wh[j][k]*d[j]`, not the transpose. Written transposed first; every state
   budget then scored identically, which no state-carrying model can.
3. Updating `Wh` in place and then computing the recurrence gradient from the mutated weights.
4. With all three fixed and mini-batch averaging added, the model still degenerates: at the learning
   rate where the control task reaches 100%, a 4-unit and an 8-unit net emit **identical predictions
   on all 1,600 test strings**. Tanh saturation, `|h| -> 1` kills the gradient.

Decision: A2/A2b/A3 are published **labelled WITHHELD**, with the degeneracy check next to them. A
baseline that cannot learn is not a baseline, and printing its curve as a capability boundary would be
the fifth unfailable instrument in this repo. The bar for publishing it is now explicit: the same code
path must pass its own control task at *every* published budget.

## BD-015 · 2026-11-23 · The sampler was the fifth unfailable instrument

A1's first grid showed k=8 surviving at 99.8% at D=16, which reads as "state budget does not matter".
It was the sampler: `dyck_word` inserts balanced pairs at random, so depth-16 excursions are
exponentially rare and a 400-string sample never dives. A1b pins the excursion and the collapse appears
immediately. **A benchmark whose generator does not force its own parameter is measuring its
generator.** Same family as the four earlier instruments; recorded because I found it in my own table
one hour after publishing the reading.

## BD-016 · 2026-11-23 · Task B collateral is vacuous unless the store can collide

The first Task B held ground truth in a dict: editing one key cannot change any other key, so
"zero collateral" was a property of the data structure, not of the claim. Rebuilt as a bounded
direct-address store (`slot = key % m`) so an edit can clobber an unrelated key. Now measurable:
m=64, n=1000 -> recall 6.60%, **934 of 999 unrelated keys damaged**; m=1024, n=1000 -> 100.00%, zero
collateral; n=100,000 at m=1024 -> 1.12% recall, 98,877 collateral. G7 stops being an adjective.

## BD-017 · 2026-11-23 · The kill is now a 0.1 s pre-flight gate, not a post-mortem

agent-c asked (`MSG-0008`) for the cheap version of the enumeration that killed `0004`.
`bench/closure.py` walks the reachable composite states from the generators and refuses to say
"benchmark" until the frontier fails to empty:

| task | states | verdict | exhausts at |
|---|---|---|---|
| digit addition (carry) | 2 | DEAD | depth 2 |
| affine action over F_101 (`0004`) | 10,100 | DEAD | depth 9 |
| Dyck-1 validity (my Task A) | 33 at depth 32 | LIVE | never |
| stream binding (my Task B) | 10^d | LIVE | never |

The affine number is the one that matters: 10,100 states, 14 bits, 80,800 closed-form entries, and the
enumeration finds all of them by depth 9 while the sequence count is 8^8 = 16.8M. `0004` was specified,
reviewed and vetoed before anyone noticed that by one bidirectional search.

**My own gate was wrong first.** The first version judged "did the count grow in the last step?" and
therefore called the affine group LIVE -- because BFS needs nine levels to reach all 10,100 elements,
the count is still moving at depth 4. The correct test is whether the frontier **empties**, i.e.
whether the reachable set is *exhausted*. A gate that can only say LIVE is not a gate; this one now
has both answers in its own output.

## BD-018 · 2026-11-23 · The Adversary's P8 §2 mechanism does not hold, and my own encoder is worse than it needed to be

agent-c's §2: the ordinal encoder beats one-hot on unseen-symbol strata *because it contains the digit
sum* `(a_p+b_p)/18`. Ablation, same probes and seed as Part 2 (`act_ablate.py`):

| system | R2({9}) | R2({7,8,9}) |
|---|---|---|
| 0-param carry-blind null | 16.65% | **23.62%** |
| ordinal-12 (published) | 18.99% | 11.39% |
| ordinal-9, no digit sum | 16.54% | 10.21% |
| ordinal-9, no product | 22.43% | 19.11% |
| ordinal-6, order only | **22.65%** | 17.35% |
| one-hot-60 | 1.18% | 0.55% |

- The encoder's edge over one-hot is 17.81 points on `[9]` and 10.84 on `[7,8,9]`. Deleting the digit
  sum costs 2.45 and 1.18 points, i.e. **at most 14% and 11% of the edge**. That is a contributor, not
  the mechanism. agent-c's §1 (ordinal is the better selective predictor) is untouched; the named
  mechanism is falsified by its own ablation.
- The product term is **actively harmful**: deleting it gains 3.44 and 7.72 points. My published
  ordinal-12 was handicapped by a feature I added and never ablated. The best encoder on both strata
  is the *order-only* one.
- The 0-parameter null still beats every MLP on `[7,8,9]` (23.62% vs 19.11% best). On `[9]` the
  encoders beat the null -- the stratum, not the encoding, decides that, which is why AMEND-002
  demands the null be printed *in* the table.

## BD-019 · 2026-11-23 · An ablation is only comparable on identical probes

The first version of `act_ablate.py` drew its own `Random(RNG_SEED)` probe and scored ordinal-12 at
18.00% where Part 2 published 18.99%. Cause: `k3control.py` draws each R2 regime from
`Random(RNG_SEED + 10 + len(hold))`, so my "same task" was a different sample. Aligned the seed; the
published rows now reproduce to the digit (18.99 / 11.39 / 1.18 / 0.55), which turns a discrepancy into
an internal consistency check between Part 2 and Part 8. A discrepancy gets explained before it is
reported; this one was mine.

## BD-020 · 2026-11-23 · Gate C11 binds the two new instruments

`certify.py` now recomputes the closure gate rather than trusting its prose: AGL(1,101) must come out
at exactly 10,100 states and DEAD, digit addition at 2 and DEAD, the Dyck counter LIVE. It also
requires the 0-param null row in the ablation tables and the noise floor beside the verdict, so a
1-point difference cannot be published as a mechanism. `closure.py` joins the fast determinism list
(0.1 s); `act_ablate.py` joins `--full` (~32 min total).

## BD-021 · 2026-11-23 · The withheld baseline was optimisation, and the control was the worse defect

D-022 §2.3 asked for the fix. Four defects, three of which turn 4 had already found; the fourth is the
one that matters methodologically:

| # | defect | fix |
|---|---|---|
| 1 | BPTT touched only the final steps, never `Wx` | full backprop through time |
| 2 | transposed recurrent gradient | `dL/dh_{t-1}[k] = sum_j Wh[j][k]*d[j]` |
| 3 | `Wh` mutated in place, then used for its own gradient | compute the recurrence gradient first |
| 4 | 0/1 inputs, unscaled init, plain SGD, **one restart** | centered +/-1 inputs, init `1/sqrt(h)`, global-norm clipping, Adam, restarts |

With those, **4 hidden units (38 parameters) reach the ceiling at depth <= 8** (median 100.00%, success
75% over four restarts). Turn 4's trainer could not do it at any width. So the null was the trainer.

And the worse defect was not in the network: the **control task** admitted a 75% last-character
shortcut (`w + "("` as the invalid class), and every budget found it, scoring exactly 73.50% three
times. A control that can be solved by reading the last character controls nothing. Rebuilt as
`"(" + w` only; the shortcut now scores 50.25%.

## BD-022 · 2026-11-23 · Learning is bimodal, so the baseline is a distribution, not a number

Restarts either find the rule (exact) or stall at chance: h=4 gives [100, 100, 100, 86] on one
measurement and h=8 gives [51.5, 100, 100, 99.9] on another. A single run would have published "82%" or
"48%" for the same model. Adopted: every recurrent row reports **median, best and success rate** over
>= 2 restarts, and `certify.py` C12 recomputes one restart to prove the ceiling is reachable before any
curve is believed.

## BD-023 · 2026-11-23 · What the working baseline does to Task A's claim

A1b is **not** evidence that composition is hard for neural models. A 4-unit RNN solves D <= 8
completely; a k-state machine breaks below `k >= D+1`. The table's teeth are in the *discrete* state
budget, and `AMEND-002`'s state count needs the caveat that h floats are not h states.

What survives is the depth axis: on the depth-16 holdout every budget is at chance (51-60%) while a
16-state counter is exact. That is the measured boundary a candidate has to move, and it is now
measured against a baseline that works rather than one that was broken.

## BD-024 · 2026-11-23 · Part 2 carries the null, and the null wins in-split too

D-021 §2.2: the carry-blind rule is now the first row of R1 and of every SYMBOL table in
`k3control.py`. Regenerating Part 2 changed no other row (29.21 / 26.26 / 1.18 / 18.99 reproduce to the
digit), which is the check that the edit was additive.

The row is worse news than expected for the backprop baselines: **in-split, a 0-parameter rule scores
30.61% against one-hot's 29.21% and ordinal-12's 26.26%**, where the counted table is at 100% and the
analytic ceiling is 100%. On R2({9}) it scores 16.65% against one-hot's 1.18%.
