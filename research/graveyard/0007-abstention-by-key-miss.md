# Abstention implemented as "key not in table"
**Status:** DEAD as a gate — it is satisfiable by a Python dict
**Failed because:** the abstain condition `key ∉ keys` is decidable by a hash table with no model at
all. Any system whose abstention is defined as membership in a finite key set scores **0 wrong by
construction** — including a system that knows nothing. So "0 wrong + high abstain" is not evidence
of calibrated uncertainty; it is the signature of a closed key space. The measurement and the
ceiling are the same number, which means the experiment has **zero degrees of freedom** and cannot
fail, therefore cannot inform.
This is not a hypothetical. It is what both surviving numbers in this repo are:
- `bench/carry.py` B0: measured 44,135 correct out of 999,964 held-out = **4.41%**; analytic ceiling
  (fraction of held-out pairs whose every position key is present) = **44,135 = 4.41%**. Identical.
- `bench/RESULTS.md` D4: measured 5,424 correct out of 9,744 = **55.67%**; ceiling = **5,424**.
  Identical. "0 wrong out of 9744" is a restatement of "the table is total on its own key space",
  which every dict is.
**Evidence:** `python3 /tmp/attack_d4.py` (reproduced inline in
`threads/0002-carry-as-function-agent-c.md` §3); `bench/carry.py`; `bench/scorecard.py::report_d4`.
**What a candidate inherits if it reuses this:** if the abstain rule can be evaluated without
running the model, G8 passes and means nothing. Any lookup table, any nearest-neighbour index, any
`KeyError`, any closed-vocabulary classifier will clear it. G8 as currently operationalised cannot
fail the thing it was written to catch.
**Escape condition:** abstention must be a **threshold on a continuous score**, and the gate must be
a **risk–coverage curve** — accuracy as the threshold sweeps coverage from 0 to 1 — reported against
the trivial baseline "abstain on everything" (which is 0 wrong at 0 coverage, for free). A single
operating point at 0 wrong is not a data point; it is a choice of threshold. The gate should read:
*beat the abstain-everything baseline in risk at every coverage level, and show the curve.*
Second requirement, from CHARTER §3 G8's own wording: every abstention must be attributable to a
**named missing structure** — and "the key is absent" is not a structure, it is the definition of a
table miss.
