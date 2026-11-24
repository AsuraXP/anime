# 0019 — terminal-only supervision cannot reach an intermediate action
**Status:** DEAD (a learning-rule family; it is the default shape of every "learned controller" proposal)
**Family:** a **local** update rule driven by a **terminal** target, asked to learn a **sequential**
policy — memory actions (`PUSH`, `POP`, `READ`, `WRITE`) whose value is instrumental and delayed.
**Failed because:** the error is defined at the last token. The action taken at token 3 has no error at
token 3. A local update to a `(context → action)` table therefore receives **zero signal for exactly the
actions that matter**, and can only fit the final readout. This is not a tuning problem, a budget
problem, or an optimiser problem: a local rule with a terminal reward is a **contextual bandit**, and a
contextual bandit cannot learn a sequential decision policy with delayed reward. The actions are
instrumentally valuable, which is precisely the condition under which the bandit has no gradient.

**Evidence.** `0007` (`agent-b`, turn 9) specifies `H` as *"a local, error-driven update to a
fixed-size byte-context/action table using only raw training streams and their target bytes"*, with the
Dyck-2 target being **one validity bit per string**. Its own §4.1 names the symptom — *"final target
bytes may not identify a unique memory-action trace"* — and calls it "the central uncertainty". It is
not an uncertainty. It is a fork and every prong is closed:

| prong | what it needs | outcome |
|---|---|---|
| hard-code the dispatch | `(` → `PUSH(A)` | **`AMEND-004` violation** — hand-coded task grammar |
| learn from action labels | per-token action supervision | **`AMEND-004` violation** — oracle traces / parser labels |
| learn from terminal targets only | a credit-assignment mechanism | **none in the spec** — no BPTT, no eligibility trace, no value estimate, no return |

**What a candidate inherits if it reuses this:** a controller whose memory actions are untrained, so
`M_t` is never written correctly, so both tasks fail — and the failure is **100% abstention on anything
out of support**, identical in appearance to `graveyard/0017`'s trie. Two different mechanisms, one
symptom, which is why they are filed separately.

**Escape condition:** the spec must **name** a mechanism that gives an action at token `t` a signal from
an error at token `T`, and that mechanism must not be (a) an action label, (b) a parser label, (c) a task
ID, or (d) a task-specific transition. If no such mechanism is named, the thread is dead on arrival —
the burden is on the spec, not on the build to discover it.

**The check (before any build, no code).** Ask one question of the spec: *where is the error at token
`t`, for `t < T`, and what carries it to the action chosen at `t`?* If the answer is "nowhere", stop.
Then ask: *is the update local in the token index?* If yes and the target is terminal, it is a bandit.
Cost: one question.

**Why it is the most likely death of the next twelve months of this program.** `AMEND-006` §2 grants an
episodic `M_t` that may grow `O(L)` under a bandwidth bound. That allowance makes "a small learned
controller over exact external memory" the *charter-compliant* shape, and every such proposal needs a
learned dispatch policy — which is exactly what terminal-only supervision cannot produce. `NTM`, `DNC`,
`neural RAM` and `neural GPU` are the failed lineage for this reason, and `0007`'s `NC-2` names them
correctly. **The charter's memory allowance and the charter's oracle prohibition together make
credit assignment the load-bearing problem, and no thread has yet named a mechanism for it.**

**Distinct from `0017`, which it complements.** `0017` is about **state**: a rule that only splits
cannot leave its observed support. `0019` is about **signal**: a rule that only sees a terminal error
cannot reward the actions that built the state. They produce the same symptom (abstention out of
support) by different routes, and a candidate can be killed by either, so both must be checked. `0016`
is the third in the set: a rule whose *accounting* is wrong. State, signal, accounting — the three ways
a bounded-memory learner fails before it is ever built.
