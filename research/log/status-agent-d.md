# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 10 — AMEND-007 compliance, and a retraction of my own G7 claim
**Branch:** `arena/154facdf-anime`
**State:** D-026 item (a) and the Task B2 floor/ceiling done. Gate **56/56 in 58.4 s** (`C16` new).
`0007` is vetoed (agent-c MSG-0014), so **no `episodic_controller.py` was built**.

## Did

1. **`dyck2.py` headers carry the envelope** (`graveyard/0018`): `D=4 (M=31, DEAD) … D=32
   (M=8,589,934,591, VIABLE) D=64 (3.69e+19, VIABLE)`, plus the sentence that fixes the kill metric to
   `D ∈ {32, 64}`. Numbers re-run as a pair (identical), not reused from Part 11.
2. **Equal-`B` ceiling** for `agent-b`'s blocker, `B = 1,024` entries: `n=10,000` → ceiling `0.102`,
   m-slot **9.90%**, KV scan 100% but G4-**no**, shared readout **0.00%**.
3. **`B < n` is empty for a superposed store** — `d=1024`: 0.10% at `n=1,024`, 0.00% beyond. Capacity is
   `~d/(2 ln |V|)` bindings with `|V| = 2^16`, so it cannot hold one binding per entry.
4. **Retracted my MSG-0009 claim** that G7 was a weak gate (see below).

## The retraction, because it is the turn

MSG-0009 said G7 "looks like a weak gate": collateral was 0–5 keys. That was an **absolute count of a
store holding few keys**. As a ratio, one add-only edit damages:

| d | n | correct before | damaged | **ratio** |
|---|---|---|---|---|
| 1024 | 32 | 9 | 2 | **22%** |
| 1024 | 64 | 5 | 3 | **60%** |
| 2048 | 128 | 9 | 3 | **33%** |

An oracle erase removes most of it, so the ratio measures the edit and not the store. G7 is written as
*zero* collateral, so both forms fail it there — but a candidate scored on counts looks far better than
one scored on ratios, and I published the count first. The gate is not weak; my metric was.

## Not claimed

No candidate scored. The Elman rows are still a weak baseline. `G7` remains `WITHHELD`-looking in one
sense: I can now measure it, but only one sharing store has been measured, so "0–5 keys" is not a law --
a different code at the same load could give a different ratio, and that table is not in the file.

## Next

Nothing on my bench is owed. If Steward wants the G7 picture settled beyond one store, the next
measurement is a second code family (sparse or with overflow handling) at matched `d` and `n`, which is
one table and about 2 minutes of compute. Otherwise I stand on Part 13 and wait for a candidate that
clears the Adversary.
