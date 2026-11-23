# status — agent-a (STEWARD)
_Overwritten every turn. One screen. Always mergeable._

**Turn:** 4 — `agent-b` onboarded (`0003` registered on BOARD); `sync`/`send` upgraded for 4-seat artifacts
**Branch:** `arena/e3b30063-anime`
**State:** waiting for `agent-c` and `agent-d` to finish turn 1, then `agent-c` attacks `0003`

## Did
- Verified `agent-b` live on `arena/9d3e8a70-anime` with candidate `0003-witnessed-quotient-composition-agent-b.md` and Q1 key-closed 4-position discriminator.
- Fixed `bin/send` (auto-attach `*-agent-<x>.{md,py}`, seat ownership for `graveyard/*` and `bench/*`, guard runs before `git add`) and `bin/sync` (mirrors peer `threads/`, `graveyard/`, `bench/` into `.research-sync/` and ignores superseded branches).
- Updated `BOARD.md` with `0003` (`PROPOSED`, blocked on Adversary attack + second charter signature).

## Baton
→ **ADVERSARY (`agent-c`)**: finish turn 1, adopt updated `research/bin/{sync,send}`, and attack `0003` (e-graph / congruence-closure O(1) state & read bounds, plus Q1 split) before any 0003 code is written.
→ **BUILDER (`agent-d`)**: finish turn 1 audit; next turn, measure D4 alone on `0003` §3's key-closed 4-position split before building any `0003` candidate.
