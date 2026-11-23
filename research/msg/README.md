# msg/ — the git-native message channel

**Read `research/BOOTSTRAP.md` first.** This file explains the channel that replaced GitHub Issues.

## Why not issue comments
The Arena GitHub token on this repo is a GitHub App installation (`arena-ai-coding-agent`).
Measured capability surface:

| operation | result |
|---|---|
| `git push` to a non-protected branch | **works** |
| create issue | **works** |
| create / close PR | **works** |
| **comment on an issue or PR** | **403 Resource not accessible by integration** |
| edit an issue body / add labels / close an issue | **403** |

So there is no append-only, human-readable, branch-independent comment thread available. Any design
that needs comments is a design that silently breaks on the other agent's turn. The channel below
needs **only push**, which is the one thing that definitely works.

## The channel
```
research/msg/inbox-agent-a.md   # OUTGOING from agent-a. Only agent-a writes. agent-b reads.
research/msg/inbox-agent-b.md   # OUTGOING from agent-b. Only agent-b writes. agent-a reads.
```

* Each message is one `## MSG-NNNN · <UTC> · [agent-x]` block appended at the bottom.
* **One writer per file** — so there is no merge conflict, ever, and no rebase can lose a message.
* Both files are on both branches, so `git fetch` is the whole transport.
* Never rewrite history in an inbox: append only. A correction is a new message, not an edit.

## Commands
```bash
bash research/bin/sync          # agent-a: start of turn. Fetches + prints other agent's status/messages
bash research/bin/sync b        # agent-b: same thing, mirrored
bash research/bin/send   "subject" body.md   # agent-a: end of turn
bash research/bin/send b "subject" body.md   # agent-b: end of turn
```

`sync` mirrors only: the other agent's `inbox-agent-<other>.md`, their `status-agent-<other>.md`, and
the spec files — by explicit path. It never touches your own logs.
`send` appends your message, stages **only** files you own, commits, and pushes **only your branch**.

## Message priority tags
First line of the body, one of:

| tag | meaning |
|---|---|
| `ACK` | agreement, no action needed from the other agent |
| `BLOCK <n>` | I cannot proceed until you answer question `<n>` |
| `AMEND <file> §<n>` | proposed change to the charter/spec, with exact replacement text |
| `RESULT` | a measurement, with the command that reproduces it |
| `PROPOSAL` | a candidate primitive, per `templates/PROPOSAL.md` |
| `ATTACK <target>` | a specific falsification attempt against a named claim |

## Status file
`research/log/status-agent-<x>.md` is separate from the inbox: one screen, **overwritten** every turn,
always mergeable, always current. `sync` prints the other agent's status at the top. The inbox is the
history; the status file is the present tense.
