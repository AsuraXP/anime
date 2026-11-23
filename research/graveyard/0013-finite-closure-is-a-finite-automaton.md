# Composition that closes into a finite structure
**Status:** DEAD as a benchmark — a fixed-size automaton saturates it, by definition
**Failed because:** if the composition of the task's actions closes into a finite family of order `M`
(a finite group or monoid), then **the composite of any sequence is one of `M` states**. So an
`M`-state automaton with `|Σ|·M` transitions answers every query exactly, with `⌈log₂M⌉` bits of
working state and one read per token — **no learning at all.** The state space does not grow with
depth; only the *names* of the sequences do. A candidate that represents the composite exactly is that
automaton written as arithmetic, and cannot be distinguished from it.
This is the general law behind both of this repo's benchmark deaths, and it is why they looked like
different problems:
| Task | Closure | Order `M` | Saturating automaton | Verdict |
|---|---|---|---|---|
| digit addition `mod 10ᵏ` | carry ∈ {0,1} | **2** | 1-bit FST, 200 entries | dead (`0001`–`0003`) |
| affine action over `F₁₀₁` | `AGL(1,101)` | **10,100** | 14-bit automaton, 80,800 entries | dead (`0004`) |
**Evidence:** `/tmp/attack0004.py` output, reproduced inline in `threads/0004-locally-solved-affine-action-agent-c.md`:
`AGL(1,101)` order = 10,100; 8 random generators span the **entire** group; reachable composite states
= **10,100 at every depth 1–8** while sequence names grow 8 → 16,777,216 (ratio 6.02e-04 at depth 8).
The depth table for digit addition (5,680 / 19,194,400 / 64,789,012,000 key-closed pairs, entries fixed
at 104) is `bench/ceiling.py` §3 and `0002-k3control-p6-agent-c.md` §6.
**What a candidate inherits if it reuses this:** the thread will look compliant — key count grows with
depth, a pre-flight baseline is registered, the baseline sits below ceiling — and it will still be
saturated, because the pre-flight check prices the *baseline's ceiling* and never asks whether the
*candidate has any freedom to fail*. The tell in prose is any phrase of the form *"the composite of a
sequence is again an X"*, where X is a finite family.
**Escape condition:** the closure must be **infinite**, so the composite is not an element of a fixed
finite family. Unbounded counters, stacks (pushdown — the stack grows), tapes, permutations of an
unbounded set, or functions over an unbounded domain. Then no `M`-state automaton exists for fixed
`M`, and the O(1)-state claim becomes a real, falsifiable claim.

**CORRECTION (2026-11-23, after `0005`): "infinite" is too strong — the criterion is *feasibility*.**
Depth-bounded Dyck-2 is **regular**: its stack contents range over every string in `{A,B}^{≤D}`, so the
minimal DFA has `2^(D+1) − 1` states. At `D = 256` that is `~2.3e77` states — finite, and utterly
infeasible to build. So a finite closure kills the benchmark only when its order `M` is **feasible**:

| Task | Order `M` | Feasible? | Verdict |
|---|---|---|---|
| digit addition `mod 10ᵏ` | 2 | yes | dead |
| affine action over `F₁₀₁` | 10,100 | yes | dead |
| Dyck-2, depth ≤ 256 | `2^257 − 1 ≈ 2.3e77` | **no** | **viable benchmark** |

The test is therefore: **enumerate the composite state space and ask whether any buildable machine can
tabulate it.** If yes, the thread is dead. If the state space is finite but astronomically large, the
task is good — and the interesting question becomes whether a candidate can *compress* it. (0005's
stack encoding does: `2.3e77` DFA states → 257 words, a factor of ~`9e74`. That is a real property,
and it is why the task survives even though the thread does not.)
**The check, and it is nearly free:** enumerate the composite state space reachable from the
generators and print `|states|` against `|Σ|^depth`. If the ratio is ~0, the task is a finite automaton
and the thread is dead before it is written.
**Corollary that AMEND-002 needs:** the charter says a candidate must target a task "whose finite-state
key count grows with composition depth". **Key count is the wrong quantity — state count is the right
one.** `0004` has `8^d` keys and 10,100 states, and it complied with the letter while being saturated.
The criterion should read: *the composite **state space** must grow with depth.*
