from nextsong.playlist import Playlist as p

p(
    "**/*.mp3",
    shuffle=True,
    loop=True,
).save_xml()
