"""Implementation of sequence subpackage"""

__all__ = [
    "AbstractWeightedIterable",
    "TrivialSequence",
    "FiniteSequence",
    "OrderedLoopingSequence",
    "ShuffledLoopingSequence",
]

from collections.abc import Iterable, Iterator
from abc import abstractmethod
import random

from nextsong.sample import sublist, weighted_choice


DEFAULT_WEIGHT = 1.0
DEFAULT_RECENT_PORTION = 0.5


class AbstractWeightedIterable(Iterable):
    """Requiring Iterable methods and a 'weight' property"""
    # pylint: disable=too-few-public-methods
    @property
    @abstractmethod
    def weight(self):
        """Weight relative to other AbstractWeightedIterable objects

        For example, weight could be the relative likelyhood of being
        included in a random sample.
        """


class TrivialSequence(AbstractWeightedIterable):
    """An iterable that yields one item one time

    This sequence is used as a component in other sequences in order to
    simplify their logic
    """
    class _TrivialIterator(Iterator):
        # pylint: disable=too-few-public-methods
        # This is implemented as an iterator class instead of generator
        # so that it can be pickled
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
        return self._TrivialIterator(self.__item)


class FiniteSequence(AbstractWeightedIterable):
    """A sequence that terminates after a pass through its items"""
    class _FiniteIterator(Iterator):
        # pylint: disable=too-few-public-methods
        # This is implemented as an iterator class instead of generator
        # so that it can be pickled
        def __init__(self, items):
            self.stack = [iter(x) for x in reversed(items)]

        def __next__(self):
            while self.stack:
                try:
                    return next(self.stack[-1])
                except StopIteration:
                    self.stack.pop()
            raise StopIteration

    @staticmethod
    def __determine_count(item_count, portion, count):
        if portion is not None and count is not None:
            raise ValueError("portion and count are mutually exclusive")

        if count is None and portion is None:
            portion = 1

        if portion is not None:
            if isinstance(portion, (int, float)):
                portion = (portion, portion)
            if isinstance(portion, (tuple, list)):
                if len(portion) != 2 or not all(
                    isinstance(x, (int, float)) for x in portion
                ):
                    raise ValueError("portion should contain two numbers")
            else:
                raise ValueError("portion should be a number or pair of numbers")
            count = tuple(int(round(x * item_count)) for x in portion)

        if isinstance(count, int):
            count = (count, count)
        if isinstance(count, (tuple, list)):
            if len(count) != 2 or not all(isinstance(x, int) for x in count):
                raise ValueError("count should contain two ints")
        else:
            raise ValueError("count should be an int or pair of ints")
        return tuple(min(item_count, max(0, x)) for x in count)

    def __init__(self, *items, weight=None, portion=None, count=None, shuffle=False):
        items = [
            x if isinstance(x, AbstractWeightedIterable) else TrivialSequence(x)
            for x in items
        ]
        items = [x for x in items if x.weight > 0]
        self.__items = items
        self.__shuffle = shuffle

        self.__count = self.__determine_count(len(items), portion, count)
        if weight is None:
            weight = DEFAULT_WEIGHT

        # Disable this sequence from being used in a parent if it will
        # never produce any items (prevents infinite busy looping in some
        # degenerate cases)
        if not self.__items:
            weight = 0
        if max(*self.__count) == 0:
            weight = 0

        self.__weight = weight

    @property
    def weight(self):
        return self.__weight

    def __iter__(self):
        count = random.randint(*self.__count)
        weights = [item.weight for item in self.__items]
        choices = sublist(self.__items, count, weights=weights)
        if self.__shuffle:
            random.shuffle(choices)
        return self._FiniteIterator(choices)


class OrderedLoopingSequence(AbstractWeightedIterable):
    """A sequence that repeatedly loops through its items in order"""
    class _OrderedLoopingIterator(Iterator):
        # pylint: disable=too-few-public-methods
        # This is implemented as an iterator class instead of generator
        # so that it can be pickled
        def __init__(self, sequence):
            self.sequence = sequence
            self.iterator = None

        def __next__(self):
            if self.sequence.weight == 0:
                raise StopIteration
            while True:
                if self.iterator is None:
                    self.iterator = iter(self.sequence)
                try:
                    return next(self.iterator)
                except StopIteration:
                    self.iterator = None

    def __init__(self, *items, portion=None, count=None, weight=None):
        self.__sequence = FiniteSequence(
            *items, portion=portion, count=count, shuffle=False, weight=weight
        )

    @property
    def weight(self):
        return self.__sequence.weight

    def __iter__(self):
        return self._OrderedLoopingIterator(self.__sequence)


class ShuffledLoopingSequence(AbstractWeightedIterable):
    """A sequence that repeatedly samples randomly from its items"""
    class _ShuffledLoopingIterator(Iterator):
        # pylint: disable=too-few-public-methods
        # This is implemented as an iterator class instead of generator
        # so that it can be pickled
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

    def __init__(self, *items, recent_portion=None, weight=None):
        items = [
            x if isinstance(x, AbstractWeightedIterable) else TrivialSequence(x)
            for x in items
        ]
        items = [x for x in items if x.weight > 0]
        if recent_portion is None:
            recent_portion = DEFAULT_RECENT_PORTION
        self.__items = items
        self.__recent_size = int(round(min(1.0, max(0.0, recent_portion)) * len(items)))

        if weight is None:
            weight = DEFAULT_WEIGHT
        # Disable this sequence from being used in a parent if it will
        # never produce any items (prevents infinite busy looping in some
        # degenerate cases)
        if not self.__items:
            weight = 0
        self.__weight = weight

    @property
    def weight(self):
        return self.__weight

    def __iter__(self):
        return self._ShuffledLoopingIterator(self.__items, self.__recent_size)
