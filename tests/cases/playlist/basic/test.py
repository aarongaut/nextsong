from nextsong import Playlist as p
from testutils import rootrel, firstn

assert list(p()) == []
assert rootrel(p("1.mp3", "2.mp3", "3.mp3")) == ["1.mp3", "2.mp3", "3.mp3"]
assert rootrel(p("*.mp3")) == ["1.mp3", "2.mp3", "3.mp3"]
assert rootrel(p(p("*.mp3"))) == ["1.mp3", "2.mp3", "3.mp3"]
assert rootrel(p(p("1.mp3"), "2.mp3")) == ["1.mp3", "2.mp3"]
assert rootrel(p(p("1.mp3"), p("2.mp3"))) == ["1.mp3", "2.mp3"]
assert rootrel(firstn(p("*.mp3", loop=True), 5)) == [
    "1.mp3",
    "2.mp3",
    "3.mp3",
    "1.mp3",
    "2.mp3",
]

# The returned item is a simple str, not a pathlib.Path or some other object
assert type(list(p("1.mp3"))[0]) is str
