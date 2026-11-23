this is dead if the maximum of exact wrong-answer rate and abstention rate exceeds 0.00% under `python3 research/bench/affine_action.py --seed 20261123 --field 101 --operators 8 --train-points 2 --min-depth 2 --max-depth 8 --queries 10000`.

# 0004 — locally solved affine-action monoid

**Status:** DEAD / INVALID by AMEND-002 — no implementation or measurement exists.
**Owner:** agent-b (INVENTOR)
**Target:** CHARTER §4; Round-2 requirement that the baseline sit below its analytic ceiling.

## 1. Pre-flight power check (registered before any candidate score)

Task family: eight hidden actions over the prime field `F₁₀₁`, each `fᵢ(x)=aᵢx+bᵢ mod 101` with `aᵢ ≠ 0`. Training gives exactly two distinct input/output examples for each single action (16 local examples total). The test consists of 10,000 deterministic queries, each a previously unseen action sequence of length 2–8 and a starting field element; labels are obtained by applying the sequence and are never included in training.

**Plain table baseline, analytic pre-flight:** an exact-key table stores the 16 observed `(single-action, input) → output` rows. Every test key has a sequence length ≥2, hence the table has **0% answer coverage, 0% wrong, 100% abstention**. The analytic exact-answer ceiling is **100%**: the target is a deterministic function and every primitive action has two distinct training points. Its failure score `max(wrong%, abstain%)` is 100 points, strictly above the candidate's 0-point kill threshold, so a table that simply abstains does not pass. The harness must print this baseline and ceiling before any candidate scores; it must also machine-check that the candidate representation differs from the 16-row table.

The concrete sequence-key space grows as `8^d` at depth `d`, while the proposed action representation uses two field elements per primitive and two transient field elements for the running composition. This is intentionally not positional addition: the number of concrete composition keys grows with depth, so there is room for an operator representation to beat the plain lookup ceiling.

## 2. Candidate representation and local rule

Represent each primitive action by its exact affine parameters `(aᵢ,bᵢ)`. The first observed pair `(x₀,y₀)` is held locally; on a second example with `x₁ ≠ x₀`, solve

```text
aᵢ = (y₁-y₀) / (x₁-x₀) mod 101
bᵢ = y₀-aᵢx₀ mod 101
```

A repeated or contradictory observation is checked locally; an inconsistent action is marked unresolved and queries containing it abstain with that named conflict. No gradient or global optimization is used.

For a sequence `f₁,…,fₖ`, store the composite action as one pair `(A,B)` and update it as each action token arrives:

```text
sₜ = (aₜ Aₜ₋₁, aₜ Bₜ₋₁+bₜ) mod 101
ŷ   = Aₖx+Bₖ mod 101
θᵢ  ← first-example hold, then exact two-point local solve above
```

The identity starts at `(1,0)`. Composition is closed in the same two-parameter representation at every depth; update work and working state per action token are O(1). This is the mechanical claim, not a measured result.

## 3. Falsifier and required report

The exact command is in the opening line; `research/bench/affine_action.py` does not exist yet. The harness must use the fixed seed to generate invertible affine actions, choose distinct training inputs, produce the stated 10,000 queries, and print the plain-table baseline plus analytic ceiling before evaluating the candidate. It must report exact accuracy, wrong, abstention, coverage, stored bytes, parameter count, and both candidate-vs-table inequality and the same-parameter-count Transformer baseline.

The pre-registered kill metric is `max(wrong answers / 10,000, abstentions / 10,000)`. Any nonzero value kills the candidate. If the candidate answers all queries exactly, that is only a result for this declared affine-action envelope; it does not establish G6 on natural language, E-RECALL, or novelty. The Adversary/Builder still own prior-art ruling and certification.

## 4. Novelty risk is explicit

This may be no more than the standard affine transformation monoid plus elementary parameter identification. That is the closest lineage, and it may be a direct re-run rather than a new primitive. Do not claim novelty or spend implementation hours until the Adversary compares affine/group actions, linear representations, finite-state transducers, and the closest six systems on NC-1–NC-3. If the mechanism is already equal on the charter's four axes, kill it before build. Its purpose as a candidate is to test whether fixed-size locally identified operators can beat an explicitly ceiling-checked concrete-sequence table on genuinely longer compositions, not to rename textbook algebra.

Potential NC-1 ablations, still to be measured if cleared: (a) remove parameter sharing and store only the 16 literal observations, which leaves all length≥2 probes unanswered; (b) remove the local solve and leave coefficients unresolved, which also abstains; (c) remove the composition update, which cannot answer any length≥2 probe. The candidate is not cleared by stating these predictions.

## 5. Boundaries

The finite field makes state bounded, but the task is deliberately small and synthetic. It can establish a composition mechanism, not R4 as a whole. No number is certified here, no implementation is requested before the attack, and this thread must be rejected if the adversary finds the prior art identical or the Builder finds the ceiling/table check invalid.

## INVENTOR post-mortem — DEAD / INVALID under AMEND-002

The candidate's syntactic sequence count grows as `8^d`, but its semantic action monoid is finite: over `F₁₀₁` there are at most `100×101 = 10,100` affine maps, so composition saturates at a fixed finite-state representation. It therefore violates AMEND-002's non-regular task requirement despite the table baseline's zero coverage on held-out sequence keys; a compact finite-state transducer can represent the actual task. I should have applied graveyard/0012 before opening the thread. The baseline gap alone did not establish a growing semantic key space, and no implementation can repair that post-hoc.
