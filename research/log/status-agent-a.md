# status — agent-a (STEWARD)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 2 — team structure
**Branch:** `arena/e3b30063-anime`
**State:** seats defined and verified; **signature gate still open**; two seats vacant

## Did
- `ROLES.md` — 4 seats with separated powers and explicit "may never" lists. Principle: nobody who
  invents a thing also grades it.
- `SEATS.md` — one paste-block per agent; give each agent only its own.
- `BOARD.md` + `bin/board` — the table in one screen; the factual half is derived from filenames so
  it cannot quietly lie.
- `sync` now discovers peers by finding an inbox file, not by guessing branch names (Arena allocates
  a fresh hash per session). Verified with 4 simulated peers on throwaway branches, then deleted.
- `graveyard/` created and seeded with 5 measured walls. `threads/` rules tightened.

## Blocked on
- **INVENTOR (agent-b)**: first turn = attack Q1 with a real falsifier + exactly one candidate thread.
- **Human ruling needed**: add agent-c (ADVERSARY) and agent-d (BUILDER), or record that we run at 3.

## Baton
→ INVENTOR for Q1 + one thread. → STEWARD next turn: close the signature gate, rule on team size.

## Not touching
No candidate code until a second signature exists. No edits to another seat's files.
