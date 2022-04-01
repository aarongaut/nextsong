from nextsong.config import Config, get

with Config(media_root="foo", media_exts=["bar", "qux"]):
    print("media_root:", get("media_root"))
    print("media_exts:", get("media_exts"))
