import os
from nextsong.playlist import Playlist
from testutils import rootrel

xml_path = os.environ["RL_ROOT"] + "/tests/common/sample_playlists/1.xml"

p = Playlist.load_xml(xml_path)
print(rootrel(p))
