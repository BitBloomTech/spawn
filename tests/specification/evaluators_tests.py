import pytest

from spawn.specification.evaluators import *

@pytest.mark.parametrize('start,end,step,expected', [
    (0, 0, 1, [0]),
    (0, 1, 1, [0, 1]),
    (0, 1, 2, [0]),
])
def test_range_evaluator_returns_correct_range(start, end, step, expected):
    assert RangeEvaluator(start, end, step).evaluate() == expected