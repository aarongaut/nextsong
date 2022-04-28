"""Implementation of config subpackage"""

__all__ = ["get", "Config"]

import os
from collections import defaultdict

from nextsong.datatypes import OnChange


def _parse_exts(exts):
    if isinstance(exts, str):
        exts = exts.split()
    return [ext.lower().lstrip(".") for ext in exts]


config_types: defaultdict = defaultdict(
    lambda: str,
    **{
        "new_state": bool,
        "media_exts": _parse_exts,
        "on_change": OnChange.cast,
    },
)


def _parse_config(config):
    return {k: config_types[k](v) for k, v in config.items() if v is not None}


default_config = {
    "priority": 0,
    "values": {
        "media_root": "./media/",
        "media_exts": [],
        "playlist_path": "./nextsong.xml",
        "state_path": "./state.pickle",
        "new_state": False,
        "on_change": OnChange.IGNORE,
    },
}

env_config = {
    "priority": 10,
    "values": _parse_config(
        {
            "media_root": os.getenv("NEXTSONG_MEDIA_ROOT", None),
            "media_exts": os.getenv("NEXTSONG_MEDIA_EXTS", None),
            "playlist_path": os.getenv("NEXTSONG_PLAYLIST_PATH", None),
            "state_path": os.getenv("NEXTSONG_STATE_PATH", None),
            "new_state": os.getenv("NEXTSONG_NEW_STATE", None),
            "on_change": os.getenv("NEXTSONG_ON_CHANGE", None),
        }
    ),
}

config_stack = [default_config, env_config]


def get(key):
    """Get a config value by name"""
    items = sorted(
        (x["priority"], i, x["values"]) for i, x in enumerate(config_stack)
    )
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
        keyword arguments are specific config values. A value of None
        is ignored rather than setting that config value to None.

        """

        object.__setattr__(
            self,
            "_Config__config",
            {
                "priority": priority,
                "values": _parse_config(values),
            },
        )

    def __getitem__(self, key):
        return get(key)

    def __setitem__(self, key, value):
        self.__config["values"].update(_parse_config({key: value}))

    def __getattr__(self, key):
        return get(key)

    def __setattr__(self, key, value):
        self.__config["values"].update(_parse_config({key: value}))

    def __enter__(self):
        config_stack.append(self.__config)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        config_stack.pop()
