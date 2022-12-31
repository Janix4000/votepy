# main.py
import my_bloc
import my_cc
import votepy as vp

voting = [
    [0, 1, 2, 3],
    [3, 2, 1, 0],
    [2, 1, 3, 0]
]


def test_get_rules_bloc():
    assert 'my_bloc' in vp.get_rules()


def test_solve_bloc():
    assert vp.solve('my_bloc', voting, size_of_committee=2)


def test_get_rules_cc():
    assert 'my_cc' in vp.get_rules()


def test_solve_cc_greedy():
    assert vp.solve('my_cc', voting, size_of_committee=2, algorithm='greedy')


def test_solve_cc_brute_force():
    assert vp.solve('my_cc', voting, size_of_committee=2, algorithm='brute_force')


if __name__ == '__main__':
    test_solve_cc_brute_force()
