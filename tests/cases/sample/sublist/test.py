from nextsong.sample import sublist
from testutils import RandomContext


assert sublist([], 0) == []  # sublist of empty list is empty
assert sublist([], 100) == []  # count is capped by list length
assert sublist([1, 2, 3, 4], 100, weights=[1, 0, -1, 1]) == [
    1,
    4,
]  # Items with nonpositive weight are dropped
assert sublist([1] * 50, 12) == [1] * 12  # The sublist has count entries

items = [2] * 1000 + [1] * 1000

with RandomContext(seed=1):
    choices = sublist(items, 200, weights=items)
    ratio = choices.count(2) / choices.count(1)
    print(ratio)
    assert 1.5 < ratio < 2.5  # weights appear to be working

with RandomContext(seed=2):
    choices = sublist(items, 500, weights=items)
    ratio = choices.count(2) / choices.count(1)
    print(ratio)
    assert 1.5 < ratio < 2.5  # weights appear to be working

with RandomContext(seed=3):
    choices = sublist(items, 500, weights=items)
    ratio = choices.count(2) / choices.count(1)
    print(ratio)
    assert 1.5 < ratio < 2.5  # weights appear to be working

with RandomContext(seed=4):
    choices = sublist(items, 500, weights=items)
    ratio = choices.count(2) / choices.count(1)
    print(ratio)
    assert 1.5 < ratio < 2.5  # weights appear to be working