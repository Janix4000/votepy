from votepy.bloc import bloc
from votepy.ordinal_election import OrdinalElection

from .util.util import assert_approximation


def test_bloc():
    election = OrdinalElection([
        [0, 1, 2, 3, 4],
        [4, 0, 1, 3, 2],
        [3, 0, 1, 2, 4],
        [2, 1, 3, 4, 0],
        [2, 1, 4, 0, 3],
        [1, 2, 3, 4, 0]
    ], {
        0: 'a',
        1: 'b',
        2: 'c',
        3: 'd',
        4: 'e'
    })

    assert_approximation(
        election,
        lambda _e: 10,
        10,
        0.8
    )
