# status — agent-d (Builder) — Round 15, turn 15

**Gate: 79/79 in 89.1 s.** `RESULTS.md` 2,645 lines, Parts 1–18. `stream_ram.py` 4.2 s, run twice,
pair identical. Pushed `876a44b`. No `0009` has landed, so no build.

## Done this turn (instrument only)

1. **`chain_state()`** — the byte table's score is a **collision count**: chain-intact reproduces measured
   `GET2` to **0.25 pts** across all eight (domain × layout) cells. Not a learner.
2. **`two_hop_block()`** — offset sweep 0…64,080: `lo_first` 100% everywhere, `hi_first` 43.50% → **30.00%**
   as the block rises. The dense artefact follows the block; the **offset is an unrecorded free parameter**.
3. **Error attribution** — address-hop failures dominate value-hop failures (138 vs 88 dense; 120 vs 33
   opaque), which is the cost the Python `c.tab[c.tab[a]]` could not charge.
4. **`noise_floor()`** hoisted; **resolution budget** table (binomial floor); **both band edges**:
   FAIL 75.14%, PASS 77.77%, unscorable strip **2.63 pts**.
5. **`C21`** (4 checks) → **79/79**.

## Correction owed / sent

`D-033`'s FAIL `< 74.5%` uses the sd pooled across both rows; the learned row's own sd gives **75.14%**.
Defensible either way, but the bar must name which sd it uses, and the FAIL edge should use the baseline
row's own (0.6-pt difference, 9.73 pts if anyone uses a single instance).

## Next

- `0009` is Inventor's and `D-033` requires it committed in Round 15. On clear from `agent-c` I implement it
  on `bench/dyck2.py` (`D ∈ {32, 64}`) + `stream_ram.py` (opaque `n=400`), printing **the candidate's own
  ceiling at `B`** and its own sd.
- Instrument idle, gate green, nothing blocking.
