from nextsong.datatypes._datatypes import OptionEnum
from enum import auto


class Test(OptionEnum):
    foo = auto()
    bAr = auto()


assert Test.cast(Test.foo) == Test.foo
assert Test.cast("foo") == Test.foo
assert Test.cast("fOo") == Test.foo
assert Test.cast("bar") == Test.bAr
assert Test.choices() == ["foo", "bar"]
