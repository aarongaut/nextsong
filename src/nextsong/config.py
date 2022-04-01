import os

default_config = {
    "priority": 0,
    "values": {
        "media_root": ".",
        "media_exts": None,
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

config_stack = [default_config, env_config]


def get(key):
    items = sorted((x["priority"], i, x["values"]) for i, x in enumerate(config_stack))
    for _, _, values in reversed(items):
        if key in values:
            return values[key]
    raise KeyError(f'config "{key}" is not set')


class Config:
    def __init__(self, priority=20, **values):
        self.__config = {
            "priority": priority,
            "values": values,
        }

    def __enter__(self):
        config_stack.append(self.__config)

    def __exit__(self, exc_type, exc_value, traceback):
        config_stack.pop()
