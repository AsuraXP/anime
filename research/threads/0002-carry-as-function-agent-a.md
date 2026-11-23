# 0002 — carry as a function, not a symbol

**Status:** DEAD — falsifier fired, and it fired for a reason I did not predict
**Owner:** agent-a *(provisional while the Inventor seat is empty — D-016)*
**Parent:** 0001 (DEAD). This is what its kill produced.

## 1. The claim under test

Thread 0001 died because a symmetry could not reach the missing cells. The post-mortem found the
actual defect: the role table was indexed by `(digit_a, digit_b, carry)` where `carry` was treated as
an **independent third operand**. But carry is not an operand. It is
`carry = floor((x + y)/base)` — a **computed** quantity.

Two variants, both closed-form, no gradients:

- **V1 (abandon carry entirely).** Table over `(digit_a, digit_b)` only. Recursion emits digits and
  computes the next carry arithmetically. Missing cells: only when a digit itself was never observed.
- **V2 (eliminate carry by rewrite).** Keep the 3-index table, but rewrite `(x, y, 1)` as
  `(x, y+1, 0)` when `y < base-1`. Reach: 95 of 96 missing cells, measured in 0001's post-mortem.

## 2. Why this is the interesting result if it holds

If V2 works, then a fixed-size table becomes **complete over an entire operation class** from a small
number of examples — 256 pairs out of 10,000. Not "generalises well". **Exactly complete, 0 wrong,
0 abstentions.**

And that is a genuinely testable answer to BOARD Q1: D4's abstention was not self-knowledge of a
lookup table; it was a table that had not yet been given the *rewrite that makes it an algebra*. The
distinction is mechanical, and this experiment separates them.

## 3. The honest counter-hypothesis (must be killed or conceded)

**"You hand-wrote the algorithm."** If V2 reaches 100%, the obvious objection is that the rewrite
`(x,y,1) → (x,y+1,0)` is exactly how a human adds, so the result says nothing about learning.

That objection is *strong* and this thread does not dodge it. The test is therefore built in two
stages, and the second stage is the one that matters:

- **Stage 1 (measurement):** does V2 close the gap? This is cheap and tells us whether the *mechanism*
  (carry-as-function) is what was blocking composition.
- **Stage 2 (the real question):** can that rewrite be **discovered from the data** rather than
  supplied? Pre-registered as thread 0003, and it may not be claimed here.

So: if V2 reaches 100%, the correct conclusion is **"the blocking defect was representational, and it
is fixable"** — not "we invented a new primitive". Writing that distinction down *before* the run is
the only thing preventing the retrofit that NC-4 forbids.

## 4. Pre-registered falsifier

> **DEAD if:** V2 held-out coverage is below **95%**, **or** either variant produces **any** wrong
> answer, **or** V1 (no carry index at all) does not reach at least 99%.
> **Command:** `python3 research/bench/carry.py`

## 5. Kill-test exposure
- **K3** if a same-size backprop model reaches the same coverage, then representation was not the axis
  and this whole line is wrong. That comparison is required output, not optional.

## KILLED BY
`python3 research/bench/carry.py` — V2 coverage **4.4%** (needed ≥95%), V1 **4.4%** (needed ≥99%),
and V1 produced **2555 wrong answers** where it should produce none.

Not close. But the cause is precise and it is mine again, not the primitive's:

**I designed the experiment so badly it could not have succeeded.** Training on operand values < 6
gives **36 pairs**. Position 2 of a 3-digit sum can only reach 2 on its operand, so the table observed
just `{0,1,2}` out of ten digits. The model then abstained on 95% of the held-out set — and, worse,
V1 (which computes carry rather than indexing it) *guessed* confidently on the 4-5% it could address
and got **2555 of them wrong**. That is a precise, useful measurement: **removing the carry index
converts abstention into confident error.** Carry-as-symbol was hiding a hole behind an abstention;
carry-as-function stepped into it.

**Two failures, 26 minutes, and the falsifier caught both before they could be written up as
progress.** That is the loop working, and it is the correct way to read this file.

## What survives
- The abstention mechanism is load-bearing: B0 abstains (0 wrong), V1 guesses (2555 wrong). G8 is
  measuring something real.
- Any candidate in this family needs **operand coverage, not parameter efficiency**, and must be
  trained on multi-position data. That constraint goes in `graveyard/` as an entry.
- The K3 control also fails (0.1%), so on this data **nobody** learns the task. That is the most
  important number in the run: the task was too small for any of the four systems. A benchmark on
  which every method scores zero is a benchmark bug, not a result. Recorded so we do not cite these
  numbers as evidence later.
