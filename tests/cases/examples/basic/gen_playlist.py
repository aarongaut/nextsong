from nextsong import Playlist as p

p(
    "**/*.mp3",
    shuffle=True,
    loop=True,
).save_xml()
