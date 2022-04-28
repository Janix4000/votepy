from ordinal_election import OrdinalElection
from typing import Union, Iterable, List
from generic_greed import greedy


def chamberlin_courant_greedy(voting: Union[OrdinalElection, List[int]], size_of_committee: int,
                              number_of_scored_candidates: int) -> List[int]:
    """Greedy implementation of the chamberlin-courant rule
    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidartes using k-borda rule
    Returns:
        list[int]: List of chosen candidates
    """

    def scoring_function(committee: Iterable[int], voting: OrdinalElection, candidate: int,
                         number_of_scored_candidates: int):
        committee = set(committee + [candidate])
        score = 0
        for vote in voting:
            for i, candidate in enumerate(vote):
                if candidate in committee:
                    score += max(number_of_scored_candidates - i, 0)
                    break
        return score

    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)

    n = voting.ballot_size
    if size_of_committee > n or size_of_committee <= 0:
        raise ValueError(f"Size of committee needs to be from the range 1 to the number of all candidates.")

    return greedy(voting, size_of_committee,
                  lambda committee, voting, candidate: scoring_function(committee, voting, candidate,
                                                                        number_of_scored_candidates))


if __name__ == '__main__':
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
        4: 'e',
    })
    print(election)
    print(
        chamberlin_courant_greedy(
            election,
            2,
            5
        )
    )
