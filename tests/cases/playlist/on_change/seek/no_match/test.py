from time import sleep
import warnings

from nextsong import Playlist as P, ensure_state

# This test relies on fairly high-precision comparisons between system
# time and the playlist's mtime to trigger the on_change logic.
# Surprisingly, a newly created file can appear to be created slightly
# in the past due to the low resolution of mtime. On an ext4 filesystem
# the resolution of mtime is about 10ms, so we are sleeping 20ms before
# each save_xml call to ensure the on_change logic is triggered as
# expected. See also: https://apenwarr.ca/log/20181113

warnings.filterwarnings("error")

sleep(0.02)
P("1.mp3", "2.mp3").save_xml()

with ensure_state(new_state=True) as state:
    next(state)

sleep(0.02)
P("3.mp3").save_xml()

try:
    # Should fail to find 2.mp3
    with ensure_state() as state:
        next(state)
except UserWarning as w:
    print(f"Got expected warning: {w}")
else:
    raise AssertionError("Expected warning not raised")

sleep(0.02)
P("1.mp3", "2.mp3").save_xml()

with ensure_state(new_state=True) as state:
    next(state)

sleep(0.02)
P(P("1.mp3", loop=True), "2.mp3").save_xml()

try:
    # Should fail with too much work
    with ensure_state() as state:
        next(state)
except UserWarning as w:
    print(f"Got expected warning: {w}")
else:
    raise AssertionError("Expected warning not raised")
