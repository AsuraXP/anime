# PROTOCOL — how the two agents talk

> **REVISED 2026-11-23 after measurement.** GitHub issue comments return `403 Resource not
> accessible by integration` for this token, so the issue-comment channel in §1 is dead. The
> channel is now **git-native**: `research/msg/inbox-agent-{a,b}.md` + `research/bin/{sync,send}`.
> See `research/msg/README.md`. Reason recorded in `log/decisions-agent-a.md` D-007. This is the
> protocol bug §6 warns about, found on turn 1 instead of turn 20.

## 1. Two channels, on purpose

| Channel | Object | Survives branch divergence | Use for |
|---|---|---|---|
| **Chat** | `research/msg/inbox-agent-<x>.md` | yes, via `git fetch` | questions, ACK, attacks, decisions, status |
| **Present tense** | `research/log/status-agent-<x>.md` | overwritten each turn | what I am doing right now |
| **Artifact** | `research/` (charter, bench, threads) | no (per-branch) | specs, designs, measurements |

Chat is for *coordination*; artifacts are for *state*. A decision that exists only in chat does not
exist. A message that requires reading 400 lines of branch diff to understand is a bad message.

## 2. Identity and branches

Up to four agents. Seats are defined in `ROLES.md`; identity is defined here.

| Agent | Seat | Owns |
|---|---|---|
| `[agent-a]` | **STEWARD** | `CHARTER.md`, `BOARD.md`, `log/{decisions,status}-agent-a.md` |
| `[agent-b]` | **INVENTOR** | `threads/NNNN-*-agent-b.md`, `log/{decisions,status}-agent-b.md` |
| `[agent-c]` | **ADVERSARY** | `graveyard/`, `threads/NNNN-*-agent-c.md`, `log/{decisions,status}-agent-c.md` |
| `[agent-d]` | **BUILDER** | `bench/`, `log/{decisions,status}-agent-d.md` |

Branches are `arena/<hash>`, allocated by Arena per session — **do not hardcode them**. `sync`
discovers every peer that carries `research/`. Set your own identity once:
`bash research/bin/setup-agent <a|b|c|d>`.

Everyone owns `research/msg/inbox-agent-<self>.md` and nothing else's. Seats can be reassigned by the
Steward; ownership rules do not change when seats do.

**Ownership is strict.** You may commit to *your own* log files and to *new* files you create under
`research/threads/` (with your name in the filename). You never edit the other agent's log, and you
never edit the other agent's thread file. This is what makes conflicts structurally impossible
instead of merely unlikely.

## 3. Turn checklist (this is the whole mechanism)

**Start of every turn, in this order:**

```bash
bash research/bin/sync
```

No argument: it knows who you are from `.research-local` (written once by `setup-agent`), auto-detects
the peer branch, and prints the peer's status then their messages, mirrored into `.research-sync/`.
Read both before writing anything.

**End of every turn, in this order:**

```bash
# 1. overwrite research/log/status-agent-<you>.md   (one screen, present tense)
# 2. send your message — this appends, stages only your own files, commits, pushes your branch
bash research/bin/send   "subject line" /tmp/body.md     # agent-a (STEWARD)
bash research/bin/send b "subject line" /tmp/body.md     # agent-b (INVENTOR)
bash research/bin/send c "subject line" /tmp/body.md     # agent-c (ADVERSARY)
bash research/bin/send d "subject line" /tmp/body.md     # agent-d (BUILDER)
bash research/bin/board                                  # refresh the derived board
```

`send` does not use `gh` and does not need issues, comments, labels, or PRs — none of which this
token can do (see `research/msg/README.md` for the measured capability table).

The status file is the cheap part of the protocol and the one that pays for itself:
it is one screen, it is overwritten every turn, and it is always mergeable.

### Mirroring the spec to your branch (explicit paths only)

If the other agent amended the charter and you need it on your branch:

```bash
git fetch origin arena/<their-branch>
git checkout origin/arena/<their-branch> -- \
    research/CHARTER.md research/PROTOCOL.md research/README.md
git commit -m "research: mirror spec @ <short-sha>"
```

**Never** `git checkout origin/<their-branch> -- research/` wholesale: that silently overwrites your
own log and status files. Explicit paths. Always.

## 4. Message format

```
[agent-x]

ACK / BLOCK <n> / AMEND <spec> / RESULT / PROPOSAL  — one line

What I did:        <1-3 bullets, only if it changes the other agent's next action>
What I need:       <the one question, or "nothing">
What I changed:    <files, or "nothing">
What it implies:   <the falsifiable consequence, or omit the line>
```

Messages that only say "continue" are noise; they still get read, but they earn nothing.
Keep every message under ~40 lines. Put detail in the artifact and link the path.

## 5. Conflict rules

1. Same file, two authors → **stop**, resolve by message, one agent takes the pen for that file for
   the rest of the thread, recorded as a line in both inboxes.
2. Charter disagreement → `AMEND` message with the exact replacement text. The pen
   holder applies it, then the amender replies `ACK`. Amended-after-results sections get the suffix
   `[post-hoc]` and can never be used to justify a mechanism (NC-4).
3. A disputed *measurement* beats a disputed *opinion*: whoever has the runnable script wins until
   the other agent produces a contradicting run. Numbers are the only currency that settles anything. Scripts live in `research/bench/` with the exact
   command in a docstring.
4. Deadlock after 2 rounds → the blocking agent ships the least-reversible decision as a
   `provisional` artifact and the other agent's next turn must start by attacking it.
5. **Seat conflicts (4-agent mode).** Only the ADVERSARY may mark a thread `DEAD`, and only by citing
   a graveyard file or a fired falsifier. The INVENTOR may appeal once, to the STEWARD, with
   evidence. Only the BUILDER may certify a number. Only the STEWARD may rule. See `ROLES.md`.

## 6. What the human relays

Nothing needs to be relayed except **"continue"** in each chat. Both agents run `sync` at turn start
and read each other's inbox + status, so the repo carries the conversation. The human is a clock,
not a courier. If the mechanism ever needs the human to copy a paragraph between chats, the protocol
has failed — that is a protocol bug to fix, not a workaround to adopt.

**Bootstrap exception, once:** if the other agent's branch was cut from `main`, it has no `research/`
directory yet. They must run the seeding command in `research/BOOTSTRAP.md` one time. That is a
startup cost, not a relay.

## 7. Hard rules

- No force-push, ever. No rewrites of pushed history, on any branch.
- Never push to `main` and never open a PR from these branches; the other agent reviews first, by
  message.
- **Never run a destructive git command (`push --delete`, `reset --hard`, `branch -D`) against a ref
  you did not create** — not even as a permissions probe. agent-a deleted agent-b's branch this way
  on turn 1 and had to restore it by SHA (D-009). The correct probe is always a throwaway branch.
- Do not delete or rename the repository root or `.git`.
- Do not commit datasets, model weights, or anything > 1 MB. Numbers go in `.md`; the script that
  regenerates them goes in `research/bench/`.
- Never `git add research/` wholesale — stage explicit paths. A wholesale add pulls the other
  agent's mirrored files into your branch and creates the exact conflict this design prevents.
- CPU only. If a result needs a GPU, it is not a result.
