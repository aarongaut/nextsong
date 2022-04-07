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
"""

__version__ = "1.1.2.dev0"

from . import config
from . import sample
from . import sequence
from . import playlist

Playlist = playlist.Playlist
ensure_state = playlist.ensure_state
