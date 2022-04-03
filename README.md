`nextsong` is a library and command line executable to support creating media playlists with a complex nested structure. It was developed to be used with [ezstream](https://icecast.org/ezstream/)'s playlist scripting capability.

# Features

- Recursive tree-based structure, where each node is also a playlist with various options for sampling songs
- Command-line executable that prints the next song in the playlist
- Save and load playlists using a validated XML schema
- Pickleable playlist state

# Usage

See `tests/cases/examples` for usage examples. For help on the command line tool, invoke

```
nextsong --help
```

# Installation

Requires Python 3.7 or higher

## From [PyPI](https://pypi.org/project/nextsong/)

Install using pip:

```
python3 -m pip install nextsong
```

## From source

This process may only work in a Linux environment. First install build dependencies:

```
python3 -m pip install build
```

Building the distribution:

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

From the top level, do:

```
make test
```
