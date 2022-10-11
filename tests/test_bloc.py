from votepy.bloc import bloc
from votepy.ordinal_election import OrdinalElection
import os

from tests.util.util import assert_approximation, load_tests, generate_tests

from itertools import product

alpha = 0.99


def scoring(voting: OrdinalElection, committee: list[int]) -> float:
    committee_size = len(committee)
    score = 0.0
    for ballot in voting:
        for candidate in committee:
            score += 1.0 if ballot.pos(candidate) < committee_size else 0.0
    return score


def test_bloc():
    for voting, size_of_committee, expected_score in load_tests("tests/fixtures/bloc_medium.json"):
        voting = OrdinalElection(voting)
        committee = bloc(voting, size_of_committee)
        score = scoring(voting, committee)
        assert (score >= alpha * expected_score)


if __name__ == "__main__":
    generate_tests(
        "tests/fixtures/bloc_medium.json",
        filter(lambda x: x[0] + x[1] > 5 and x[0] >
               0 and x[1] > 0, product(range(20), range(20))),
        lambda c, v: OrdinalElection([list(range(c)) for _ in range(v)]),
        lambda e, c: scoring(e, bloc(e, c))
    )
