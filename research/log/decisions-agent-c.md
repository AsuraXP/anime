# research/log/decisions-agent-c.md
Append-only. **Owned by agent-c (ADVERSARY). Others: read-only.** Newest at the bottom.
Decisions that exist only in a message do not exist; they get a line here.

---

## D-C01 · 2026-11-23 · I broke the "one graveyard entry per turn" rule, in the open
ROLES.md caps the Adversary's turn output at one graveyard entry and one attack record. The human's
brief for this turn explicitly ordered all five seeds turned into real entries plus at least one
family from my own knowledge, plus the attack on 0002. The human's instruction wins over the role
cap; recorded here so the cap's next reader knows it was overridden deliberately and not forgotten.
Nine entries written, one attack record. From next turn: back to one and one.

## D-C02 · 2026-11-23 · RULED (adversarial, not stewardly): "design error" is a real category and 0002 misused it
The distinction is valid in principle — a zero-power run cannot refute a mechanism — and invalid as
applied, because 0002 used it to assert the positive claim "the mechanism is intact". Zero power
licenses *uninformative*, never *intact*. Recorded in `threads/0002-carry-as-function-agent-c.md` §0.
This is a ruling on a thread's conclusion, which is inside the Adversary's veto. It is not a charter
ruling; that stays with the Steward.

## D-C03 · 2026-11-23 · Adopted as standing method: compute the analytic ceiling before reading a score
If measured == ceiling, the harness had zero degrees of freedom and the number is a restatement of
the training set. This one check overturned the repo's two surviving numbers (4.41% in `carry.py`,
55.67% in D4) and costs under a second. It is now the first entry in the graveyard index and the
first thing I will run against every future thread.

## D-C04 · 2026-11-23 · A falsifier scored against a variant identical to its baseline is not a test
`carry.py`'s V2 is byte-identical to B0 (the rewrite added zero entries). The pre-registered
"V2 ≥ 95%" therefore never evaluated the mechanism. Rule I will apply to every thread: before
accepting any ablation, assert the ablated variant actually differs from its baseline — in code, not
in prose. This is the cheapest possible check and it was skipped.

## D-C05 · 2026-11-23 · G8 as operationalised is not a gate; proposed NC-5 to the Steward
`abstain iff key ∉ table` is satisfiable by a hash table, so G8 passes any lookup at 0 wrong by
construction. The Steward asked in MSG-0001 whether G8 was a metric invented after seeing D4; as
measured, yes. I proposed (not decreed) a risk–coverage requirement and an NC-5 "no post-hoc
exculpation" clause. Both are the Steward's to adopt or reject.

## D-C06 · 2026-11-23 · The one thing worth keeping from 0002, and where it goes
All 2555 of V1's wrong answers occur where an incoming carry of 1 meets a key learned under carry 0.
So the finding is a collision, not an abstention property: **the correct digit is not a function of
`(digit_a, digit_b)`**. Filed as a mechanism in `graveyard/0007-abstention-by-key-miss.md` rather
than as a G8 capability on the board, because the "abstention" in both surviving numbers is a dict
membership test.
