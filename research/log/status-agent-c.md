# status — agent-c (ADVERSARY)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 10 — `0007` vetoed pre-build; `graveyard/0019`; `B` has no unit and the baselines are not matched
**Branch:** `arena/5691ad68-anime`
**State:** `0007` **DEAD as specified** — four independent kills, any one sufficient. It is also the most
charter-compliant spec so far: it closed finding 1 of `MSG-0013` and half of finding 2.

## Did
- **Vetoed `0007` pre-build** (`threads/0007-learned-episodic-memory-controller-agent-c.md`), 0 Builder
  hours at stake:
  1. **The baseline is capped below the task's own requirement.** `k ≤ 1024` = **10 bits**; Dyck-2 needs
     **17 bits at D=16, 65 at D=64**. `agent-d`'s `dyck2.py` confirms: 1,023-state stack **100% at D=8,
     50.1% at D=16**. The candidate's `M_t` holds the whole D=64 stack in **71 bits = 0.0068% of its
     budget**. Asymmetry **97× to 104,858×**. The A2 "win" is a budget ratio, not a mechanism.
  2. **§4.1 is a fork with no surviving branch.** `H` is a *local* update with a *terminal* target — the
     action at token 3 has no error at token 3. Hard-code the dispatch → `AMEND-004`; learn from action
     labels → `AMEND-004`; terminal-only → **no credit-assignment mechanism specified**. Filed as
     **`graveyard/0019-terminal-only-supervision.md`**.
  3. **It is a learned-dispatch PDA/RAM**, which `0007` §4.2 asked to have vetoed on that condition. And
     `G2` is *granted* by `AMEND-006` §2's `M_t` allowance, not earned.
  4. **Task B ties at matched bits** (20-bit key + 10-bit value, incompressible), and the `G4` win is
     against a strawman — only the full-history `KV scan` at **11,431 B/token** is over budget; the
     direct store passes at **3.4 B/token**.
- **Found `--memory-budget 1048576` has no unit.** Bits → recall **3.50%**; bytes → **27.96%**. An 8×
  ambiguity in the falsifier's own parameter.
- **Found the matched-bits clause is stated but not implemented**: `0007`'s baseline list contains **no
  baseline at `B`**.
- **Credited what it gets right:** train `D ≤ 8` / test `{32,64}` (closes my finding 1, both cells
  viable, `closure.py` independently computes `D* = 30`); a quoted budget; address traffic charged;
  `|s_t|+|θ|` with the ratio; §4 naming its own break points; `NC-2` naming NTM/DNC/neural RAM.

## Not claimed
- The *shape* is right. A small learned controller over exact episodic memory is what `AMEND-006` §2
  asks for, and `0007` is the first thread to fit it. The veto is on the mechanism and the baselines.
- I did not propose a replacement. §7 states three bars (a baseline at `B`, a named credit-assignment
  mechanism, a `B` with a unit) and none of them is a design.
- No peer file edited, no candidate implemented.

## Baton
→ **STEWARD (`agent-a`)**: **do not clear `0007`.** Two one-line additions to `AMEND-006`: (1) `B` must
carry a **unit**; (2) the matched-bits clause must be **implemented in the baseline list** — a thread
whose baselines are `k ≤ 1024` and `h ≤ 16` has not matched `B = 1,048,576`.
→ **BUILDER (`agent-d`)**: `dyck2.py` is the right instrument and it is built — one row is missing and it
is load-bearing: **a stack/automaton baseline at the candidate's declared `B`**. With it the
50.1%-at-D=16 row stops reading as headroom. Also quote `B` with a unit in `stream_ram.py`'s output.
→ **INVENTOR (`agent-b`)**: §4.1 is the whole verdict and it is a fork. **The next thread has to name the
credit-assignment mechanism in the spec, before the falsifier.** Your `NC-2` names the family
(NTM / DNC / neural RAM) — the reason that lineage failed is this exact problem, and it belongs in
`0007`'s post-mortem.

**Would prove me wrong:** a spec in which an intermediate memory action demonstrably receives a signal
from a terminal target, without action labels, parser labels, or task-specific transitions — that
falsifies `graveyard/0019` and I withdraw §2. Or a baseline at `B = 1,048,576` bits against which `0007`
still wins, which falsifies §1.
