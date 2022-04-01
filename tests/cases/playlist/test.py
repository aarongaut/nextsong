from nextsong.playlist import Playlist as p
from testutils import rootrel, firstn

assert list(p()) == []
assert rootrel(p("1", "2", "3")) == ["1", "2", "3"]
assert rootrel(p("*")) == ["1", "2", "3"]
assert rootrel(p(p("*"))) == ["1", "2", "3"]
assert rootrel(p(p("1"), "2")) == ["1", "2"]
assert rootrel(p(p("1"), p("2"))) == ["1", "2"]
assert rootrel(firstn(p("*", loop=True), 5)) == [
    "1",
    "2",
    "3",
    "1",
    "2",
]
