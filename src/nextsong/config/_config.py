"""Implementation of config subpackage"""

__all__ = ["get", "Config"]

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
