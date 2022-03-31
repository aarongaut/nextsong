from collections.abc import Iterable, Iterator
from abc import abstractmethod


DEFAULT_WEIGHT = 1.0


class WeightedIterable(Iterable):
    @property
    @abstractmethod
    def weight(self):
        pass


class TrivialNode(WeightedIterable):
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
        self.__weight = weight

    @property
    def weight(self):
        return DEFAULT_WEIGHT

    def __iter__(self):
        return self.__TrivialIterator(self.__item)


class ConsumingNode(WeightedIterable):
    class __ConsumingIterator(Iterator):
        def __init__(self, items):
            self.__stack = [iter(x) for x in reversed(items)]

        def __next__(self):
            while self.__stack:
                try:
                    return next(self.__stack[-1])
                except StopIteration:
                    self.__stack.pop()
            raise StopIteration

    def __init__(self, *items, weight=DEFAULT_WEIGHT):  # , portion=None):
        self.__items = [
            x if isinstance(x, WeightedIterable) else TrivialNode(x) for x in items
        ]
        self.__weight = weight

    @property
    def weight(self):
        return self.__weight

    def __iter__(self):
        return self.__ConsumingIterator(self.__items)


# class ShuffledLoopingNode(Iterable):
#    def __init__(self, items, *,
