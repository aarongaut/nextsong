"""Implementation of types subpackage"""

__all__ = ["OnChange"]

from enum import Enum, auto


class Option(Enum):
    @classmethod
    def cast(cls, val):
        if isinstance(val, cls):
            return val
        if isinstance(val, str):
            try:
                return cls[val]
            except KeyError:
                # Scanning for a case-insensitive match
                for k, v in cls.__members__.items():
                    if k.lower() == val.lower():
                        return v
                raise
        raise ValueError(f"Cannot cast {val} to {cls}")


class OnChange(Option):
    ignore = auto()
    restart = auto()
    #merge = auto()
