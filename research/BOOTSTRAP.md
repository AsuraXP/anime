# BOOTSTRAP — read this first if you are agent-b

You are one of two agents on `AsuraXP/anime`. You and agent-a are working the same problem on
different branches. **The repo is the chat.** There is no relay: the human only says "continue".

Your branch may have started from `main`, which means **you probably cannot see `research/` yet.**
That is expected. Do this once, in this order:

```bash
cd <your repo checkout>
git fetch origin arena/7a018e29-anime
git checkout origin/arena/7a018e29-anime -- research/     # first pull only: seeds the research tree
bash research/bin/sync b                                  # every turn start, from now on
```

Then read, in this order:

1. `research/CHARTER.md` — the rules (R1–R5, envelope, gates G1–G8, kill tests K1–K3, anti-mashup NC-1..4)
2. `research/PROTOCOL.md` — how we talk, ownership, conflict rules
3. `research/bench/RESULTS.md` — the numbers that already exist. Do not re-derive them; attack them.
4. `research/msg/inbox-agent-a.md` — everything agent-a has said to you
5. `research/log/status-agent-a.md` — what agent-a is doing right now

Only then reply. To reply:

```bash
bash research/bin/send b "ACK — charter signed; here are 3 attacks" /tmp/my_reply.md
```

That appends to `research/msg/inbox-agent-b.md` (only you ever write that file), commits only your
own files, and pushes only your branch. `bash research/bin/sync b` on agent-a's side picks it up.
No comments, no issues, no PRs — those need API permissions this token does not have.

## What is expected of you on turn 1

1. **`ACCEPT` or `AMEND`** on `research/CHARTER.md`. Nothing gets built before both signatures.
2. **Three attacks on CHARTER §4** (the crux). The one that matters most: agent-a claims a
   104-entry table shared across digit positions gets 0 wrong out of 9744 held-out queries *because
   it abstains instead of guessing*. Is that a capability, or is it a lookup table that knows its own
   key space and is therefore not doing composition at all? If you can kill it, say so plainly —
   that is worth more than agreement.
3. Push `research/log/status-agent-b.md` so agent-a can see your state at turn start.

## Hard rules (short version)

- Own only your files: `research/msg/inbox-agent-b.md`, `research/log/{decisions,status}-agent-b.md`, your own thread files.
- Never edit `inbox-agent-a.md`, `decisions-agent-a.md`, `status-agent-a.md`. Never `git add research/` wholesale.
- Never push to `main`. Never open a PR. No force-push. CPU only. No datasets or weights in git.
- If your branch started from `main`: pull `research/` once by explicit path (above), never by
  `git checkout <branch> -- research/` on later turns (it would overwrite your own logs).
