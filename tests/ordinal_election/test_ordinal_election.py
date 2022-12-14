
from votepy.ordinal_election import OrdinalElection


def test_un_eq_list():
    assert OrdinalElection([[0, 1, 2], [0, 1, 2]]) != [[0, 1, 2], [1, 0, 2]]


def test_eq_list_same_order():
    assert OrdinalElection([[0, 1, 2], [1, 0, 2]]) == [[0, 1, 2], [1, 0, 2]]


def test_eq_list_diff_order():
    assert OrdinalElection([[0, 1, 2], [1, 0, 2]]) == [[1, 0, 2], [0, 1, 2]]


def test_un_eq_ordinal_election():
    assert OrdinalElection([[0, 1, 2], [0, 1, 2]]) != OrdinalElection([[0, 1, 2], [1, 0, 2]])


def test_eq_ordinal_election_same_order():
    assert OrdinalElection([[0, 1, 2], [1, 0, 2]]) == OrdinalElection([[0, 1, 2], [1, 0, 2]])


def test_eq_ordinal_election_diff_order():
    assert OrdinalElection([[0, 1, 2], [1, 0, 2]]) == OrdinalElection([[1, 0, 2], [0, 1, 2]])


def test_un_eq_ordinal_election_diff_repr():
    left = OrdinalElection([[0, 1, 2], [1, 0, 2]], mapping={0: 'a', 1: 'b', 2: 'c'})
    right = OrdinalElection([[0, 1, 2], [1, 0, 2]], mapping={0: 'a', 1: 'c', 2: 'b'})

    assert left != right


def test_eq_ordinal_election_same_repr():
    left = OrdinalElection([[0, 1, 2], [1, 0, 2]], mapping={0: 'a', 1: 'b', 2: 'c'})
    right = OrdinalElection([[0, 1, 2], [1, 0, 2]], mapping={0: 'a', 1: 'b', 2: 'c'})

    assert left == right
