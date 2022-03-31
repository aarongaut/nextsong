from nextsong.iterate import TrivialIterable

x = TrivialIterable("asdf")

assert list(x) == ["asdf"]  # Creates an iterable with just the given item

assert list(x) == ["asdf"]  # Can be reused

assert x.weight == 1.0  # Has a weight
