`nextsong` is a library and command line executable to support creating media playlists with a complex nested structure. It was developed to be used with [ezstream](https://icecast.org/ezstream/)'s playlist scripting capability.

# Features

- Recursive tree-based structure, where each node is also a playlist with various options for sampling songs
- Command-line executable that prints the next song in the playlist
- Save and load playlists using a validated XML file (XSD under development)
- Simple ezstream integration

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

```
$ nextsong
/home/myusername/media/music/my_favorite_song.mp3
$ nextsong
/home/myusername/media/music/artist1/album1/01_hello_world.mp3
$ nextsong
/home/myusername/media/music/artist1/album1/02_foobar.mp3
```

The `nextsong` command will print the absolute path of the next track to standard output or print an empty line once the end of the playlist has been reached. In this example, the playlist is set to loop, so it will never end. The state of iteration through the playlist is maintained in a pickle file named `state.pickle`. Note that changes to the playlist XML file will only take effect by deleting this pickle file.

The filepaths in this example and other options such as the root media directory can be configured within the Python script or via environment variables.

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

```
$ NEXTSONG_MEDIA_ROOT=~/music ezstream -c ~/ezstream.xml
```

## Learning more

Any module, class, or function can be passed into the builtin `help` function for detailed information. See `tests/cases/examples` for complete usage examples. For help on the command line tool, invoke

```
$ nextsong --help
```

Please feel free to open an issue for any further questions.

# Installation

Requires Python 3.7 or higher

## From [PyPI](https://pypi.org/project/nextsong/)

Install using pip

```
python3 -m pip install nextsong
```

## From source

First install build dependencies

```
python3 -m pip install build
```

Building the distribution

```
git clone https://gitlab.com/samflam/nextsong.git
cd nextsong
make
```

To install, you can `pip install` the built wheel in `dist` or simply run

```
make install
```

# Testing

There are some additionally dependencies for testing

- `black`: format checker
- `pylint`: linter

From the top level, do

```
make test
```
