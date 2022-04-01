from pathlib import Path


def firstn(iterable, n):
    values = []
    iterator = iter(iterable)
    try:
        for _ in range(n):
            values.append(next(iterator))
    except StopIteration:
        pass
    return values


def rootrel(paths):
    from nextsong.config import get as get_cfg

    root = get_cfg("media_root")
    return [str(Path(p).relative_to(root)) for p in paths]
