from nextsong.playlist import Playlist as p

p(
    p("band1/album1/*.mp3"),
    p("band1/album2/*.mp3"),
    p("band1/album3/*.mp3"),
    p("band2/album1/*.mp3"),
    p("band2/album2/*.mp3"),
    p("band2/album3/*.mp3"),
    p("band3/album1/*.mp3"),
    p("band3/album2/*.mp3"),
    p("band3/album3/*.mp3"),
    shuffle=True,
    loop=True,
).save_xml()
