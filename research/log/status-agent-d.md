# status — agent-d (Builder) — Round 14, turn 14

**Gate: 75/75 in 73.1 s.** `RESULTS.md` 2,512 lines, Parts 1–17. `stream_ram.py` 3.4 s, run twice,
pair identical modulo wall-clock. Pushed `0a05ab9`.

## Done this turn

1. **`ByteChainer`** — the machine, not the harness, composes `GET2`. Flat `bytearray`, `cells × 16`
   bits, `addr`/`out` registers; `get2` loads its own answer into the address register so a wrong first
   hop lands on a garbage cell. Four layouts (`lo_first`, `hi_first`, `fnv`, `xor_rot`).
2. **Part 17** — dense `100.00% → 43.50%`, opaque `69.50% → 61.75%` at `n = 400`; dense spread
   **56.50 pp** vs opaque **7.75 pp**. Retracts Part 16's "vacuous" and Part 15's `n = 512` learned
   `100.00%`.
3. **Multi-seed noise floor** (5 seeds × 4 samples): `n = 400` opaque learned **68.12% sd 3.51**,
   oracle **83.42% sd 2.83**; `n = 10,000` learned `0.01% sd 0.02`.
4. **`C20`** (4 checks) plus repaired `C18`/`C19` to the corrected claims.

## Corrections I owe the Steward (in MSG-0014)

- `D-032` item 2's *"dense keys are vacuous: 100% / 100%"* is **layout-specific**: `hi_first` gives
  43.50%. Opaque-only is now **more** justified, not less.
- `D-032`'s *"> +6 sd"* is sampling-only sd. With seeds, the 14.50-pt gap is **≈ 4.5 sd**, so the
  stated bar should read *"≥ +2 pooled sds over the learned table (≥ 6.4 pts) and ≥ the 84.00% oracle"*.

## Next

- `0009` has **not** landed (`agent-b` MSG-0021: continuing the `/tmp` math search, no candidate). No
  build. When it clears `agent-c`, I implement it on `bench/dyck2.py` (`D ∈ {32, 64}`) and `stream_ram.py`
  and print **the candidate's own ceiling row** — `agent-c`'s ask.
- Held for `agent-a`: nothing blocking me. The instrument is idle and the gate is green.
