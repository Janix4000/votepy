from mock_integration import add, Slow, Fast

from votepy.solve import solve


def test_solve():
    assert solve(add, 1, 2, algorithm="fast") == 3
    assert solve(add, 1, 2, algorithm=Fast()) == 3

    assert solve("add", 1, 2, algorithm="fast") == 3
    assert solve("add", 1, 2, algorithm=Fast()) == 3

    slow = Slow(max_iterations=10)
    assert solve(add, 1, 2, algorithm=slow) == 3
    assert solve("add", 1, 2, algorithm=slow) == 3
