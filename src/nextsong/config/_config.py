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
import os

default_config = {
    "priority": 0,
    "values": {
        "media_root": "./media",
        "media_exts": None,
        "playlist_path": "./nextsong.xml",
        "state_path": "./state.pickle",
        "new_state": False,
    },
}

env_config = {
    "priority": 10,
    "values": {},
}

if "NEXTSONG_MEDIA_ROOT" in os.environ:
    env_config["values"]["media_root"] = os.environ["NEXTSONG_MEDIA_ROOT"]
if "NEXTSONG_MEDIA_EXTS" in os.environ:
    env_config["values"]["media_exts"] = os.environ["NEXTSONG_MEDIA_EXTS"].split(" ")
if "NEXTSONG_PLAYLIST_PATH" in os.environ:
    env_config["values"]["playlist_path"] = os.environ["NEXTSONG_PLAYLIST_PATH"]
if "NEXTSONG_STATE_PATH" in os.environ:
    env_config["values"]["state_path"] = os.environ["NEXTSONG_STATE_PATH"]
if "NEXTSONG_NEW_STATE" in os.environ:
    env_config["values"]["new_state"] = bool(os.environ["NEXTSONG_NEW_STATE"])

config_stack = [default_config, env_config]


def get(key):
    """Get a config value by name"""
    items = sorted((x["priority"], i, x["values"]) for i, x in enumerate(config_stack))
    for _, _, values in reversed(items):
        if key in values:
            return values[key]
    raise KeyError(f'config "{key}" is not set')


class Config:
    """Overrides the global configuration

    This class is a context manager that overrides some or all of the
    global configuration inside of a 'with' block

    """

    def __init__(self, priority=20, **values):
        """Create a Config instance

        The Config instance should be used in a 'with' statement and
        is only active for the duration of the 'with' block. The
        priority argument can be used to tune the overriding of other
        configs. See the module-level docstring for details. Other
        keyword arguments are specific config values.

        """
        self.__config = {
            "priority": priority,
            "values": values,
        }

    def __enter__(self):
        config_stack.append(self.__config)

    def __exit__(self, exc_type, exc_value, traceback):
        config_stack.pop()
