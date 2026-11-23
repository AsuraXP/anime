# Operand coverage, not parameter efficiency
**Status:** DEAD (as an experimental design, not as a mechanism)
**Failed because:** a role table trained on a restricted operand range cannot address digits it has
never seen, no matter how cleverly the carry is handled. Measured in threads/0002: 36 training pairs
on a 3-position sum reach 4.4% held-out coverage, and removing the carry index converts abstention
into **2555 confident errors**.
**Evidence:** `python3 research/bench/carry.py`
**What a candidate inherits if it reuses this:** if your training pairs do not cover every digit in
every position you will test, you are measuring your own sampling, not your primitive.
**Escape condition:** train where every position sees the full digit range, or hold out *positions
that were fully observed in other roles" rather than *values never seen at all*.
