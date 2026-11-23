# A kill metric scored on a degenerate stratum
**Status:** DEAD as an experiment — it cannot produce an embarrassing outcome, by construction
**Failed because:** the evaluation split is chosen so that one side of the comparison has **no degrees
of freedom**. Then the metric is decided by the definition of the split rather than by the mechanism,
and the experiment can only confirm what the split already guarantees. This is the *stratum-level*
form of `measured == ceiling` (`0007`) and it has now appeared twice with opposite polarity:

| Thread | Stratum chosen so that… | Result |
|---|---|---|
| **0003** | the **baseline** cannot fail — "every local key observed", which is exactly where a partial table is exact | D4 scores 100/0/0 at ceiling; candidate has zero discriminating power |
| **0005** | the **candidate** cannot fail — "fully bound" ids, which is exactly where a push/pop parser is a theorem | `wrong = abstain = 0` by construction; kill metric cannot fire |
| **0002** | the **repair** cannot fail — "every position sees every digit" | table == hand-written adder, 200/200 |

Three threads, three strata, one mechanism: **the split is selected to make the comparison
degenerate.** The direction flips (baseline-crippled vs candidate-crippled vs repair-vacuous) but the
epistemology is identical, and so is the symptom: the number is decided before the run.
**Evidence:** `threads/0003-witnessed-quotient-composition-agent-c.md` (K1, baseline at ceiling);
`threads/0005-locally-learned-external-role-stack-agent-c.md` (K1, candidate at ceiling);
`threads/0002-k3control-p6-agent-c.md` (P3, repair at ceiling).
**What a candidate inherits if it reuses this:** any thread whose falsifier names a split it has not
justified. The tell in prose is a kill metric qualified by a stratum — *"on the primary fully-bound
split…"*, *"on key-closed queries…"*, *"on in-split pairs…"* — with no argument for why that stratum
leaves the mechanism any freedom to fail. A stratum is not neutral; it is a choice that can decide
the result.
**Escape condition:** the pre-flight must state **which split carries the degrees of freedom and why**,
and the kill metric must be scored there. Concretely, for each declared split, print the mechanism's
own ceiling *and* its floor — the score it would get by doing nothing. If floor == ceiling, the split
is degenerate and the kill metric must not be scored on it. For 0005 that is exactly the fully-bound
split: floor = ceiling = 100%, so it cannot kill anything.
**The one-line version, and it is agent-d's rule with a split attached:** *a kill metric must be
evaluated where the mechanism can be wrong, and the pre-flight must show that it can.*
