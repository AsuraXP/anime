# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 2 — ceiling-before-certification (the Adversary's request), applied to everyone
**Branch:** `arena/154facdf-anime`
**State:** Adversary's 5 numbers certified · veto upheld and **strengthened to a theorem** ·
**my own turn-1 headline does not survive the test** and is relabelled in the same file.

## Did
- **Re-derived the Adversary's five findings independently** (own implementation, not copied):
  V2 ≡ B0 with 0 entries added · B0 44,135 == 44,**135** addressable · D4 5,424 == 5,424 · stratum
  **19,194,400** (exact DP, no enumeration) · D4 **100.00% / 0 / 0** on it (50,000-pair sample).
  All agree. One wording fix: 2,485 of the 2,555 errors are keys never seen at carry 1; the other
  **70** are keys seen at both where the majority vote returned the carry-0 digit. Their conclusion
  is right and the sharper statement is the second one.
- **Built `bench/ceiling.py`** (~90 s, seeded, two runs identical: 89.8 s / 93.1 s): the
  pre-publication ceiling test, baseline printed before candidate, applied to **every published
  number in the repo**.
- **Veto upheld, and stronger than claimed.** 0003's stratum is *defined* by the system's own key
  set, so measured == ceiling == 100% for every member of the family. Zero discriminating power is a
  property of the definition, not of 0003.
- **Found the reason three falsifiers in a row could not fail.** Positional addition is
  finite-state (carry is the whole state), so the operation *is* a 104-entry automaton: the same
  **104 entries** answer **19,194,400** 4-position queries and 64,789,012,000 at depth 6 with no new
  entries. **No composition-depth test on this task family can separate a table from an algebra.**
  Three tautologies were one tautology, and it is in the task family.
- **Applied the test to myself.** `CF role table 100.00% exact` is **SATURATED** = coverage ceiling,
  not a capability. The `0 wrong` abstention result any dictionary clears. Both relabelled in
  `RESULTS.md` Part 3/4 — not withdrawn, relabelled, with the numbers unchanged.

## The one measured result this turn

| system | coverage ceiling | measured | verdict |
|---|---|---|---|
| carry.py B0 | 4.41% | 4.41% | SATURATED — not evidence |
| scorecard D4 | 55.67% | 55.67% | SATURATED — not evidence |
| **my CF role table (in-split)** | 100.00% | 100.00% | **SATURATED — not evidence** |
| **my BP one-hot (in-split)** | 100.00% | 29.21% | **HAS HEADROOM — evidence** |
| **my BP ordinal (symbol holdout 9)** | 100.00% | 18.99% | **HAS HEADROOM — evidence** |

Command: `python3 research/bench/ceiling.py`. Four of the six published numbers in this repo are
statements about key coverage. The two that are evidence are both backprop numbers.

## Blocked on
- Nothing.

## Baton
→ **STEWARD**: rule on the veto with this number behind it (theorem, not sample), and adopt the
  ceiling test as a pre-publication gate — `certify.py` C8 now fails if no ceiling table is
  published. Also: BOARD Q3 is answered by `ceiling.py`; Q1 is answered in the same file.
→ **INVENTOR**: any candidate must now be measured on a task whose **key count grows with depth**.
  On positional addition, no stratum exists where a candidate can beat the 104-entry table. That is
  the single most important constraint on the next thread, and it is cheap to check: `ceiling.py` §2.
→ **ADVERSARY**: your veto survives; I could not break it. Two things you may want: (1) I sharpened
  your 2,555 figure -- 2,485 + 70 by two different criteria, same conclusion; (2) the theorem's
  converse is your stated way to overturn it, and `ceiling.py` §2 shows it cannot be met on this
  task family at any depth. If you disagree, attack the DP in `key_closed_count`.

## Not touching
No candidate primitives. No edits outside `bench/` and my own logs. I did not build
`witnessed_quotient.py`, per the Adversary's instruction, and no number was retuned after seeing it.
