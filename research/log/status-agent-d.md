# status — agent-d (BUILDER)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 8 — Round 8: AMEND-006 landed, and building the benchmark it asked for found two bugs in my own task
**Branch:** `arena/154facdf-anime`
**State:** all three D-024 harness items are built and gated (**46/46 in 59.6 s**). No candidate built.
The headline is not the new table: it is that **my first Dyck-2 task was not Dyck-2** and would have
been published as one.

## Did

| D-024 / AMEND-006 item | delivered | evidence |
|---|---|---|
| closure gate prints `\|states\|` **and** bits at `D_max`, `M >= 2^30` required | `closure.py` rewritten: per-depth counts, stop at `D_max`, DEAD / VIABLE / LIVE | Dyck-1 D=16 → **17 states, 5 bits, DEAD**; Dyck-2 D=32 → **8.59e9, 33 bits, VIABLE**; crossing computed at depth 30 |
| Task A2: Dyck-2 at `D ∈ {4,8,16,32,64}`, trained `D <= 8` | `dyck2.py` (new, pair-identical, ~9 min): 0-param nulls, capped type stacks, Elman h ∈ {4,8,16} over 4 restarts | 1,023-state stack **100% at D=8, 50.1% at D=16**; Elman h=16 73.3% at D=4 → chance at 16 |
| Task B collateral definition, raw serialization, `\|s_t\|+\|theta\|`, G4 bytes/token | `stream_ram.py` (new): byte-level stream, both baselines charged | direct store 22-26 bits state, 0 params, 3.4 bytes/token, coverage on `m/L`; KV scan 11,431 bytes/token at L=10^4 — over the 4 KiB budget |

RESULTS.md: Part 11 appended by script (1834 lines total). Gate: **C14 added, 46/46 in 59.6 s**.

## The two defects, because they are the turn

1. **`valid()` counted depth only.** `Ab` scored valid, so the "Dyck-2" label was a one-counter
   (merged-alphabet) label with a two-type name.
2. **Pinned probes were single-type runs.** `pairs == pin_depth` left the inner word empty, so every
   depth-`D` probe was `AAAAAAAAaaaaaaaa`. The depth axis was real; the two-type half was untested.

Plus a third, caught by an assert: a sign flip changes depth by **2**, so the "trained at depth <= 8"
set contained depth-10 strings. And a fourth in the baseline: the stack readout lacked a
final-stack-non-empty flag, which made the *minimal exact* machine look approximate (96-97% instead of
100%) — a readout defect that would have been published as a property of the machine.

All four are fixed in code; the numbers from the first run are void and appear nowhere in RESULTS.

## Not claimed

- The Elman rows are not a strong neural baseline. They only learn the shallow half, with a disclosed
  curriculum, and **never become exact in-distribution** — so they show a qualitative collapse, not a
  state budget. The budget evidence is the capped type stacks.
- Task B still cannot test G7: collateral is 0-3 keys by construction.
- `0007` is still unscored. The surface for it now exists; the candidate does not.

## Next

Score `0007` on `dyck2.py` (it is the design Part 11 was built for), or state that its working state
cannot stay inside `2^30` at D=32 and close it the way `0006` was closed. Nothing else on my bench is
waiting.
