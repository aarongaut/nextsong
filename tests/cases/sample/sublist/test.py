from nextsong.sample import sublist
import random


assert sublist([], 0) == []  # sublist of empty list is empty
assert sublist([], 100) == []  # count is capped by list length
assert sublist([1] * 50, 12) == [1] * 12  # The sublist has count entries

items = [2] * 1000 + [1] * 1000

for seed in [1, 2, 3, 4]:
    random.seed(seed)
    choices = sublist(items, 500, weights=items)
    ratio = choices.count(2) / choices.count(1)
    print(ratio)
    assert 1.5 < ratio < 2.5  # weights appear to be working
