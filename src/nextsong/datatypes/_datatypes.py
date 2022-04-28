"""Implementation of types subpackage"""

__all__ = ["OnChange"]

from enum import Enum, auto


class OptionEnum(Enum):
    """Custom extension of Enum

    Adds methods to integrate better with command line options and
    environment variables.
    """

    def __str__(self):
        return self.name.lower()

    @classmethod
    def cast(cls, val):
        """Convert a value to an OptionEnum

        Does a case-insensitive lookup if given a string.
        """
        if isinstance(val, cls):
            return val
        if isinstance(val, str):
            try:
                return cls[val]
            except KeyError:
                # Scanning for a case-insensitive match
                for key, enum_value in cls.__members__.items():
                    if key.lower() == val.lower():
                        return enum_value
                raise
        raise ValueError(f"Cannot cast {val} to {cls}")

    @classmethod
    def choices(cls):
        """List available choices for the OptionEnum as strings"""
        return [x.lower() for x in cls.__members__]


class OnChange(OptionEnum):
    """What happens to the playlist state if the playlist has changed

    IGNORE:
        Continue playing with the old playlist.
    RESTART:
        Start over with the new playlist.
    SEEK:
        Start over with the new playlist and skip tracks until what
        would have been the next track in the old playlist. If this
        isn't possible because the track doesn't appear in the new
        playlist, fall back to behavior for RESTART.
    """

    IGNORE = auto()
    RESTART = auto()
    SEEK = auto()
    # MERGE = auto()
