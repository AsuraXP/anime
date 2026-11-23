# research/log/decisions-agent-a.md
Append-only. **Owned by agent-a. agent-b: read-only.** Newest at the bottom.
Decisions that exist only in issue chat do not exist; they get a line here.

---

## D-001 · 2026-11-23 · Channel = issue #1, state = repo artifacts
Chat lives on GitHub issue #1 (not branch-scoped, so both branches see the same thread).
Durable state lives in `research/` with one log file per agent, so a rebase or branch divergence
cannot lose or conflict the conversation. Rationale: conflict is *structurally* impossible if
nobody writes a file they do not own.

## D-002 · 2026-11-23 · "Zero capability loss" is scoped to a declared envelope
Unscoped, R4 is impossible (pigeonhole + energy, `bench/RESULTS.md` §A). Impossibility is not a
reason to stop; it is the reason to declare E-RECALL / E-COMPOSE / E-EDIT before building, and to
report the out-of-envelope gap rather than hide it. Adopted as CHARTER §1, incl. the refusal clause.

## D-003 · 2026-11-23 · R2 is claimed over *working state*, not over the store
Bounded RAM + addressable store is the only physically possible reading. The claim is made
falsifiable by G3/G4 (per-token cost and per-token reads must be flat in n), which specifically
kills "constant RAM, O(n) reads" i.e. a cache with extra steps.

## D-004 · 2026-11-23 · My own pre-registered prediction was falsified and kept
Predicted in-code that a bilinear table over one-hot pairs would generalise perfectly because it
"tables the operation not the data". Measured held-out 11.8% (=chance). Recorded as falsified in
`bench/RESULTS.md` §D rather than rewritten. This is NC-4 working as intended; expect it to keep
hurting and keep publishing.

## D-005 · 2026-11-23 · Generalisation axis identified: parameter sharing, not trainer
D1 (linear, closed form) and D3 (MLP, 3000 SGD steps) score *identically*. Adding backprop bought
nothing. D4 [post-hoc] reused ONE 104-entry table across digit positions and got 55.7% held-out
coverage with **0 wrong out of 9744** — because it abstains instead of guessing. Therefore:
(a) the search axis is representation/sharing, not optimisation; (b) adopt three-way
correct/wrong/abstain as G8; (c) D4 is post-hoc and cannot be the load-bearing term (NC-4).

## D-006 · 2026-11-23 · No implementation hours before both signatures
agent-a will not write candidate code until agent-b posts ACCEPT or AMEND on the charter. The point
of two agents on one problem is that one of them is allowed to say "this is a nicer-sounding
straw man", and it costs nothing to wait one turn for that.
