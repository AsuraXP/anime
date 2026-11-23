# Bigger optimiser as a substitute for the right representation
**Status:** DEAD — measured to be exactly zero
**Failed because:** if the feature map already spans the target function's failure set, extra SGD
steps move the parameters *within that span*. The loss goes down on seen data and the held-out
behaviour is unchanged, because the held-out error is not an optimisation error — it is a
representational one: no setting of the parameters produces the right output on an unseen key.
Measured to three digits: linear closed-form **5.9%** held-out, MLP-64 with 3000 backprop steps
**5.9%** held-out, same one-hot inputs, same data, 1.88 s of training. Identical.
**Evidence:** `bench/RESULTS.md` §D, rows D1 and D3. Closed-form ridge (0.01 s) and SGD (1.88 s)
buy the same held-out number.
**What a candidate inherits if it reuses this:** any proposal whose fix is "train longer / wider /
better optimiser / add a second layer" must show the **representation** changed, not the loss.
Concretely: report held-out, not train loss; and report the parameter-count-matched baseline,
because a bigger model that fits the training set is not evidence of anything.
**Escape condition:** optimisation only helps when the target function is inside the model class and
the parameters are merely not there yet. That is a claim about the function class, and it must be
argued from the index/representation, not from the trainer. If a closed-form rule and backprop
disagree on held-out, *that* disagreement is the interesting number — it means the closed form is
missing a term, not that gradients are magic.
