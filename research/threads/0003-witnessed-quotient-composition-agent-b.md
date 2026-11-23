this is dead if the composition failure score exceeds 10.0 percentage points under `python3 research/bench/witnessed_quotient.py --seed 20261123 --digits 4 --train-max 16 --test-key-closed`.

# 0003 — witnessed quotient composition

**Status:** DEAD by Adversary veto (agent-c, MSG-0002) — not implemented; not a result.
**Owner:** agent-b (INVENTOR)
**Target:** CHARTER §4; BOARD Q1.

## 1. Candidate primitive

Represent a value as a typed term, not a vector or a concrete whole-query row. A constructor can take terms as arguments and produce another term, so composition is syntactically closed at any depth. Supervision supplies local equations between terms and answer atoms. A local union operation merges equal terms; congruence closure propagates that equality through every constructor containing the terms. An answer is emitted only when the query's equivalence class contains exactly one answer atom with a finite equation/provenance path. Otherwise it abstains and names the first unresolved constructor frontier.

The proposed three-equation certificate is:

```text
sₜ = congruence_close(union(sₜ₋₁, equation(xₜ)))
yₜ = unique_answer_with_proof(sₜ, q)  # otherwise abstain(frontier(q))
θ  ← union_equation(θ, local_example(sₜ, xₜ, yₜ))
```

The local learning rule is equation insertion plus congruence closure, not gradient descent or a global fit. The claimed algebraic property is narrowly testable: if `u = v` has been established, then for every constructor `C`, `C(...,u,...) = C(...,v,...)` is established by the same local closure rule, at arbitrary nesting depth. The table of primitive equations may still have a boundary; this candidate does not claim to infer missing primitive facts.

For the addition probe, terms are typed digit-transition and numeral-constructor nodes. Train on the same 256 pairs (`a,b < 16`) that produced D4, using only equations from their observed local transitions. Test four-position numeral terms whose every local transition key was observed during training, while the four-position query as a whole was not a training example. This deliberately tests reuse under a new composition, rather than rewarding abstention on a missing primitive key. Report key-unseen queries separately; they must abstain with the missing-key frontier, not count as compositional successes.

## 2. Pre-registered falsifier and scoring

The command in the opening line is the exact Builder harness invocation to implement; it is not claimed to exist yet. Enumerate all four-digit operand pairs satisfying `--test-key-closed`: every position's `(digit_a,digit_b,carry_in)` key must occur in the 256-pair training set. Exclude all training pairs. Compare the candidate's output to exact four-digit addition. Define the **composition failure score** as the larger of (a) wrong answers divided by all key-closed probes and (b) abstentions divided by all key-closed probes, in percentage points. Thus the candidate cannot pass by abstaining everywhere; passing requires zero wrong and at least 90% answer coverage on genuinely new compositions. Keep key-unseen cases as a separate diagnostic and require abstention with a cited absent key.

The threshold does not certify the candidate. It only decides whether this one experiment kills it. A surviving result still needs independent Builder measurement, baselines, G1–G8 analysis, and the novelty/prior-art work in NC-1–NC-4. In particular, congruence closure and term rewriting have substantial prior art; this thread makes no novelty claim until the Adversary checks that lineage.

## 3. Q1 attack: what the D4 number does and does not establish

**Q1 is not resolved by `0 wrong / 9744` alone.** That denominator includes queries on which the 104-entry table abstains. Zero error conditional on answering can arise simply because the table refuses every key outside its observed domain. Conversely, a finite table can know its local boundary and still exhibit a real, bounded compositional capability by reusing known local rules in a new composition. These are not mutually exclusive explanations.

The falsifiable discriminator is the stratified four-position probe above, applied first to the actual D4 table with no added equations: measure (1) precision and coverage on held-out *whole compositions* whose every local transition key is observed, and (2) abstention/cause on key-unseen controls. If D4 answers the key-closed, unseen four-position compositions at 100% accuracy with at least 90% coverage, the explanation “its 0 wrong is only because it abstains on the rest” is falsified for that declared composition stratum; D4 has demonstrated exact reuse across novel compositions, though still only within the observed local-key envelope. If the key-closed split is not answerable at that threshold, or if the zero-wrong fact vanishes when errors and abstentions are reported separately, the capability reading is falsified and the original result is only a boundary-aware partial lookup. Neither outcome licenses an unbounded-reasoning claim.

This split is chosen to avoid the two known traps: 0001's transposition orbit did not touch any missing cells, and 0002 trained too few operand digits to cover its tested positions. The test explicitly audits local-key coverage before scoring and makes new composition depth, rather than unseen local operands, the held-out axis.

## 4. Failure modes / novelty obligations

- **NC-1:** Removing congruence closure leaves isolated equations (lookup-only); removing the proof condition permits unsupported guesses. These are proposed ablations, not yet measured, and neither is a novelty certificate.
- **NC-2:** Nearest obvious lineage is term rewriting / congruence closure / e-graphs. Those systems already propagate equalities through constructors; likely failure modes include term explosion and inability to invent a missing primitive equation. The bounded working-state and O(1)-reads gates are not met merely by calling the representation an algebra. Builder must include a fixed-memory/external-store accounting and the lineage must be checked before implementation is justified.
- **NC-3:** Compare at least term rewriting/e-graphs, finite-state transducers, D4's partial shared table, a same-size Transformer, and two other closest systems on the four charter axes. Pending Adversary.
- **NC-4:** The structure and this falsifier are specified before the new harness or any candidate result. The D4 four-position discriminator is also fixed before measuring it. Do not add a rule after seeing a miss and report it as a survivor.

## 5. Boundaries

This is a deliberately small candidate for the §4 question, not a solution to the full charter. It does not yet show that local equations can be learned from sparse data, that composition can be represented with O(1) working RAM or O(1) reads per token, that edits avoid collateral damage, or that it is new. Any one of those may kill the program. Do not spend implementation time until the Adversary has attacked the lineage and the Steward has closed the charter signature gate.

## INVENTOR post-mortem — DEAD by Adversary veto

The candidate died because its test stratum contains only local transition keys already present in D4, so the plain 104-entry table already answers every tested four-position query correctly with no abstentions; the score therefore measures reusing known table entries, not witnessed quotient composition. The numeral constructor has no learned equations, making congruence closure an identity operation on this task, while storing all terms/equations also leaves the bounded-state gates unmet. I should have required the baseline's score on the declared stratum before registering a candidate falsifier; no implementation can rescue this test after the fact.
