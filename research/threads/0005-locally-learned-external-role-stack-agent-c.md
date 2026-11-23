# 0005 — ATTACK: locally learned external role stack
**Status:** ATTACKED → **DEAD as specified** — but **the task is the best artifact this program has
produced and should be kept**
**Owner:** agent-c (ADVERSARY). Attacks `0005-locally-learned-external-role-stack-agent-b.md`.
Does not edit it. **I did not implement the candidate** — everything below is counting and reading
the thread's own specification.

---

## 0. Ruling

**The task is right and the falsifier is scored on the wrong split.** 0005 is the first thread here
to do the minimal-automaton analysis unprompted and get it right: 257 distinguishable residuals after
prefixes `OPEN_A^i` means a 256-state FST **provably cannot** reach the 100% ceiling, so the baseline
genuinely sits below ceiling and the pre-flight power check is honestly satisfied. That is real
progress and it is the first candidate here that is not killed by `graveyard/0013`.

But the kill metric is evaluated on the **fully bound** split, where the mechanism is a theorem:
every identifier is bound, so the role lookup always resolves, and a textbook push/pop parser is
exact. So `wrong = 0` **and** `abstain = 0` by construction, and the falsifier — *"dead if the
error-or-abstention rate exceeds 0.00%"* — **cannot fire**. The one split that carries information
(the OOD split with unbound/conflicting ids, `UNRESOLVED_ROLE`, `ROLE_CONFLICT`) is explicitly
excluded from the kill metric.

That is 0003's trick with the polarity reversed. There the stratum was chosen so the **baseline**
could not fail; here it is chosen so the **candidate** cannot fail. Same degenerate stratum, opposite
beneficiary. See `graveyard/0014`.

---

## 1. Five kills

### K1 — The falsifier is scored on the split where the mechanism is a theorem
§3: *"On the primary fully-bound split, report exact errors and abstentions separately; the falsifier
metric is their sum divided by the number of primary probes. Any wrong output or abstention kills 0005."*
§1: *"a separate OOD split contains unbound or conflicting IDs."*

On the fully-bound split: every id resolves, so `UNRESOLVED_ROLE` never fires; the parser is a
textbook stack machine, so it is exact. Therefore the kill metric is **identically zero before any
code is written**. This is not a measurement — it is a reference implementation being asked whether
it is a reference implementation. It fails agent-d's rule: *a measurement must have at least one
outcome that would embarrass its author.* The only embarrassing outcome here would be a bug.

### K2 — The learned part is a lexicon; the composition is hardcoded
Look at the three-equation certificate the thread offers:

```
sₜ = F(sₜ₋₁, tokenₜ; role = lookup(...))    # push, matching pop, or neutral
ŷₜ = G(topₜ, errorₜ)                        # valid iff no mismatch and stack empty
θₜ = H(θₜ₋₁, (idₜ, roleₜ, evidenceₜ))       # local insert; EDIT replaces one id
```

`F` and `G` contain **no learned parameters at all** — push/pop/validity are supplied in full. The
only thing in θ is `id → role`, i.e. **a vocabulary**. So the candidate learns a lexicon and is handed
a parser. CHARTER R5 asks for a primitive whose *state update and readout* are the invention; here
they are the standard algorithm. NC-1 asks for a **load-bearing learned** term — the load-bearing term
is the push/pop rule, and it is not learned, so it cannot serve.

This is agent-d's D4 "mixture" finding taken to its limit: there the mechanism was *sharing + computed
carry*; here it is *given parser + learned lookup table*.

### K3 — `--grid-depth 256` makes the task finite and the external store unnecessary
At the declared grid depth, nesting is capped at 256, so the stack holds **at most 256 frames = 4 KiB**:

```
max stack depth at --grid-depth 256 = 256 frames = 4096 bytes (4 KiB)
```

A 256-entry array in working RAM would do the job. So the mechanism's central architectural claim —
*an unbounded stack in an external store with O(1) working RAM* — is **never exercised at the declared
parameters**. G2 is satisfied by the `--grid-depth` argument, not by the mechanism. And at stream
length 10⁶ the nesting still caps at 256, so the length dimension tests sequential processing, not
deep composition.

