from nextsong.sequence import TrivialSequence

x = TrivialSequence("asdf")

assert list(x) == ["asdf"]  # Creates a sequence with just the given item

assert list(x) == ["asdf"]  # Can be reused

assert x.weight == 1.0  # Has a weight
