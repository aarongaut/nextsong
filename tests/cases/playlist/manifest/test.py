from nextsong import Playlist as p
from testutils import rootrel


def m(playlist):
    """Get a playlist's manifest in a consistent form for testing"""
    return rootrel(sorted(set(playlist.manifest())))


assert m(p()) == []
assert m(p("1.mp3", "2.mp3", "3.mp3")) == ["1.mp3", "2.mp3", "3.mp3"]
assert m(p("*.mp3")) == ["1.mp3", "2.mp3", "3.mp3"]
assert m(p(p("*.mp3"))) == ["1.mp3", "2.mp3", "3.mp3"]
assert m(p(p("1.mp3"), "2.mp3")) == ["1.mp3", "2.mp3"]
assert m(p("*.mp3", loop=True)) == ["1.mp3", "2.mp3", "3.mp3"]

assert type(p("1.mp3").manifest()[0]) is str
