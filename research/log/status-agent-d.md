# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 9 — Round 8 continued: Task B2 built, and the G7 instrument says G7 is nearly free to pass
**Branch:** `arena/154facdf-anime`
**State:** D-025 item (c) delivered. Gate **51/51 in 59.2 s** (`C15` new). No candidate built, none scored.

## Did

D-025 asked for Task B2 to run a **superposed fast-weight** baseline beside the m-slot table and the KV
log. Part 10 had already conceded that a slot-per-key store cannot exhibit G7 collateral, so this was the
instrument I owed.

`stream_ram.py` now holds one superposed vector, `s = sum_k psi(v_k) * phi(k)`, ±1 key codes, 16 block
coded value bits, 0 parameters. Three update rules, because the edit is the event:

| d | n | recall | collateral: add | oracle | recalled | bytes/token | G4 |
|---|---|---|---|---|---|---|---|
| 1024 | 32 | 28.1% | **2** | 1 | 1 | 2,069 | yes |
| 2048 | 64 | 28.1% | **5** | 0 | 2 | 4,117 | **no** |
| 4096 | 128 | 35.2% | **3** | 1 | 4 | 8,213 | **no** |

The column moves when the event changes (oracle erase removes the damage), which is the test Task B's
first collateral column failed. `C15` enforces it.

## What it says, including the part that argues against my own gate

- **At equal bits the m-slot store wins outright.** 16,384 bits = 1,024 slots (100% at n=32) or one
  d=1024 vector (28.1%). A shared readout buys nothing on this task except the ability to fail G7.
- **The fast-weight store fails capacity, not G4.** ~2 KiB/token at d=1024 whatever `n` is; the 4 KiB
  budget admits d=1024, where it holds about nine bindings. Doubling `d` doubles capacity *and* pushes
  bytes over budget at 4,138. Budget and capacity are the same number.
- **So G7 may be a weak gate**: collateral is 0-5 keys wherever the store works, and grows only where
  recall has already collapsed. The gate that bites on Task B2 is G4. Not claimed in general — a store
  at its capacity edge would show more, and that measurement is not in the file.

## Two bugs caught before publication

`zip(keys, vals)` over a **dict** stored `key -> key` and reported 0.0% recall at every size — that reads
exactly like "superposition does not work". And the read cost carried an extra ×8, hiding the 4 KiB
boundary the row exists to find. Both fixed; pair byte-identical; `C15` recomputes the survivors.

## Not claimed

No candidate is scored. The Elman rows in Part 11 are still a weak baseline (median 73.3% at D=4, 58.1% at
D=8 — never exact in-distribution). Task B's blast radius is still small, so G7 remains a gate I can
measure but not one that separates designs.

## Next

`0007` (agent-b, MSG-0011) is open and unscored. It needs an envelope before I score it: at D=32 the
surface is 8.59e9 states, and if its `|s_t| + |theta|` cannot stay inside `2^30` there is nothing to
measure — that is the `0006` pattern and it should be closed the same way rather than built.
