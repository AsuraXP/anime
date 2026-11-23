# A benchmark whose minimal automaton satisfies the gates
**Status:** DEAD as a benchmark — saturated by construction, before any candidate is built
**Failed because:** every task has a *minimal automaton* that computes it. If that automaton also
satisfies G2/G3/G4 (O(1) working state, O(1) reads per token), then the benchmark's ceiling is 100%
for a machine with no learning at all, and **no candidate can score above it.** The falsifier is then
passed by the baseline at ceiling, for every mechanism, at every depth — zero discriminating power as
a property of the definition, not of any particular candidate.
This is the general form of what killed three threads in a row. `AMEND-002` says a candidate must
target a task "whose finite-state key count grows with composition depth". That is **necessary but not
sufficient**: key count growing with depth does not by itself make the task hard, it only makes the
*table* big.
**The correct test:** name the minimal automaton for the task. Then:
- **If it satisfies G2/G3/G4** → the benchmark is dead. Some machine with O(1) state saturates it, so
  a candidate cannot be distinguished from a lookup, and any falsifier built on it is passed by
  construction. This is what happened to digit addition.
- **If it fails a gate** → the benchmark is viable, and **that automaton becomes the baseline the
  candidate must beat on the gate it fails.** The candidate's win must be on the gate, not on accuracy.
**Worked instances.**
| Task | Minimal automaton | Satisfies G2/G3/G4? | Consequence |
|---|---|---|---|
| digit addition `mod 10ᵏ` | 2-state FST, state = carry ∈ {0,1} = **1 bit**, 200 entries | **YES** — O(1) state, O(1) reads | **benchmark dead.** `D4` is that FST with unobserved transitions left out; `measured == ceiling == 100%` at every depth (5,680 / 19,194,400 / 64,789,012,000 key-closed pairs at depth 2/4/6, entries fixed at 104) |
| Dyck matching, nested eval | pushdown automaton | **NO** — stack grows with depth, so G2 fails | **benchmark viable**, and the PDA is the baseline. A candidate must beat it *on G2/G4*, not on accuracy |
| unbounded-counter arithmetic | 1-counter machine | **NO** — counter grows, G2 fails | viable; the counter machine is the baseline |
| lookup over a fixed key space | hash table | **YES** | dead — `graveyard/0007` |
**Evidence:** `bench/ceiling.py` §3 and `threads/0002-k3control-p6-agent-c.md` §6 (FST identity,
200/200 entries, `measured == ceiling`); depth table reproduced independently at 5,680 / 19,194,400 /
64,789,012,000 for the 104-entry D4 table and 10^(2d) for the complete 200-entry table.
**What a candidate inherits if it reuses this:** if the thread's falsifier is an accuracy threshold on
a task whose minimal automaton satisfies the gates, the candidate is untestable and the thread will
die at the pre-flight check. The tell in prose is *"we test on N-digit sums"* or *"nested depth up to
d"* with no statement of what machine saturates the task.
**Escape condition:** before opening a thread, write one line — *"the minimal automaton for this task
is X; it fails gate G because Y; therefore the candidate must beat X on G."* If you cannot fill in
the gate it fails, you have not got a benchmark, you have got a tautology.
**Corollary, and it is the uncomfortable one:** the reason a task is a *good* benchmark is precisely
that some cheap machine fails a gate on it. That means the baseline for every future thread is not a
neural network — it is a 1970s automaton. Candidates should expect to be measured against a stack
machine, and to lose on accuracy while winning on state.
