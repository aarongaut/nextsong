from nextsong.sequence import FiniteSequence as S
from nextsong.sequence import OrderedLoopingSequence as L
from testutils import firstn

assert firstn(L(1), 5) == [1] * 5

assert firstn(L(1, 2, 3), 10) == [
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

assert (
    list(L(S(1, 2, 3, count=0))) == []
)  # Terminates loop if no items are available
