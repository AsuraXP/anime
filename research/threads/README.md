# threads/

One file per candidate primitive: `NNNN-<slug>.md`. Copy `templates/PROPOSAL.md` into a new file.
Author's name goes in the filename if two threads could collide (`0002-hash-chains-agent-b.md`).

Rules:
- Ownership: the author owns their thread file; the other agent attacks it **in issue #1**, not by
  editing the file. The author applies accepted changes.
- No candidate is implemented before its §4 falsifier exists.
- A killed candidate stays in the file with a `## KILLED BY` section. Do not delete threads —
  the graveyard is what stops re-inventing the same failure two turns later.
