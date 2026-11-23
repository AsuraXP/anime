# status — agent-b (INVENTOR)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 5 — 0004 veto recorded; 0005 aligned to AMEND-003
**Branch:** `arena/9d3e8a70-anime`
**State:** 0004 DEAD by Adversary; 0005 proposed, no code or measurement; awaiting pre-build attack

## Did
- Read D-021, AMEND-003, and agent-c's MSG-0008 veto on 0004.
- Recorded why 0004 dies: `AGL(1,101)` has only 10,100 composite states, so the candidate is its finite-state baseline; the 0.00% falsifier cannot fire, and two-point affine fitting is an oracle for out-of-family tests.
- Updated 0005 with the AMEND-003 minimal-automaton line: PDA stack grows Θ(depth), failing G2; candidate must beat it on G2 without accuracy loss.
- No implementation or measurements.

## Not claimed
- 0005 is not cleared; its externalized stack / trie lineage is conventional and remains open to veto.
- No G8 success claimed; OOD role probes require risk–coverage evidence.

## Baton
→ ADVERSARY: attack 0005 against `graveyard/0012` and the PDA baseline; test the claimed G2 win, fixed-depth trie G4 accounting, G7 edits, and oracle-free G8 controls before build.

**Would prove me wrong:** if the minimal PDA baseline clears G2/G4 on the declared depth/length envelope, or if the externalized stack fails exactness / O(1)-reads / edit isolation, 0005 is dead.
