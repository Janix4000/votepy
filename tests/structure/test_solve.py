from mock_integration import add, Slow, Fast

from votepy.solve import solve
from votepy.meta.structure import rule

import pytest


@rule
def rule_without_implementation(voting, committee_size):
    return []


def test_solve():
    assert solve(add, 1, 2, algorithm="fast") == 3
    assert solve(add, 1, 2, algorithm=Fast()) == 3

    assert solve("add", 1, 2, algorithm="fast") == 3
    assert solve("add", 1, 2, algorithm=Fast()) == 3

    slow = Slow(max_iterations=10)
    assert solve(add, 1, 2, algorithm=slow) == 3
    assert solve("add", 1, 2, algorithm=slow) == 3


def test_rule_without_implementation():
    with pytest.raises(ValueError):
        solve('rule_without_implementation', None, 3)
