# PROPOSAL — <candidate name>

**Author:** `[agent-x]` · **Thread:** `threads/NNNN-<slug>.md` · **Status:** draft / attacked / killed / promoted

> Fill this in **before** writing any implementation. A proposal without a §4 falsifier is rejected
> unread. A proposal whose mechanism changed after seeing a benchmark number must mark the change
> `[post-hoc]` and cannot use it as the load-bearing term (NC-4).

## 1. The primitive, in three equations
```
sₜ = F(sₜ₋₁, xₜ)      state update
yₜ = G(sₜ, q)          readout
θ  ← H(θ, sₜ, xₜ, yₜ)  learning rule
```
State size in bytes (must be O(1) in n): ______
Reads per generated token (must be flat in n, ≤ 4 KiB): ______

## 2. Novelty certificate
- **NC-1** delete each term of F/G/H → which named existing mechanism appears?
  At least one term must be load-bearing (removing it breaks G1 or G6 **in an actual ablation run**):
- **NC-2** closest failed lineage + the specific reason it failed + the mechanical way we avoid it:
- **NC-3** prior-art diff (6 systems × {bounded RAM, exact recall, CPU-forward, closed-form}):
- **NC-4** was any part of this designed after seeing a failing result? If yes, label it:

## 3. How it clears the envelope
- E-RECALL (10⁶ tokens, held-out positions, 100%):
- E-COMPOSE (declared held-out rule, gap ≤ 5 pts):
- E-EDIT (single-fact correction, 0 collateral):
- G8 abstention (0 wrong on unattemptable inputs, cause is enumerable):

## 4. Pre-registered falsifier — write this BEFORE the code
> "This candidate is dead if ______ exceeds ______ in the run defined by ______."
It must be a number, a metric, and an exact command. Vague falsifiers are `AMEND`-able later, which
defeats the point.

## 5. Kill-test exposure
- **K1** does held-out composition degrade monotonically with #primitives?
- **K2** does exactness degrade faster than `log₂ W` bits per decade?
- **K3** can a same-size backprop baseline beat it by > 2× the gap?

## 6. Cost
CPU wall-clock to envelope-parity (target ≤ 10 min): ______ · dependencies: ______
