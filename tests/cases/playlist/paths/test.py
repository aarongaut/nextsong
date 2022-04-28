from nextsong import Playlist as p
from testutils import rootrel


def paths(playlist):
    """Get a playlist's paths in a consistent form for testing"""
    return rootrel(sorted(set(playlist.paths())))


assert paths(p()) == []
assert paths(p("1.mp3", "2.mp3", "3.mp3")) == ["1.mp3", "2.mp3", "3.mp3"]
assert paths(p("*.mp3")) == ["1.mp3", "2.mp3", "3.mp3"]
assert paths(p(p("*.mp3"))) == ["1.mp3", "2.mp3", "3.mp3"]
assert paths(p(p("1.mp3"), "2.mp3")) == ["1.mp3", "2.mp3"]
assert paths(p("*.mp3", loop=True)) == ["1.mp3", "2.mp3", "3.mp3"]

assert type(p("1.mp3").paths()[0]) is str
