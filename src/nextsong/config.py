import os

default_config = {
    "media_root": ".",
    "media_exts": None,
}

env_config = {}
if "NEXTSONG_MEDIA_ROOT" in os.environ:
    env_config["media_root"] = os.environ["NEXTSONG_MEDIA_ROOT"]
if "NEXTSONG_MEDIA_EXTS" in os.environ:
    env_config["media_exts"] = os.environ["NEXTSONG_MEDIA_EXTS"].split(" ")

config_stack = [default_config, env_config]


def get(key):
    for config in reversed(config_stack):
        if key in config:
            return config[key]
    raise KeyError('config "{key}" is not set')


class Config:
    def __init__(self, **config):
        self.__config = config

    def __enter__(self):
        config_stack.append(self.__config)

    def __exit__(self, exc_type, exc_value, traceback):
        config_stack.pop()
