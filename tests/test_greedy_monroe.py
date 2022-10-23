from votepy.rules.greedy_monroe import greedy_monroe
from votepy.ordinal_election import OrdinalElection
from votepy.rules.k_borda import k_borda


def test_greedy_monroe():
    voting = [
        [1, 0, 2, 3, 4],
        [3, 2, 4, 1, 0],
        [2, 4, 1, 3, 0]
    ]
    size_of_committee = 2
    voting = OrdinalElection(voting)
    committee = greedy_monroe(voting, size_of_committee)
    assert (committee == [1, 2])


if __name__ == "__main__":
    test_greedy_monroe()
