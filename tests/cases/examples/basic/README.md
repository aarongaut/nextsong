This is a basic example which picks mp3 files at random from the `media` directory.

First run the `gen_playlist.py` script, which generates a `nextsong.xml` file. Then invoke the `nextsong` command line executable. Each time it is invoked, it prints the filepath of the next track in the playlist based on the `nextsong.xml` file. It also maintains a `state.pickle` file which tracks its current location in the playlist. After modifying the playlist, either delete `state.pickle` or use the `--new-state` argument the next time `nextsong` is invoked.
