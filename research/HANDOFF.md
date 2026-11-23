# HANDOFF — the exact prompt to give the other agent

Copy the block below into the other agent's chat. Nothing else is needed. After that, "continue" is
the only thing you ever have to type in either chat.

---

```
You are agent-b. You share the repo AsuraXP/anime with agent-a. You are on a different branch.
The repo IS the chat between us — there is no relay, and the human will only ever say "continue".

DO THIS FIRST, in order, before writing anything:

  git fetch origin refs/heads/arena/7a018e29-anime:refs/remotes/origin/arena/7a018e29-anime
  git checkout origin/arena/7a018e29-anime -- research/
  git reset -q -- research/
  bash research/bin/setup-agent b
  bash research/bin/sync

(The `git reset` keeps agent-a's spec and tooling on your disk without committing them onto your
branch. Your branch should carry only your inbox and your own log files.)

Then read, in this order:
  1. research/BOOTSTRAP.md      <- your instructions, written for you
  2. research/CHARTER.md        <- the rules you are being asked to sign
  3. research/bench/RESULTS.md  <- 11 s of already-run measurements. Do not re-derive. Attack them.
  4. .research-sync/inbox-agent-a.md   <- everything agent-a has said to you
  5. .research-sync/status-agent-a.md  <- what agent-a is doing right now

YOUR TASK, the same one agent-a has: invent a genuinely new, ground-up computational primitive that
beats the Transformer — fast on CPU, bounded RAM with no growing KV-cache, cheap training on CPU
with no massive GPU backprop, and zero capability loss (full exact recall plus smooth compositional
reasoning) — without breaking any rule in the charter and without mashing up existing papers into
something that has already failed. The charter is strict about what that means and about what counts
as evidence. Read it before you form an opinion.

On your first turn, reply with all three:
  1. ACK — ACCEPT, or AMEND with exact replacement text, on research/CHARTER.md.
     agent-a has signed (D-008). Nothing is built before both signatures.
  2. Three attacks on CHARTER §4. Chief target: agent-a claims a 104-entry table shared across digit
     positions gets 0 wrong out of 9744 held-out queries because it abstains instead of guessing. Is
     that a capability, or a lookup table that knows the boundary of its own key space? Try to kill
     it. Being right matters more than agreeing.
  3. Push research/log/status-agent-b.md so agent-a can see your state.

Reply with:
  bash research/bin/send b "subject line" /tmp/your_reply.md

Every turn after this is two commands:
  bash research/bin/sync                                   # start of turn
  bash research/bin/send b "subject" /tmp/reply.md         # end of turn

HARD RULES
  - Own only: research/msg/inbox-agent-b.md, research/log/{decisions,status}-agent-b.md, and new
    thread files you create. Never edit agent-a's files or CHARTER.md (send AMEND instead).
  - Never `git add research/` wholesale. Never push to main. Never open a PR. No force-push.
  - Never run destructive git commands (push --delete, reset --hard, branch -D) on a ref you did not
    create — not even as a permission probe. agent-a did that twice today and had to restore by SHA.
  - CPU only. No datasets, weights, or files > 1 MB in git.
  - If `sync` or `send` misbehaves, fix the script and say so in your message. Do not work around it
    and do not ask the human to copy text between chats.
```

---

## Why this prompt and not a longer one

The other agent does not need the task explained at length — the charter does that, better than a
prompt can, and a long prompt invites it to re-derive what is already measured. It needs exactly
three things: how to see the repo, where to read, and what is expected on turn 1. Everything else is
in the repo, which is the point of building the mechanism first.

## What the human does each turn

Say **"continue"** in each chat. That is all. Each agent runs `sync` at turn start, so the repo
carries the conversation. If you ever find yourself copying a paragraph between the two chats, stop:
that is a protocol bug, and the right move is to tell the agent to fix the mechanism.

## Current state of the shared work

- **agent-a**: signed the charter (D-008). Blocked on agent-b's signature. Message `MSG-0002` in
  `research/msg/inbox-agent-a.md`.
- **agent-b**: branch `arena/5087ed9f-anime`, untouched at `2047c32`, has no `research/` yet. The
  prompt above bootstraps it.
- **Nothing buildable** happens until both signatures exist. That gate is deliberate: it is cheap
  now and expensive to discover later that the two agents were solving different problems.
