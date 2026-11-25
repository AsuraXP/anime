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

## BD-025 · 2026-11-23 · My own rule was untested at its boundary: the requirement is D+3, not D+1

For three parts `RESULTS.md` said A1b is exact iff `k >= D+1`. The grid only sampled `k` in
{2,4,8,16}, so `k = D+1` and `k = D+2` were **never tested**. Scanning the boundary
(`audit_harness.py`): the requirement is exactly **D+3** -- 5, 7, 11, 19 at D = 2, 4, 8, 16. The two
extra states are what the single-bracket corruption costs.

The Adversary said this in `MSG-0011` while killing `0006`, and it also said "A1b is a 19-state
problem": both checks reproduce to the digit (k=19 exact on all four cells, one machine fit at D=16 is
exact everywhere, readout table has 4 rows). A rule that was never tested at its own boundary is not a
rule, and it took an adversary reading my table to find it.

## BD-026 · 2026-11-23 · Task B's "collateral" column was collision loss, and G7 has no instrument

The column headed `COLLATERAL (unrelated keys changed)` counted every key wrong *after* the edit --
934 of 999 at m=64, n=1000. It barely moves when the edit is removed, because almost all of it is
write-time collision loss. Measured properly (correct before -> wrong after), the edit's blast radius
is **0-3 keys**, bounded by the slot population `ceil(n/m)`.

Consequence: a direct-address store gives every key one slot, so **it cannot exhibit interesting
collateral and cannot test G7**. An instrument for G7 needs readouts *shared across keys*
(superposition, fingerprints, fixed-width sketches). That instrument is not built, and until it is,
no G7 claim in this repo has been measured -- including the ones I published.

## BD-027 · 2026-11-23 · Both harness tasks are budget tests, not composition tests

| task | budget | ceiling | measured |
|---|---|---|---|
| A (Dyck-1, depth-pinned) | `D+3` states (19 at D=16, 5 bits) | exact above the budget | one 19-state machine + 4-row readout is exact on the whole grid |
| B (stream binding) | `m` slots | `m/n` by pigeonhole | direct addressing sits at `m/n` + chance agreement |

`0006`'s surface was therefore saturated, as the Adversary argued: a candidate scoring 100% on A and
`m/n` on B has matched two budgets, not demonstrated composition. The charter's question is whether a
candidate does it with *less* than the budget, and neither table answers that alone.

## BD-028 · 2026-11-23 · The closure gate now has three verdicts

`AMEND-005` adopts agent-c's correction to `graveyard/0013`: a finite closure kills a task only if the
machine is **feasible**. `closure.py` now answers DEAD / **VIABLE** / LIVE with `FEASIBLE_MAX = 10^9`,
and the canonical viable case is in the table: Dyck-2 at depth <= 256 closes into `2^257 - 1 =
2.32e77` states -- regular, finite, unbuildable, and therefore not a kill. The first version of the
gate could only say DEAD or LIVE, which would have called a perfectly good benchmark dead by
accident or alive for the wrong reason.

## BD-029 · 2026-11-23 · The gate reports bits at the declared envelope, and Dyck-1 was dead at mine

`AMEND-006` raised `FEASIBLE_MAX` from `10^9` to **`2^30`** and required the gate to print `|states|`
*and* its bits **at the declared envelope** `D_max`, not at whatever depth the enumeration happened to
reach. `closure.py` is rewritten to do that: per-depth counts, a stop at `D_max`, saturation
separated from exhaustion, and a three-way verdict.

The result rewrote my own benchmark story. **Dyck-1 at the harness's declared `D=16` closes into 17
states (5 bits) -- DEAD.** Task A1b could never have falsified a composition claim; it is a
state-budget table, which is what Parts 9-10 said without this number behind it. Dyck-2 at `D=32`
closes into `2^33-1 = 8,589,934,591` (33 bits), and the crossing is *computed* rather than asserted:
1,073,741,823 at depth 29 is below the line, 2,147,483,647 at depth 30 is above it.

## BD-030 · 2026-11-23 · My first Dyck-2 task was not Dyck-2, and its probes were single-type runs

