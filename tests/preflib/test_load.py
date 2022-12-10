import os
from votepy import preflib
from votepy.ordinal_election import OrdinalElection

dir_path = os.path.join('tests', 'fixtures', 'preflib')


def test_load_no_dups():
    expected = [
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ]
    assert preflib.load(os.path.join(dir_path, 'voting_no_dups.txt')) == expected


def test_load_with_dups():
    expected = [
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [3, 2, 1, 0],
        [2, 1, 3, 0],
        [2, 1, 3, 0],
        [2, 1, 3, 0]
    ]
    assert preflib.load(os.path.join(dir_path, 'voting_with_dups.txt')) == expected


def test_load_with_names():
    expected = OrdinalElection(
        [
            [0, 1, 2, 3],
            [3, 2, 1, 0],
            [2, 1, 3, 0]
        ],
        mapping={0: 'A', 1: 'B', 2: 'C'}
    )
    assert os.getcwd() == ""
    assert preflib.load(os.path.join(dir_path, 'voting_with_names.txt')) == expected
