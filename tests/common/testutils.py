import random

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


