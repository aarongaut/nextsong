from nextsong.playlist import Playlist
from testutils import rootrel

p = Playlist.load_xml("test.xml")
print(rootrel(p))
