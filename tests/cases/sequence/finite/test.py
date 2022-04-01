from nextsong.sequence import FiniteSequence as S
from testutils import RandomContext

assert list(S()) == []
assert list(S(10, 20, 30, 40, 50, 60)) == [10, 20, 30, 40, 50, 60]

for seed in [42, 43, 44, 45]:
    print(f"testing seed {seed}")
    with RandomContext(seed=seed):
        assert list(S(10, 20, 30, 40, portion=0)) == []
        assert len(list(S(10, 20, 30, 40, count=2))) == 2
        assert len(list(S(10, 20, 30, 40, portion=0.5))) == 2
        assert list(S(S(10, weight=100), 20, S(30, weight=100), 40, portion=0.5)) == [
            10,
            30,
        ]