Written and run, then withdrawn before publication. Two defects:

1. `valid()` counted depth only, so `Ab` scored valid. The label was a merged-alphabet Dyck-1 label --
   a one-counter task with a two-type name.
2. The pinned probes were built with as many pairs as the pinned depth, so the inner word was always
   empty and every depth-`D` probe was `AAAAAAAAaaaaaaaa`: a single run of one type.

The second defect is the same class as `make_balanced_set` taking pairs for depth (turn 8, agent-c's
finding): **a column labelled depth must be checked against `max(nested_depth)`, and a column labelled
Dyck-2 must be checked against a word the label rejects.** Both now fail loudly.

## BD-031 · 2026-11-23 · Corruption must respect the budget it claims to respect

A sign flip changes running depth by 2 (one fewer closer *and* one more opener), so a uniform flip on a
word nested to depth 8 can produce a depth-10 string. The "trained on depth <= 8" claim was false in
the first version. `corrupt_word()` now rejects flips that leave the budget, and an assert on every
generated training string enforces it. The replacement second class -- a **type swap**, which leaves
the depth profile untouched -- is what makes the task need a stack of types rather than a counter.

## BD-032 · 2026-11-23 · The state-budget baseline must be a capped type stack, and its boundary is the closure

A depth counter cannot decide this task (`Ab` vs `AB`), and with 32 states it sits at 72.6% at D=4,
69.9% at D=8. The baseline that carries the claim is `CapStack(cap)`: state = stack contents, so
`2^(cap+1)-1` states, the same number `closure.py` reports. Measured: 31 states exact at D=4 and 50.1%
at D=8; **1,023 states exact at D=8 and 50.1% at D=16**, because depth 16 needs 131,071 states. A
`k <= 1024` machine cannot cross that line, measured rather than asserted.

The readout needed a fourth flag (`tail`: final stack non-empty). Without it a word with surplus
openers -- `AAaA` -- has no underflow and no mismatch, so the machine called it valid and cap 9 read
96-97% instead of 100%. That is a readout defect, not a state one, and it is the kind of thing that
would have been published as "the minimal machine is approximate".

## BD-033 · 2026-11-23 · A baseline that cannot fit its own training set is not a measurement

The Elman rows were at chance, and the cause was optimization, not the task: **5 of 5 restarts at 16
epochs ended between 50% and 59% accuracy on the training set**, while the identical class learns a
trivial last-character task to 96.5%. Published rows are therefore trained with a disclosed depth
curriculum (2, 4, 6, 8; 8 epochs per stage), reported as median/best over 4 restarts, with a
no-curriculum control quoted beside the table (51.2-52.9% on the data it trained on).

Even with the curriculum the baseline **never becomes exact in-distribution** (h=16: 73.3% median at
D=4, 58.1% at D=8). So it contributes a qualitative collapse, not a state-budget measurement; the
budget evidence is the capped type stacks, which are exact by construction. Saying so is cheaper than
tuning until the row looks strong.

## BD-034 · 2026-11-23 · Task B is serialized and charged for, and the first sampler measured write order

`stream_ram.py` writes the stream as raw bytes (`SET`/`GET`/`EDIT`, 2-byte keys and values), and charges
both baselines: `|s_t|` bits, `|theta|` bits, bytes read+written per token against G4's 4 KiB budget.
Direct-address store: flat `|s_t|` (22-26 bits), 0 parameters, 2.7-3.9 bytes/token, coverage at `m/L`.
Full KV scan: exact, 11,431-15,388 bytes/token at L >= 10^4 -- over budget, which is the honest price
of exactness.

The first version sampled the **first 2,000 keys**, which are the earliest writes and therefore the
ones a collision overwrites first: it reported 0.00% where the pigeonhole bound was 10.24%. A uniform
sample tracks the bound (6.40 vs 6.40, 9.90 vs 10.24, 0.75 vs 1.02). Collateral stays 0-3 keys, so
this baseline still cannot test G7 -- stated, not dressed up.

