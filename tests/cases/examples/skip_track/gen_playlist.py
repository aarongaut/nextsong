from nextsong import Playlist as p

p(
    "01.mp3",
    p(
        p("02.mp3", weight=1/4),
        p(weight=3/4),
        count=1,
    ),
    "03.mp3",
    "04.mp3",
    loop=True,
).save_xml()
