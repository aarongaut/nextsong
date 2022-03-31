from nextsong.iterate import ConsumingIterable as C
from nextsong.iterate import ShuffledLoopingIterable as L
from testutils import RandomContext, firstn

with RandomContext(seed=123):
    assert firstn(L(C(1, weight=100), 2, 3, recent_portion=1), 10) == [1, 2, 3, 1, 2, 3, 1, 2, 3, 1]

assert firstn(L(1, recent_portion=0), 5) == [1] * 5