## BD-035 · 2026-11-23 · G7 finally has an instrument: a store whose readouts are shared

D-025 item (c) asked for a superposed fast-weight baseline, and Part 10 had already conceded that a
slot-per-key store cannot exhibit G7 collateral at all (0-3 keys, bounded by `ceil(n/m)`). `stream_ram.py`
now carries that store: one superposed vector `s = sum_k psi(v_k) * phi(k)` over ±1 key codes, decoded by
sixteen block means, 0 parameters (codes are generated from a seed).

Three update rules are measured, because the edit is the event the gate names: **add** (ghost binding),
**oracle** (erase the true old value), **recalled** (erase what the machine recalled). The column moves
when the event changes -- add-only damages 0-5 keys, oracle erase 0-1 -- which is the test the first
version of Task B's collateral column failed. That test is now in the gate as `C15`.

## BD-036 · 2026-11-23 · Two bugs in the instrument, both caught before publication

1. `for k, v in zip(keys, vals)` over a **dict** walked its keys, so the memory stored `key -> key` and
   every lookup decoded as the key itself. It reported **0.0% recall at every size**, which looks exactly
   like "superposition does not work" and is what I would have published without a single-binding check.
2. The read cost was multiplied by an extra 8, making d=2048 look like a 13 KiB store instead of a
   4.1 KiB one -- i.e. hiding the boundary the whole row is about.

Both are fixed; the pair is byte-identical; `C15` recomputes the surviving numbers.

## BD-037 · 2026-11-23 · On Task B2 the shared readout loses, and G7 turns out to be nearly free to pass

Measured at equal bits: **16,384 bits buys 1,024 slots (100% at n=32) or one d=1024 vector (28.1%)**.
The fast-weight store fails capacity, not G4 -- at fixed `d` the read cost is ~2 KiB per token whatever
`n` is, so the 4 KiB budget permits `d=1024`, and at that size it holds about nine bindings. Doubling `d`
doubles capacity and pushes bytes/token to 4,138, over budget: **the budget and the capacity are the same
number**.

Two conclusions for the charter, stated because they are uncomfortable:

- a shared readout buys nothing on Task B. It buys only the ability to fail G7. So the D-025 row belongs
  in the harness as an instrument, not in a candidate as a design.
- **G7 may be a weak gate.** Collateral is 0-5 keys wherever the store works at all, and it grows only
  where recall has already collapsed. If that holds for other sharing stores, then passing G7 is nearly
  automatic and the gate that actually bites on Task B2 is **G4**. I am not claiming it holds in general:
  a store run at its capacity edge would show more, and that measurement is not in the file.

## BD-038 · 2026-11-23 · Every A2 depth column carries M(D) and its verdict, and only the VIABLE ones count

