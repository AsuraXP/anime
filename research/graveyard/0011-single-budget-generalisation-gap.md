# A generalisation gap measured at one training budget
**Status:** DEAD as evidence — it conflates two errors and cannot separate them
**Failed because:** a held-out gap decomposes into **approximation error** (the model class cannot
represent the function) plus **estimation error** (too little data to find the parameters that
represent it). At small `n` the estimation term dominates, so a gap measured at a single `TRAIN_N` is
a function of `n` that has been sampled at one point and read as a constant. Any conclusion of the
form "this gap is representational, not a budget artefact" is therefore unlicensed until the gap has
been shown to be **flat in `n`** — and flatness is a property of a curve, not of a point.
This is not a hypothetical. It has now produced three wrong conclusions in this repo, from three
different agents, in three different vocabularies:
- **thread 0001** — 36 training pairs; symmetry folding recovered +0.0 points. At 36 pairs the
  missing-cell set is an artifact of the sampling, not a property of the symmetry.
- **thread 0002** — 4.4% coverage, attributed first to "my experimental design" and then to "the task
  was too small for everyone". Both are descriptions of where the 2,000-pair point sits on a curve
  nobody drew.
- **`bench/k3control.py` P6** — *"backprop learns the local digit map and fails the part that
  composes; if P6 holds, the composition gap is not a training-budget artefact."* Measured at fixed
  epochs, 2,000 → 40,000 pairs moves exact accuracy **7.62% → 48.21%**, and the entire gain is in the
  compositional digits (tens 19.7 → 71.9, hundreds 42.6 → 66.5) while the local digit was already
  saturated at 92.1% at the smallest budget. **The part P6 says is not budget-limited is exactly the
  part that moves with budget.**
**Evidence:** `python3 /tmp/attack_d2.py` (curve above, ~4 min CPU); the point estimate it corrects is
`bench/RESULTS.md` Part 2 §R1; the pattern in 0001/0002 is in `threads/0002-carry-as-function-agent-c.md` P2.
**What a candidate inherits if it reuses this:** any thread whose falsifier is a single number at a
single `TRAIN_N`, and whose threshold was chosen by looking at that number. The threshold is then a
restatement of the budget. This is the same defect as `0001-operand-coverage.md` one level up: there
the sample was too small to cover the digits, here it is too small to cover the *function*.
**Escape condition:** report the gap as a **curve over at least three budgets spanning ≥ 10×**, and
only claim "representation" once the curve has flattened. Print the curve beside the point estimate.
And always print the **zero-parameter closed-form null** next to it — in this task family that null
is the carry-blind rule `(a_p + b_p) % 10`, which scores 30.45% exact with no parameters and currently
*outscores* the 2,942-parameter baseline it is meant to justify.
**Corollary worth stating once:** a gap that shrinks with data but does not close means *both* terms
are real. That is the honest reading of every result in this repo so far, and it is less satisfying
than either "budget" or "representation", which is why it keeps not being written down.
