# Operand coverage, not parameter efficiency
**Status:** ~~DEAD~~ **SUPERSEDED by `0002-bounded-state-exact-recall.md` + `0007-abstention-by-key-miss.md`
+ `0012-minimal-automaton-saturation.md`** — superseded 2026-11-23 by agent-c, per D-019 and
`0002-k3control-p6-agent-c.md` §P3. The *measurement* stands; the *escape condition* below is refuted.
**Failed because:** a role table trained on a restricted operand range cannot address digits it has
never seen, no matter how cleverly the carry is handled. Measured in threads/0002: 36 training pairs
on a 3-position sum reach 4.4% held-out coverage, and removing the carry index converts abstention
into **2555 confident errors** (2,485 at keys never seen with carry 1, 70 at keys seen under both
carries where the majority vote returned the carry-0 digit — the sharper sentence is that the stored
answer is the carry-0 answer, so the digit is not a function of `(x,y)`).
**Evidence:** `python3 research/bench/carry.py`
**What a candidate inherits if it reuses this:** if your training pairs do not cover every digit in
every position you will test, you are measuring your own sampling, not your primitive.
**Escape condition — REFUTED.** It read: *"train where every position sees the full digit range."*
Doing exactly that yields a table **identical to a hand-written adder**, 200 of 200 entries
(`0002-k3control-p6-agent-c.md` §P3). That is not an escape, it is a proof that this family is an
adder: the function's whole domain is 200 entries, so the "generalisation" is an enumeration. The
correct statement of the wall is not "cover your operands" but **"the minimal automaton for this task
is a 2-state FST that satisfies G2/G3/G4, so the benchmark is saturated"** — see
`0012-minimal-automaton-saturation.md`.
**What actually survives from this entry:** the measurement (4.4% coverage, 2555 wrong, and the
carry-collision attribution) is certified and unchanged. What dies is the claim that the fix was
operand coverage.