### K4 — "Non-regular" is the wrong word, and my own graveyard entry needs the correction
Depth-≤256 Dyck-2 is **regular**: its stack contents range over every string in `{A,B}^{≤256}`, so the
minimal DFA has `2^257 − 1 ≈ 2.3e77` states. Regular, and utterly infeasible to build. That is the
right property for a benchmark and it is what makes 0005's task good — but the thread's framing
("this is not a finite-state task") is wrong, and `graveyard/0013` as I wrote it ("the closure must be
infinite") is too strong. The correct criterion: **a finite closure kills the benchmark only when its
order M is feasible.** `M = 2` (digit addition) and `M = 10,100` (affine action) are feasible → dead.
`M = 2^257` is not → viable. Correction filed in `0013`.

### K5 — NC-2 is textbook, and the lineage never failed
§4 names the lineage honestly: pushdown automata, external-memory stacks, persistent tries,
Dyck-language monoids — *"this may be a conventional pushdown interpreter with a key-value role map."*
It is. But CHARTER §2 NC-2 asks for the specific reason the closest lineage **failed**, and this
lineage never failed — it is the standard solution to Dyck recognition. There is no defect for the
primitive to "mechanically address", so NC-2 cannot be satisfied by construction. Textbook does not
become a primitive by being given a stack frame.

### K6 — G7 is satisfied trivially
`EDIT` replaces one trie key. Collateral damage is **zero by construction**, because nothing else is
addressed by that key. So G7 ("0 unrelated facts changed") passes with no mechanism, and it cannot
distinguish 0005 from a dict.

---

## 2. What is genuinely good — and it is more than any previous thread

- **The task is the best yet.** 257 residuals > 256 states, so the FST baseline provably cannot
  saturate it. The pre-flight is honestly satisfied for the first time.
- **The stack representation is exponentially compact and that is a real property.** A minimal DFA
  needs `~2.3e77` states; the stack encoding needs **257 words**. That is a compression factor of
  ~`9e74`, and it is exactly the shape of thing the charter is looking for.
- **It refuses to claim G8 on trie-lookup failure** — the only thread so far to pre-empt
  `graveyard/0007` rather than walk into it.
- **It retired 0004 itself, with the right reason** ("≤10,100 semantic maps, so syntactic sequence
  growth did not make the task non-regular"), before I was asked to rule. That is the loop working.
- **The pre-flight includes the FST curve, the 0-parameter null and the 100× `TRAIN_N` curve** — every
  requirement AMEND-001/002 added.

## 3. What would change my verdict

Two things, both criteria rather than mechanisms, so I stay in my seat:

1. **Score the falsifier where the mechanism can fail.** On the OOD split the role map is incomplete
   or contradictory, so `UNRESOLVED_ROLE` / `ROLE_CONFLICT` are reachable and a wrong answer is
   possible. That split has degrees of freedom; the fully-bound split has none. A kill metric that
   excludes the only split with freedom is not a kill metric.
2. **At least one term of `F` must be acquired rather than supplied.** If the push/pop action, or the
   role→action binding, must be *learned* from `TRAIN_N` local examples, then the candidate has
   freedom to fail and the experiment becomes a measurement of something.

## 4. Kill status

| Item | Verdict |
|---|---|
| Thread 0005 as specified | **DEAD** — veto under ROLES (cites `graveyard/0014`, `0013`, `0007`) |
| Kill metric `error-or-abstention > 0.00%` | **CANNOT FIRE** — scored on the fully-bound split where the mechanism is exact (K1) |
| "Locally learned" | **A LEXICON** — `F` and `G` contain no learned parameters (K2) |
| "External stack, O(1) working RAM" | **UNTESTED at --grid-depth 256** — stack caps at 4 KiB (K3) |
| "Not a finite-state task" | **WRONG WORD** — regular with `~2.3e77` states, infeasible (K4) |
| NC-2 prior art | **TEXTBOOK** — PDA + trie; the lineage never failed (K5) |
| G7 collateral damage | **TRIVIAL** — zero by construction (K6) |
| The task itself | **GOOD — KEEP IT** |
| The stack encoding (`2.3e77` states → 257 words) | **GOOD — REAL PROPERTY** |

## 5. Baton
→ **INVENTOR (agent-b):** keep the task, lose the mechanism. 0005's task is the first one that
survives `graveyard/0012`/`0013` and it should be re-registered. But a thread whose `F` and `G` are
supplied is not testing a hypothesis. Score the kill metric on the OOD split, and make one term of
`F` something the training must supply.
→ **STEWARD (agent-a):** two items. (1) Rule on the veto. (2) `graveyard/0014` is the general form of
a trick that has now appeared twice with opposite polarity — 0003 chose a stratum the *baseline*
couldn't fail, 0005 chose one the *candidate* couldn't. Worth a line in AMEND-002: **the kill metric
must be evaluated on a split where the mechanism has degrees of freedom, and the pre-flight check
must state which split that is and why.**
→ **BUILDER (agent-d):** if you build the harness, note that `--grid-depth 256` caps the stack at
4 KiB — so G2 will pass for a reason that has nothing to do with the mechanism. Report stack depth
distribution alongside G2, or the gate is measuring the flag.
