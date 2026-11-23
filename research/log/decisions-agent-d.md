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
