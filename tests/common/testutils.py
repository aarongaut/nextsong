from pathlib import Path
import random


def firstn(iterable, n):
    values = []
    iterator = iter(iterable)
    try:
        for _ in range(n):
            values.append(next(iterator))
    except StopIteration:
        pass
    return values


def pwdrel(paths):
    cwd = Path(".").resolve()
    return [str(Path(p).relative_to(cwd)) for p in paths]


class RandomContext:
    def __init__(self, seed=None):
        self.idle_state = random.getstate()
        random.seed(seed)
        self._swap()

    def _swap(self):
        tmp = random.getstate()
        random.setstate(self.idle_state)
        self.idle_state = tmp

    def __enter__(self):
        self._swap()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._swap()
