from collections.abc import Iterable, Iterator
from abc import abstractmethod
import random
from nextsong.sample import sublist, weighted_choice


DEFAULT_WEIGHT = 1.0
DEFAULT_RECENT_PORTION = 0.5


class AbstractWeightedIterable(Iterable):
    @property
    @abstractmethod
    def weight(self):
        pass


class TrivialIterable(AbstractWeightedIterable):
    class __TrivialIterator(Iterator):
        def __init__(self, item):
            self.item = item
            self.consumed = False

        def __next__(self):
            if self.consumed:
                raise StopIteration
            self.consumed = True
            return self.item

    def __init__(self, item):
        self.__item = item

    @property
    def weight(self):
        return DEFAULT_WEIGHT

    def __iter__(self):
        return self.__TrivialIterator(self.__item)


class ConsumingIterable(AbstractWeightedIterable):
    class __ConsumingIterator(Iterator):
        def __init__(self, items):
            self.stack = [iter(x) for x in reversed(items)]

        def __next__(self):
            while self.stack:
                try:
                    return next(self.stack[-1])
                except StopIteration:
                    self.stack.pop()
            raise StopIteration

    def __init__(
        self, *items, weight=DEFAULT_WEIGHT, portion=None, count=None, shuffle=False
    ):
        items = [
            x if isinstance(x, AbstractWeightedIterable) else TrivialIterable(x)
            for x in items
        ]
        items = [x for x in items if x.weight > 0]
        self.__items = items
        self.__weight = weight if self.__items else 0
        self.__shuffle = shuffle

        if portion is not None and count is not None:
            raise ValueError("portion and count are mutually exclusive")

        if count is None and portion is None:
            portion = 1

        if portion is not None:
            if isinstance(portion, (int, float)):
                portion = (portion, portion)
            if isinstance(portion, (tuple, list)):
                if len(portion) != 2:
                    raise ValueError("portion should have two elements")
                if not isinstance(portion[0], (int, float)):
                    raise ValueError("portion should contain numbers")
                if not isinstance(portion[1], (int, float)):
                    raise ValueError("portion should contain numbers")
            else:
                raise ValueError("portion should be a number or list")
            count = tuple(int(round(x * len(items))) for x in portion)

        if isinstance(count, int):
            count = (count, count)
        if isinstance(count, (tuple, list)):
            if len(count) != 2:
                raise ValueError("count should have two elements")
            if not isinstance(count[0], int):
                raise ValueError("count should contain ints")
            if not isinstance(count[1], int):
                raise ValueError("count should contain ints")
        else:
            raise ValueError("count should be an int or list")
        self.__count = tuple(min(len(items), max(0, x)) for x in count)

    @property
    def weight(self):
        return self.__weight

    def __iter__(self):
        count = random.randint(*self.__count)
        weights = [item.weight for item in self.__items]
        choices = sublist(self.__items, count, weights=weights)
        if self.__shuffle:
            random.shuffle(choices)
        return self.__ConsumingIterator(choices)


class ShuffledLoopingIterable(Iterable):
    class __ShuffledLoopingIterator(Iterator):
        def __init__(self, items, recent_size):
            self.fresh_items = list(items)
            self.recent_items = []
            self.current_iter = None
            self.recent_size = recent_size
            self.item_count = len(items)

        def __next__(self):
            if not self.item_count:
                raise StopIteration

            while True:
                if self.current_iter is None:
                    if self.fresh_items:
                        i = weighted_choice([x.weight for x in self.fresh_items])
                        choice = self.fresh_items.pop(i)
                    elif self.recent_items:
                        choice = self.recent_items.pop(0)
                    else:
                        raise RuntimeError("Unexpected logic error")
                    self.recent_items.append(choice)
                    if len(self.recent_items) > self.recent_size:
                        self.fresh_items.append(self.recent_items.pop(0))
                    self.current_iter = iter(choice)

                try:
                    return next(self.current_iter)
                except StopIteration:
                    self.current_iter = None

    def __init__(self, *items, recent_portion=DEFAULT_RECENT_PORTION):
        items = [
            x if isinstance(x, AbstractWeightedIterable) else TrivialIterable(x)
            for x in items
        ]
        items = [x for x in items if x.weight > 0]
        self.__items = items
        self.__recent_size = int(round(min(1.0, max(0.0, recent_portion)) * len(items)))

    def __iter__(self):
        return self.__ShuffledLoopingIterator(self.__items, self.__recent_size)
