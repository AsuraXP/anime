# threads/

One file per candidate primitive: `NNNN-<slug>-agent-<x>.md`.

**Owner:** the INVENTOR (agent-b) writes them. **The ADVERSARY attacks them in its own file**, never
by editing the Inventor's thread. **The BUILDER** writes numbers into `bench/`, and links them from
a `## MEASURED` section appended by the Inventor.

## Rules that are not negotiable

1. **A falsifier exists before any code.** Section 4 of `templates/PROPOSAL.md`. A number, a metric,
   and an exact command. "It would be interesting to see whether…" is not a falsifier.
2. **One candidate per turn.** Four half-built ideas are worth less than one that can be killed.
3. **A killed candidate stays.** Append `## KILLED BY` with the graveyard file or the fired falsifier
   and one paragraph on why. Do not delete. The graveyard is the only asset that compounds.
4. **No candidate is `post-hoc`-load-bearing.** If the mechanism changed after a failing result, label
   it and it cannot be the reason the thing works (NC-4).

## Status line (required, first 3 lines)

```
**Status:** DRAFT | CLEARED-TO-BUILD | MEASURED | DEAD | PARKED
**Owner:** agent-<x>
**Falsifier:** <one line, plus command>
```

`research/bin/board` reads that line, so a thread without it shows up as `NO STATUS LINE` on the
board — which is the polite version of being called out.
