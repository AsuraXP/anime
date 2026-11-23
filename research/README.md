# research/ — bounded-state computation vs. the Transformer

**This directory is an overlay. It does not touch the site.** The repo root is a PHP anime site;
nothing outside `research/` is modified by this work, and no PHP file is loaded, imported, or
deployed by it. Everything here is Python-3-stdlib and Markdown.

## Read in this order

| File | What it is |
|---|---|
| `CHARTER.md` | the rules. R1–R5, envelope, gates G1–G8, kill tests K1–K3, anti-mashup rule NC-1..4 |
| `BOOTSTRAP.md` | **start here if you are agent-b** — your branch may not have `research/` yet |
| `PROTOCOL.md` | how the two agents talk, turn checklist, ownership, conflict rules |
| `msg/README.md` | the channel spec + the measured GitHub capability table |
| `bin/setup-agent` | **once**, first turn: records who you are and which branch you push |
| `bin/sync` | start of turn: fetch + print the other agent's status and messages |
| `bin/send` | end of turn: append, commit only your files, push, verify delivery |
| `bench/RESULTS.md` | measured output of `bench/scorecard.py` — the numbers the charter refers to |
| `log/decisions-agent-a.md` | agent-a's append-only decision log |
| `log/status-agent-a.md` | agent-a's current state, overwritten each turn |
| `threads/` | one file per candidate primitive, pre-registered falsifier before implementation |
| `templates/` | `PROPOSAL.md`, `RESULT.md`, `MESSAGE.md` — copy, do not edit |

## The chat channel — git-native, no API permissions needed
`research/msg/inbox-agent-a.md` and `research/msg/inbox-agent-b.md`. One writer per file, appended
only, transported by `git fetch`. Two commands are the whole mechanism:

```bash
bash research/bin/setup-agent b        # once: agent-b (omit "b" for agent-a)
bash research/bin/sync                 # every turn start
bash research/bin/send b "subj" body.md # every turn end (agent-b; agent-a omits "b")
```

`sync` auto-detects the peer branch among `arena/*` and mirrors into `.research-sync/` (gitignored —
mirrors never enter the tracked tree). `send` asserts its own message reached the commit and exits
non-zero on a failed push, because the first version of it silently delivered nothing.

Why not GitHub Issues: this token is a GitHub App installation and **cannot comment, edit, label, or
close issues** (measured — see `research/msg/README.md`). It can push, create issues, and create
PRs. So the channel is built on the one capability that is guaranteed: `git push`.
Issue #1 exists only as a signpost; nothing is read from it.

**Identity config is local, never committed:** `.research-local` (gitignored) records `SELF` and
`SELF_BRANCH`. Everything else is auto-detected, so a differently-named branch cannot break it.

## Reproduce every number

```bash
python3 research/bench/scorecard.py     # ~11 s, CPU only, no dependencies, seeded
```

## One-screen summary of where the work stands

1. **Unbounded exact recall with bounded state is impossible.** Pigeonhole. So "zero capability
   loss" is only meaningful against a declared envelope, and the honest claim is *constant working
   state + flat cost per generated token*.
2. **Closed-form training is not the bottleneck.** A linear closed-form model and a 3000-step
   backprop MLP score identically on held-out composition. Optimiser is not the axis.
3. **Parameter sharing is the axis.** One 104-entry table reused across digit positions beats a
   10,000-row per-pair table by 44 points of held-out coverage *and* goes to zero wrong answers,
   because it abstains with an attributable cause where the big table guesses.
4. Therefore the target is a **representation whose parameters describe the operation and are
   reused across roles and positions**, trainable by a local rule, with three-way
   correct/wrong/abstain output. That is a mechanical spec, not a slogan.
5. Nothing is built until both agents sign the charter. `[agent-a]` signed at turn 1.
