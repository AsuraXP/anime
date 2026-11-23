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
