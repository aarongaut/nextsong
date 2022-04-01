from nextsong.playlist import Playlist as p
from nextsong.config import Config
from testutils import pwdrel, firstn

with Config(media_root="media"):
    assert list(p()) == []
    assert pwdrel(p("1", "2", "3")) == ["media/1", "media/2", "media/3"]
    assert pwdrel(p("*")) == ["media/1", "media/2", "media/3"]
    assert pwdrel(p(p("*"))) == ["media/1", "media/2", "media/3"]
    assert pwdrel(p(p("1"), "2")) == ["media/1", "media/2"]
    assert pwdrel(p(p("1"), p("2"))) == ["media/1", "media/2"]
    assert pwdrel(firstn(p("*", loop=True), 5)) == [
        "media/1",
        "media/2",
        "media/3",
        "media/1",
        "media/2",
    ]
