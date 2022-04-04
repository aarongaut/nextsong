from nextsong import Playlist as p


p(
    p(
        "1.mp3",
        "2.mp3",
        "3.mp3",
        portion=0.5,
    ),
    p(
        "more_tracks/*",
        count=1,
        weight=0.5,
    ),
    loop=True,
    shuffle=True,
    recent_portion=0,
).save_xml()
