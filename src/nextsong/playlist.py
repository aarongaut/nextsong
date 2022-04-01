import nextsong.sequence
import nextsong.config
import warnings
from pathlib import Path


class Playlist:
    class PlaylistState:
        def __init__(self, iterator):
            self.__iterator = iterator

        def __next__(self):
            return next(self.__iterator)

    def __init__(
        self,
        *items,
        shuffle=False,
        portion=None,
        count=None,
        recent_portion=None,
        weight=None,
        loop=False,
    ):
        self.__loop = loop

        processed_items = []
        for item in items:
            if isinstance(item, Playlist):
                if item.__loop:
                    raise ValueError(
                        "loop=True is only allowed for the top-level Playlist"
                    )
                processed_items.append(item.__sequence)
            elif isinstance(item, str):
                root = Path(nextsong.config.get("media_root"))
                resolved_path = (root / item).resolve()
                if resolved_path.exists():
                    paths = [resolved_path]
                else:
                    paths = sorted(p.resolve() for p in root.glob(item))
                    paths = [p for p in paths if p.exists()]
                    if not paths:
                        warnings.warn(
                            f'file "{resolved_path}" not found and has no matches as a glob pattern'
                        )

                if nextsong.config.get("media_exts"):
                    supported_paths = []
                    for path in paths:
                        if path.suffix.lower().lstrip(".") in nextsong.config.get(
                            "media_exts"
                        ):
                            supported_paths.append(path)
                        else:
                            warnings.warn(
                                f'file "{path}" has unsupported extension and will be skipped'
                            )
                else:
                    supported_paths = paths

                processed_items.extend(str(p) for p in supported_paths)
            else:
                raise ValueError(f"item {repr(item)} of unknown type")

        if loop:
            if weight is not None:
                raise ValueError("weight requires loop=False")
            if shuffle:
                if count is not None:
                    raise ValueError("count requires loop=False or shuffle=False")
                if portion is not None:
                    raise ValueError("portion requires loop=False or shuffle=False")
                self.__sequence = nextsong.sequence.ShuffledLoopingSequence(
                    *processed_items, recent_portion=recent_portion
                )
            else:
                if recent_portion is not None:
                    raise ValueError("recent_portion requires shuffle=True")
                self.__sequence = nextsong.sequence.OrderedLoopingSequence(
                    *processed_items, portion=portion, count=count
                )
        else:
            if recent_portion is not None:
                if shuffle:
                    raise ValueError("recent_portion requires loop=True")
                else:
                    raise ValueError(
                        "recent_portion requires loop=True and shuffle=True"
                    )
            self.__sequence = nextsong.sequence.FiniteSequence(
                *processed_items,
                weight=weight,
                portion=portion,
                count=count,
                shuffle=shuffle,
            )

    def __iter__(self):
        return self.PlaylistState(iter(self.__sequence))
