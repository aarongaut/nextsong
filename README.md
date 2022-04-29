`nextsong` is a library and command line executable to support creating media playlists with a complex nested structure.

_Note: This project is theoretically platform agnostic, but isn't tested outside of Linux. If you encounter a problem using it on another platform please feel free to open an issue._

# Features

- Recursive tree-based structure, where each item in the playlist is itself a playlist with various options for sampling songs
- XML format to save and load playlists
- Command-line executable to get the next song in the playlist
- [ezstream](https://icecast.org/ezstream/) integration

# Usage

## Basic example

First create a playlist and save it to an XML file:

```python
from nextsong import Playlist

Playlist(
    "my_favorite_song.mp3",
    "artist1/album1/*.mp3",
    loop=True,
).save_xml()
```

Each item the playlist can be a filepath, a [glob pattern](https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob), or another playlist.

This creates a file named `nextsong.xml` describing the playlist:

```xml
<nextsong>
  <meta/>
  <playlist loop="true">
    <path>my_favorite_song.mp3</path>
    <path>artist1/album1/*.mp3</path>
  </playlist>
</nextsong>
```

After creating the XML file, invoke `nextsong` from the command line to get the next track in the playlist

```sh
$ nextsong
/home/myusername/media/music/my_favorite_song.mp3
$ nextsong
/home/myusername/media/music/artist1/album1/01_hello_world.mp3
$ nextsong
/home/myusername/media/music/artist1/album1/02_foobar.mp3
```

The `nextsong` command will print the absolute path of the next track to standard output or print an empty line once the end of the playlist has been reached. In this example, the playlist is set to loop, so it will never end. The state of iteration through the playlist is maintained in a pickle file named `state.pickle`.

## Configuration

The filepaths in the above example and other configuration options such as the root media directory can be changed from environment variables, command line arguments, and in scripts using the `nextsong.config.Config` class. For example

```python
from nextsong.config import Config
from nextsong import Playlist

with Config(playlist_path="my_playlist.xml") as cfg:
    # prints "my_playlist.xml"
    print(cfg.playlist_path)
    # prints "./media/" (the default)
    print(cfg.media_root)
    # saves to "my_playlist.xml"
    Playlist("my_favorite_song.mp3").save_xml()
```

In the above example we create a `Config` object to override the `playlist_path` config. This override is in effect until the end of the `with` block. Config values can be accessed as attributes of the `Config` object. If the `Config` object doesn't override a value, the value is sourced from lower priority configs such as defaults and environment variables. This is seen when accessing `media_root`. Note that while the config value for `playlist_path` isn't explicitly passed down to `save_xml`, it still determines the XML file's path. It is never necessary to pass a `Config` object into a function to have effect - just invoke the function inside the `Config`'s `with` block.

See the `nextsong.config` module's docstring for a comprehensive overview of supported config options, their behaviors, and corresponding environment variables. Run

```python
import nextsong; help(nextsong.config)
```

## Handling playlist updates

By default the state of iteration through a playlist, saved in `state.pickle`, is based on a snapshot of the playlist at the moment the iteration began. A new state must be created (such as by deleting the `state.pickle` file) for playlist changes to take effect. This behavior can be changed by setting the `on_change` config. Currently the options are:

|`on_change` choice|Behavior|
|:-|:-|
|`ignore`|Continue based on the old playlist. This is the default behavior.|
|`restart`|Start over at the beginning of the new playlist.|
|`seek`|Start over with the new playlist, and seek to what would have been the next track in the old playlist. If this isn't possible for some reason, emit a warning and fall back to the `restart` behavior.|

_Note: playlist change detection is based on the playlist file's last modified time. This is a simple 'good enough' solution but has some pitfalls. See [mtime comparison considered harmful](https://apenwarr.ca/log/20181113) for a good overview._

## Ezstream integration

First create the playlist XML file using this package as described above.

To update the `ezstream` XML file see the `ezstream` man page for the most fleshed out and up to date details. You need to create a `program` intake that runs `nextsong`. Overall your `intakes` element should look something like this:

```xml
<intakes>
  <intake>
    <type>program</type>
    <filename>nextsong</filename>
  </intake>
</instakes>
```

When running `nextsong` through `ezstream` you can use environment variables to adjust the configuration. For example, to set `nextsong`'s `media_root` config, run `ezstream` with `NEXTSONG_MEDIA_ROOT` set to the desired value

```sh
$ NEXTSONG_MEDIA_ROOT=~/music ezstream -c ~/ezstream.xml
```

Details on config values and their corresponding environment variables can be found in the `nextsong.config` docstring, which can be viewed in the Python interpreter by calling `help(nextsong.config)`.

## Local playback example with vlc

While actually playing the media is outside this library's scope, it's fairly straightforward to write a script that does media playback by invoking `nextsong` in a loop and feeding the result into a media player. For example, here's a bash script using vlc to play the playlist:

```bash
trap break INT
while true
do
    TRACK="$(nextsong)"
    if [ -z "$TRACK" ]
    then
        printf "End of playlist\n"
        break
    fi
    printf "Playing %s\n" "$TRACK"
    cvlc --play-and-exit "$TRACK" >& /dev/null
done
```

## Learning more

Any module, class, or function can be passed into the builtin `help` function for detailed information. See `tests/cases/examples` for complete usage examples. For help on the command line tool, invoke

```sh
$ nextsong --help
```

Please feel free to open an issue for any further questions.

# Installation

Requires Python 3.7 or higher

## From [PyPI](https://pypi.org/project/nextsong/)

Install using pip

```sh
$ python3 -m pip install nextsong
```

## From source

First install build dependencies

```sh
$ python3 -m pip install build
```

Building the distribution

```sh
$ git clone https://gitlab.com/samflam/nextsong.git
$ cd nextsong
$ make
```

To install, you can `pip install` the built wheel in `dist` or simply run

```sh
$ make install
```

# Testing

There are some additional dependencies for testing

- `black`: format checker
- `pylint`: linter
- `flake8`: linter and style checker

From the top level, do

```sh
$ make test
```
