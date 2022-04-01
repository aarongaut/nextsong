from nextsong.sequence import FiniteSequence as S
from nextsong.sequence import ShuffledLoopingSequence as L
from testutils import firstn
import random

random.seed(123)

assert firstn(L(S(1, weight=100), 2, 3, recent_portion=1), 10) == [
    1,
    2,
    3,
    1,
    2,
    3,
    1,
    2,
    3,
    1,
]

assert firstn(L(1, recent_portion=0), 5) == [1] * 5

assert list(L(S(1, 2, 3, count=0))) == []  # Terminates loop if no items are available
