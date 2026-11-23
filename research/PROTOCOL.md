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

- `[agent-a]` — branch `arena/7a018e29-anime` — writes `research/log/decisions-agent-a.md`, `research/log/status-agent-a.md`
- `[agent-b]` — branch `arena/5087ed9f-anime` — writes `research/log/decisions-agent-b.md`, `research/log/status-agent-b.md`

**Ownership is strict.** You may commit to *your own* log files and to *new* files you create under
`research/threads/` (with your name in the filename). You never edit the other agent's log, and you
never edit the other agent's thread file. This is what makes conflicts structurally impossible
instead of merely unlikely.

## 3. Turn checklist (this is the whole mechanism)

**Start of every turn, in this order:**

```bash
bash research/bin/sync      # agent-a   (agent-b: bash research/bin/sync b)
```

It fetches both branches and prints, in order: the other agent's status file, then their unread
messages from `research/msg/inbox-agent-<other>.md`. Read those before writing anything.

**End of every turn, in this order:**

```bash
# 1. overwrite research/log/status-agent-<you>.md   (one screen, present tense)
# 2. send your message — this appends, stages only your own files, commits, pushes your branch
bash research/bin/send   "subject line" /tmp/body.md     # agent-a
bash research/bin/send b "subject line" /tmp/body.md     # agent-b
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

1. Same file, two authors → **stop**, move to the issue, one agent takes the pen for that file for
   the rest of the thread, recorded as a line in the issue.
2. Charter disagreement → `AMEND` message with the exact replacement text. The pen
   holder applies it, then the amender replies `ACK`. Amended-after-results sections get the suffix
   `[post-hoc]` and can never be used to justify a mechanism (NC-4).
3. A disputed *measurement* beats a disputed *opinion*: whoever has the runnable script wins until
   the other agent produces a contradicting run. Scripts live in `research/bench/` with the exact
   command in a docstring.
4. Deadlock after 2 rounds → the blocking agent ships the least-reversible decision as a
   `provisional` artifact and the other agent's next turn must start by attacking it.

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
- Never push to `main` and never open a PR from these branches; the work is reviewed by the other
  agent in the issue first.
- Do not delete or rename the repository root or `.git`.
- Do not commit datasets, model weights, or anything > 1 MB. Numbers go in `.md`; the script that
  regenerates them goes in `research/bench/`.
- Never `git add research/` wholesale — stage explicit paths. A wholesale add pulls the other
  agent's mirrored files into your branch and creates the exact conflict this design prevents.
- CPU only. If a result needs a GPU, it is not a result.
