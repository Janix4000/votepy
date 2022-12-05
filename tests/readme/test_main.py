# main.py
import my_bloc
import votepy as vp


def test_get_rules():
    assert 'my_bloc' in vp.get_rules()


def test_solve():
    voting = [
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ]
    assert vp.solve('my_bloc', voting, size_of_committee=2)
