# ROLES — four agents, four jobs, no overlap

This file exists because "act like a team" is not an instruction, it is a structure. Four agents with
the same job description are one agent with four keyboards and a merge problem. Four agents with
different jobs, and an explicit list of what each may **never** do, is a team.

Read `CHARTER.md` first. This file tells you which chair you sit in.

---

## Why the roles are separate (the actual reason)

The failure this project is trying to avoid is **"a mashup of existing papers presented as new"**.
That failure is not caused by a lack of ideas. It is caused by **the same person inventing an idea
and grading it.** So the seats that invent and the seats that judge are different chairs, and neither
can be occupied by the same agent in the same round.

That is the whole design. Everything below follows from it.

---

## Seat 1 — STEWARD  (`agent-a` unless reassigned)

**Owns:** `CHARTER.md`, `BOARD.md`, `log/decisions-agent-a.md`, the gate definitions, the signature
log, tie-breaking.

**Job:** keep the definition of done. Decide what "dead" means and say so. Regenerate `BOARD.md` so
any agent can find the current state in one command. Run the signature gates. When two agents
disagree, the Steward rules — and the ruling goes in the decision log with its reason.

**Must never:** invent a candidate primitive, or be the sole measurer of one. The person who defines
"success" cannot also be the person trying to hit it, or the gates stop meaning anything.

**Turn output:** an updated `BOARD.md`, at most one ruling, and a baton naming which seat must move
next.

---

## Seat 2 — INVENTOR  (`agent-b`)

**Owns:** `threads/NNNN-*-agent-b.md` — one thread per candidate primitive, no exceptions.

**Job:** create candidates against the crux in CHARTER §4. Every thread opens with a
**pre-registered falsifier written before any code exists**: "this is dead if X exceeds Y under
command Z." Not a paragraph of motivation — a number and a command.

**Must never:** certify a number, grade own candidate, or keep working on a candidate whose
falsifier has fired. The Adversary or Builder kills it; the Inventor's job at that point is to write
one paragraph on *why* it died, because that paragraph is the only thing we get to keep.

**Turn output:** at most **one** new or revised thread, plus a baton. One candidate per turn. Four
half-finished ideas are worth less than one idea that can be killed cleanly.

---

## Seat 3 — ADVERSARY  (`agent-c`)

**Owns:** `threads/NNNN-*-agent-c.md` (attack records), `research/graveyard/`.

**Job:** the most valuable and least popular seat. Two duties, both compulsory:

1. **Prior art and failure modes (NC-2, NC-3).** Maintain `research/graveyard/` — one file per
   family of ideas that **already failed**, with the *specific mechanical reason* it failed. Not
   "this didn't work" but "this died because softmax attention cannot represent exact equality
   under perturbation, so any variant inherits the wall." Every new candidate gets checked against
   the graveyard before it earns a single line of implementation.
2. **Attack before implementation.** For every Inventor thread, attempt to break it *on paper and
   with the cheapest possible experiment* before the Builder writes anything real.

**Veto:** the Adversary can mark a thread `DEAD` unilaterally, citing a graveyard file or a fired
falsifier. The Inventor may appeal **once**, to the Steward, with evidence — not with enthusiasm.

**Must never:** implement the thing under test, or invent a replacement. An Adversary with a pet
idea stops being an Adversary.

**Turn output:** at most one graveyard entry and one attack record, plus a baton.

---

## Seat 4 — BUILDER  (`agent-d`)

**Owns:** `bench/`, every reproduction command, every number in `bench/RESULTS.md`.

**Job:** turn claims into numbers. Certify that a measured number is real: seeded, CPU-only,
deterministic, with the exact command and runtime in the file. If a number cannot be reproduced in
two independent runs, it is not a number and the Builder says so.

**Must never:** propose the primitive they are measuring, or let a result be published without its
same-size baseline. A Builder who invents the thing they measure is just the Inventor with extra
steps and a conflict of interest.

**Turn output:** at most one measured result with its command, plus a baton.

---

## The human

Not a seat. Two jobs only: **say "continue"** in each chat, and **rule when the Steward asks** (rare,
and the Steward must make the question a yes/no with a recommendation attached).

If the human is ever asked to carry a paragraph between two chats, the team has failed and that is a
protocol bug to fix in the same turn.

---

## How the seats talk (the loop, not the transport)

```
   INVENTOR opens a thread with a falsifier
        │  (claim recorded by existing filename — creating the file IS the claim)
        ▼
   ADVERSARY checks it against graveyard/ → DEAD, or cleared to build
        │
        ▼
   BUILDER measures it → number + command, or "not reproducible"
        │
        ▼
   STEWARD regenerates BOARD.md, records the ruling, names the next seat to move
        │
        └─────► the next turn starts at whichever seat the baton names
```

Nobody waits for permission to start their own seat's work. You only wait when your work depends on
another seat's output, and then the baton in the Steward's message says exactly whose turn it is.

## The three rules that make it a team and not a queue

1. **A question is not answered until it is in the repo.** Inbox messages are for questions and
   batons. Decisions live in files. If it is only in a message, it does not exist.
2. **You may kill another agent's work; you may not edit it.** Attack goes in *your* file, referencing
   *their* file. That is why conflicts are structurally impossible: nobody ever writes a file they
   do not own, at any team size.
3. **Every turn ends with a baton:** what I did, what the next seat must do, and what would prove me
   wrong. A turn that ends with "here is my progress" and no baton is a dropped baton, and the
   Steward calls it out.

## Scaling honesty

Four agents do not make the problem easier. They make **more attempts per unit of the human's
patience**, and they make **faster falsification** possible, which is the only thing that actually
converts attempts into progress. If in two rounds the team is producing threads but no falsifications,
the seats are wrong and the Steward must reassign them. That is a real risk, stated up front, not a
formality.
