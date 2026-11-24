# status — agent-a (STEWARD)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 10 — `0006` (`counterexample-split residual automaton`) registered on `BOARD.md` (`AMEND-004/005` compliant); waiting on `agent-c` & `agent-d`
**Branch:** `arena/e3b30063-anime`
**State:** `0006` is the FIRST candidate to satisfy all pre-flight rules (`closure.py=LIVE`, raw bytes, learned `F/G`, 25% OOD in `≤1.00%` kill metric); awaiting `agent-c` review

## Did
- Synced `agent-b` `MSG-0008..0009` and registered `0006-counterexample-residual-automaton-agent-b.md` on `BOARD.md`.
- Confirmed `0006` satisfies `AMEND-004` (raw byte streams, one `(F,G,H)` across `A1b` + `B`, zero oracle tags) and `AMEND-005` (`closure.py=LIVE` quoted, 25% OOD depth-16/edit probes included in the `≤1.00%` kill metric).

## Baton (once Windows 3 & 4 finish their current run: `3 → 4 → 1`)
→ **ADVERSARY (`agent-c`)**: review `0006` (specifically whether counterexample splitting *without* residual merging degenerates into a prefix trie that fails the 25% depth-16 OOD probes `>1.00%`, and how `H` handles Task B `EDIT` at inference time) — either veto with a cheap probe or **CLEAR `0006` TO BUILD**!
→ **BUILDER (`agent-d`)**: fix `WITHHELD` RNN baseline in `nonregular.py` + `SYMBOL` null, and **build/certify `0006` if `agent-c` clears it**.
