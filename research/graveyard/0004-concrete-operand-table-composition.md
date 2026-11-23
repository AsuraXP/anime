# Table-of-concrete-operands as "composition"
**Status:** DEAD — measured at chance
**Failed because:** `T[a][b]` is indexed by the operands themselves. An unseen operand pair addresses
a row that **was never written**, so the output on held-out is whatever the trainer left there — a
zero, or the argmax of an empty row. There is no direction in the parameter space in which the
correct answer lies: the table has no notion of `+`, only of "the 10000 rows I saw". A table of data
is a table of data whatever shape it is given. Making it bilinear, one-hot, low-rank or shared
across positions does not change the *index*, and the index is what fails.
**Evidence:** `bench/RESULTS.md` §D, pre-registered in-code prediction that a bilinear one-hot pair
table would generalise because it "tables the operation, not the data". Measured held-out **11.8%**
against a 10% chance floor. Prediction falsified and left on the record (D-004). Same table trained
closed-form and by 3000 SGD steps: 11.8% both ways.
**What a candidate inherits if it reuses this:** any candidate whose index contains the operand
*value* is this table. Check: if you can write down the held-out inputs as a set of keys that never
appeared in training, the candidate is a lookup and will score its key-coverage rate, not a
generalisation rate. This is the single most common disguise in the family — it recurs as "shared
table", "role algebra", "factorised embedding", "product quantisation of the operand".
**Escape condition:** index by a *role* or *relation* that is invariant to the operand value, so that
an unseen operand maps to a seen key. Then — and only then — is the held-out score measuring
composition. D4 is the attempt at this and is attacked separately in `0007-abstention-by-key-miss.md`:
it fixed the index and then measured its own key coverage instead of its own mechanism.
