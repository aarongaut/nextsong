"""This module provides a global configuration to the package

Configuration is sourced from defaults, environment variables, and user
overrides using this module's Config class. A config value can be
queried from anywhere using this module's 'get' function.

Config values
-------------
media_root:
    Used as the root when resolving relative paths to media files in a
    Playlist. Defaults to "./media".
media_exts:
    Lists permitted file extensions for media files. If none are given
    the related checks are skipped. Defaults to None.
playlist_path:
    The default filepath used when saving/loading a playlist with the
    Playlist.load_xml and Playlist.save_xml methods. Defaults to
    "./nextsong.xml".
state_path:
    The default filepath used when pickling/unpickling a playlist's
    state. Defaults to "./state.pickle".
new_state:
    If True, an existing pickle file is ignored and playlist state
    should be recreated from scratch from the playlist. Defaults to
    False.
on_change:
    See nextsong.datatypes.OnChange for options and behavior.
max_seek_skips:
    When seeking through a playlist for a specific track, the maximum
    number of tracks that will be skipped before giving up and issuing
    a warning.

Environment variables
---------------------
NEXTSONG_MEDIA_ROOT:
    Overrides media_root config
NEXTSONG_MEDIA_EXTS:
    Space-separated list; overrides media_exts config
NEXTSONG_PLAYLIST_PATH:
    Overrides playlist_path config
NEXTSONG_STATE_PATH:
    Overrides state_path config
NEXTSONG_NEW_STATE:
    False if empty string, True if anything else; overrides new_state
NEXTSONG_ON_CHANGE:
    See nextsong.datatypes.OnChange for options and behavior; overrides
    on_change
NEXTSONG_MAX_SEEK_SKIPS:
    Overrides max_seek_skips

Details
-------
A configuration value is looked up by searching through a global stack
of config dictionaries for an item with matching key. New config
dictionaries can be pushed to the stack to override existing ones. The
stack is initialized with a dictionary containing default values for
all known config keys, followed by a dictionary containing overrides
from any known environment variables. Additional configs can be pushed
to the stack using this module's Config class to initiate a 'with'
block. The config is pushed and popped at the beginning and end of the
'with' block, respectively.

Configurations also include a priority determining who overrides who. A
config with larger number priority overrides a config with smaller
number priority, and the position on the stack is the tiebreaker. For
example, this can be used to create a user config that overrides the
defaults, but not environment variables by using a priority of 5
(between the default priority of 0 and environment variable priority of
10).

"""

from ._config import *