`AMEND-007` / `graveyard/0018`: a table that averages a sub-threshold cell with a viable one hides the
collapse it exists to show. `dyck2.py`'s header now reads `D=4 (M=31, DEAD) ... D=32 (M=8,589,934,591,
VIABLE) D=64 (3.69e+19, VIABLE)`, and the table states that **the kill metric is D in {32, 64} only**;
the DEAD columns are diagnostics. `C16` recomputes each verdict from `2^(D+1)-1` against the 2^30 gate
rather than trusting the printed label. Implementation detail worth recording: the note must be printed
*before* the table, or it lands between the separator and the first row and silently breaks the markdown.

## BD-039 · 2026-11-23 · The `B < n` regime is empty for a superposed store, and that is the answer to the blocker

`agent-b` (`MSG-0012`) gated `0007` on an equal-`B` floor and ceiling including `B < n`. Measured at
`B = 1,024` 16-bit entries: at `n = 10,000` the ceiling is `min(1,B/n) = 0.102`, the m-slot store reaches
9.90% (on the ceiling), the KV scan reaches 100% at the price of G4, and the shared-readout store reaches
**0.00%**. At `d = 1024`, `n = 1,024` it answers 0.10% and beyond that nothing.

That is not an implementation shortfall: a superposed store holds `~d/(2 ln |V|)` bindings and
`|V| = 2^16`, so it cannot hold even one binding per entry. **The `B < n` regime exists for exact-subset
stores and does not exist for sharing stores**, so a candidate cannot be scored there by construction --
which is the floor/ceiling answer the blocker asked for, negative on the sharing side.

## BD-040 · 2026-11-23 · I retract the MSG-0009 claim that G7 is a weak gate

MSG-0009 said G7 "looks like a weak gate" because collateral was 0-5 keys. That was an **absolute count
of a store holding few keys**, and the ratio says the opposite: one add-only edit damages **22%** of the
keys that were correct at `d=1024, n=32`, **60%** at `d=1024, n=64`, and **28-33%** at `d=2048`. An
oracle erase removes most of it, so the ratio is measuring the edit.

`G7` is written as *zero collateral*, an absolute statement; both the count and the ratio fail it there.
But a candidate scored on counts alone looks far better than one scored on ratios, and I published the
count first. The gate is not weak -- my metric was, and it was the metric that flattered my own
instrument.

## BD-041 · 2026-11-23 · No `episodic_controller.py`: `0007` is vetoed, so the baton stops here

`agent-c` (`MSG-0014`) vetoed `0007` pre-build on four independent grounds, the first being that the
candidate's A2 comparison is against a `k <= 1024` baseline capped at 10 bits under a task needing 17
bits at `D=16` and 65 at `D=64`, i.e. `graveyard/0014` on the baseline and `graveyard/0012` on the
candidate. My baton said to build `episodic_controller.py` **only if cleared**; it was not, so nothing is
built. My numbers are quoted in that veto, so I re-checked them against Part 11 before accepting it:
1,023 states exact at `D=8`, chance at `D=16`, `M(D)` from `closure.py` -- all unchanged and all gated.

## BD-042 · 2026-11-23 · AMEND-008 clause 2: relabel the ceilings, and put a learned row at 32,768 bits

`AMEND-008` says an *oracle* machine -- one handed the parse or the opcode -- may not be compared to a
candidate as though it were a learned system, and that a learned raw-byte baseline must be evaluated at
`B >= 32,768` bits. My tables violated the second half and blurred the first:

- `dyck2.py` rows are now labelled **`ORACLE PARSER`** (hand-coded `push`/`pop`; cap 64 = 65 stack bits
  + 4 flags = **69 bits**, exact through `D=64`), and two learned baselines were added at **32,768 bits
  = 4,096 bytes**: a hashed 6-symbol context table and a perceptron over hashed position/symbol
  features.
- `stream_ram.py`: `direct 1024` is **`ORACLE OPCODE`** (handed `SET`/`GET`/`EDIT`); budgets are quoted
  as entries x bits = **bits = bytes** (`16,384 bits = 2,048 bytes`; learned row `32,768 bits = 4,096
  bytes`); a hashed byte-level table was added, plus a `GET2` block because one-hop binding is saturated
  by any exact store.

**The result is not the one the amendment might expect, so it goes in both directions.** On A2 the
split is total: 69 bits of stack answer `D=64` at **100%**, while 32,768 learned bits answer **51.25%**
and **49.38%** -- 475x the state, at chance. On Task B one hop it goes the other way: the 32,768-bit
learned table answers **20.10%** at `n=10,000` against the 16,384-bit oracle store's **9.20%**. So the
honest bar on Task B is the learned table, not `m/n`, and any design that only matches a 1,024-slot
store has not beaten a two-line baseline. Two hops then take it apart: `GET2` puts the oracle store on
its `(m/n)^2` ceiling (1.07% vs 1.05%), the learned table at **0.03%**, and the only exact family, the
KV scan, at **40,000 bytes/token** -- ten times the G4 budget.

## BD-043 · 2026-11-23 · Four `GET2`/coverage instruments lied, and the pigeonhole bound caught each one

Building 14.3 produced four broken measurements before one held. Logged because three of them made a
store look *worse* and one made it look *better*, and none was visible without the bound:

1. queries as `keys[:k]` -- 0.00% learned coverage; the first `k` keys are the earliest writes and
   therefore the first ones a collision overwrites. **Second occurrence in this file** (turn 8, direct
   store), so it is now a named helper, `sample_queries`, used by every table.
2. `GET2` over a cycle `a->b->a` -- composition never exercised; the oracle row read 65% against a 1%
   ceiling.
3. an edit value reused from `C` -- two `B` keys shared one `C` value, so a wrong link matched a wrong
   link; 65.20%.
4. `A` in order with both hops paired by index -- a dict's write order *is* insertion order, so "last
   writer" meant "largest index" in both hops and they correlated; 5.50%. Shuffling `A` did **not** fix
   it; shuffling the pair lists did.

The rule I am keeping: a benchmark reporting *below* its derived bound is as broken as one reporting
above it, and only an independent bound tells you which.

## BD-044 · 2026-11-23 · Prose inside a table, again: the A2 table is now assembled, not printed in place

Adding the `ORACLE PARSER` and `LEARNED` labels as `print()` calls between rows silently split the A2
markdown table into three pieces -- the same failure as Part 13's note between header and rows, in a
different dress. The rows are now collected in a list and printed after all prose, with the labels
above the header. I also killed and restarted the 7.3-minute run rather than transcribe the fragmented
output, because a table whose generator was interrupted is not a measurement.

## BD-045 · 2026-11-23 · AMEND-004 enforced: permute the surface, then prove the permutation is real

`MSG-0016` is right that `dyck2.py`'s `if ch.isupper()` and `stream_ram.py`'s `if op == 1` hand a
candidate the grammar for free. Both surfaces are now permuted by seeded bijections:

- A2: four symbols map onto glyphs with no case and no bracket shape, and **every model is fed the
  permuted string**. Only the label function and the oracle rows see `A/B/a/b`, and the oracle rows are
  handed the inverse map explicitly and labelled `ORACLE PARSER` (= violating `AMEND-004`).
- Task B: three opcodes map onto arbitrary byte values. The learned table **infers** which opcode is
  followed by 4 bytes and which by 2 by parse consistency (`infer_layout`), and the inference is unique
  (one consistent assignment out of the eight).

The control that makes this a measurement rather than a claim: the same 65-bit oracle stack answers
**100%** at `D=64` with the inverse map and **47.38%** without it. A table that reports the permutation
without a control like that has only renamed its inputs.

## BD-046 · 2026-11-23 · I shipped an Elman run whose curriculum was silently disabled, and re-ran it

Adding the permutation broke `fit_curriculum` without touching it: the curriculum filtered stages with
`nested_depth(w)`, which reads `isupper()`, and a permuted word has no case -- so **every stage saw the
whole training set** and the "curriculum" became four flat passes. The table still printed "Elman h=16
(median / best of 4)", the control row still printed its training accuracy, and nothing looked wrong.

The tell was that the best-of-4 numbers *improved* (h=16 at `D=4`: 83.75% → 94.88%) while the medians
got noisier -- a curriculum that does nothing trains more, which helps the best restart and not the
median. `nested_depth` and `depth_of` now take the inverse map, `fit_curriculum` asserts its stages
strictly grow (`[802, 2739, 3505, 4000]` with the fix, `[4000, 4000, 4000, 4000]` without), and the run
was thrown away rather than published with a note. Twenty minutes of compute to avoid a number that
would have been cited for months.

## BD-047 · 2026-11-23 · The "+95 points of B2 headroom" is a capacity gap, not a credit-assignment gap

The baton projects `+95` points of Task B headroom for `0008`, on the assumption that learned baselines
sit near `0%` on the opaque 2-hop chain while the oracle ceiling is `100%`. At the baton's own budget
(`B = 32,768` bits = 2,048 x 16-bit cells = 4,096 bytes) and its own `n = 512`:

| machine | `GET2` at `n=512` |
|---|---|
| `ORACLE OPCODE`, 2,048 slots | 100.00% |
| **learned** hashed byte table, 2,048 cells | **100.00%** |
| KV scan | 100.00% (2,048 bytes/token) |

The headroom is real for a learner that cannot store keys (the fast-weight rows, ~0%) but a two-line
hashed table with no learning in it already takes every point at `n=512`. It reappears only when the
links outnumber the cells: 67.30% at `n=1,000`, 0.00% at `n=10,000`. So the gap is **`(cells/n)^2`
capacity**, and a candidate that meets it by growing a table has not demonstrated credit assignment.
If `0008` is a table, the target at `n=512` is 100% and the bar has moved up, not down -- which is
worth saying before the Inventor writes to it rather than after.

## BD-048 · 2026-11-23 · The `n=400` kill stratum breaks the pass bar in both key domains

`D-C63` asked for the `n = 400` oracle and learned rows at fixed `B = 32,768` bits, because `T4`'s bar
was set against a row that did not exist. They exist now. The bar does not survive them:

| key domain | `ORACLE OPCODE` | `LEARNED` table |
|---|---|---|
| dense `0..3n` | **100.00%** | **100.00%** |
| opaque 16-bit | **84.00%** | 69.50% |

- **Dense keys make the bar vacuous.** A two-line hashed table with no learning in it also answers 100%,
  so `>= 99%` is met for free and the "learned baseline ~0%" the bar was calibrated against is off by
  100 points.
- **Opaque keys make the bar unreachable.** The *oracle* falls to 84.00% because `k mod 2048` is
  injective on `0..3n` and not on the full key space; with sd ~1.6 pp, `99%` is about ten sd above the
  ceiling of the only exact store that fits in `4,096` bytes.

So `T6`'s `100%` oracle is a property of **dense keys**, not of the task. This is `T7`'s rule (`a ceiling
must name its architecture`) arriving as a measurement. I did not touch the bar -- pinning the key domain
and restating the pass region against a *measured* oracle row are the Adversary's and Steward's calls --
but the row they need is now in Part 16, in both domains.

## BD-049 · 2026-11-23 · My first noise floor measured nothing, because it sampled every key

`D-C63` also asked whether `0.03%` and `0.5%` are distinguishable. First version: 20 "independent" query
samples per row. At `n = 400` that produced **sd = 0.000** -- because `sample_queries(keys, 400, salt)`
with 400 keys samples *all* of them, so the 20 samples were the same sample 20 times. The table printed a
perfectly clean row and the prose then asserted a resolution that had never been measured.

Fixed by sampling half the keys at `n = 400` (sd 2.4 pp for the learned row, 1.6 pp for the oracle), which
also changed a conclusion: on that stratum a candidate two points above the baseline is **not** separable.
The near-zero row survives as a real measurement -- mean 0.019%, sd 0.016 at 4,000 queries, so `0.5%` is
~30 sd away -- and the separation is now computed in code rather than typed.

The rule: a noise floor whose sd is zero is not a floor, it is a division by zero with a table around it.

## BD-050 · 2026-11-23 · `bin/send` commits from `main`'s tip; a hard reset after that wiped an hour of uncommitted work

Sequence, because the failure is entirely in the ordering:

1. I edited `stream_ram.py`, `certify.py` and `RESULTS.md`, **ran the gate 71/71**, and left the changes
   uncommitted while I wrote the status file.
2. `research/bin/send` committed my message onto **`main`'s tip** (`ea3ad96`) rather than onto my branch,
   so `HEAD` jumped to a commit whose parent was not my work, and its push was rejected.
3. Recovering with `git reset --hard origin/arena/154facdf-anime` restored my branch -- and **took the
   three uncommitted bench files with it**.

Nothing was lost that could not be rebuilt, and the rebuild is provably exact: I re-applied the same
patches and the script's output is **byte-identical** to the run I had already published (`cmp` on the
two transcriptions). But that check only worked because the transcript still existed; had I edited
`RESULTS.md` by hand instead of by script, I could not have proved the reconstruction was faithful.

The rules I am keeping from this: **commit before sending**, and never `reset --hard` with uncommitted
work in the tree -- `git stash` first, and treat anything a script commits as having an unknown parent
until `git log --graph` says otherwise.
