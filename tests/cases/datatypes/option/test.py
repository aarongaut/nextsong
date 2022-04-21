from nextsong.datatypes._datatypes import Option
from enum import auto

class TestOption(Option):
    foo = auto()
    bAr = auto()

assert TestOption.cast(TestOption.foo) == TestOption.foo
assert TestOption.cast('foo') == TestOption.foo
assert TestOption.cast('fOo') == TestOption.foo
assert TestOption.cast('bar') == TestOption.bAr
