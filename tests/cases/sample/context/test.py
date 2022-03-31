from nextsong import sample
import random

ctx = sample.RandomContext(seed=123)

expected = [0.052363598850944326, 0.08718667752263232]

with ctx:
    assert random.random() == expected[0]
    assert random.random() == expected[1]


ctx = sample.RandomContext(seed=123)

random.random()
with ctx:
    assert random.random() == expected[0]
random.random()
with ctx:
    assert random.random() == expected[1]
