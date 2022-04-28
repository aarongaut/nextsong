"""A media playlist library for Python

This library can be used to create complex, nested media playlists.

Modules
-------
playlist:
    defines the Playlist class, the main feature of the package
config:
    provides global configuration to the package
sequence:
    low level iterator classes
sample:
    low level random sampling routines
datatypes:
    low level data only classes and enums
"""

__version__ = "1.2.1.dev0"

from . import config
from . import datatypes
from . import sample
from . import sequence
from . import playlist

Playlist = playlist.Playlist
ensure_state = playlist.ensure_state
