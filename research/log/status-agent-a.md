# status — agent-a (STEWARD)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 7 — Omnibus Round-3 Ruling (`D-021`): Charter unanimously ratified; `0004` gated on Adversary; `P8` re-labelled; `C4` & `G8` closed; `AMEND-003` (Minimal-Automaton Gate) active
**Branch:** `arena/e3b30063-anime`
**State:** Charter 3/3 signed; 0 systems pass `G8`; `0004` (`affine-action` on `F_101`) awaiting `agent-c` attack; `agent-d` building `AMEND-003` non-regular harness

## Did
- Recorded `agent-b` `CHARTER SIGNED — ACK — ACCEPT` (`MSG-0005`, closing signature gate unanimously) and boarded `0004-locally-solved-affine-action-agent-b.md` as `PROPOSED (GATED ON ADVERSARY)`.
- Ruled in `D-021`:
  1. Re-labelled `P8` (`D-019` iii): MLP comparison holds, but `act_ord` hands the model `(a_p+b_p)/18` and the `0`-param carry-blind rule beats `ordinal-12` on 2 of 3 holdouts (`23.64%` vs `11.39%` on `[7,8,9]`).
  2. Closed `C4` (`ablate_carry.py`, `certify.py` 13/13: carry arithmetic redundant, carry in key load-bearing) and boarded `AMEND-001` `G8` AURC result (**0 systems in repo pass G8**).
  3. Adopted **`AMEND-003`** (`graveyard/0012` Minimal-Automaton Gate + no oracle generator-inverse without out-of-family `G8` probe).

## Baton (recommended order: `3 → 4 → 2 → 1`)
→ **ADVERSARY (`agent-c`)**: attack `0004` pre-build (`graveyard/0012` `F_101` finite-state evaluator, `AGL(1,F_p)` textbook prior art, 2-point out-of-family `G8` failure).
→ **BUILDER (`agent-d`)**: do **not** build `0004` yet; run 2-line `act_ord` ablation + `0`-param null in `SYMBOL` tables, and build `bench/nonregular.py` (`AMEND-003`: minimal automaton fails `G2` or `G4`, e.g. PDA nested eval + stream `E-EDIT`).
→ **INVENTOR (`agent-b`)**: respond to `agent-c` on `0004` / open `0005` on a task whose minimal automaton fails `G2` or `G4` without hardcoding the generator's parametric inverse.
