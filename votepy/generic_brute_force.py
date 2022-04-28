from ordinal_election import OrdinalElection
from typing import Callable, Iterable
from itertools import combinations



def brute_force(voting: OrdinalElection, size_of_committee: int, scoring_function: Callable[[Iterable[int], OrdinalElection], int]) -> list[int]:
    """A generic brute force algorithm that calculates the winning committee using a given scoring function

    Args:
        voting (OrdinalElection): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        scoring_function (Callable[[Iterable[int], OrdinalElection], int]): The scoring function used to determine the best committee. It should take the committee and election as parameters and return the score of that committee.
        

    Returns:
        list[int]: The winning committee
    """
    best_committee, best_score = None, -1
    for committee in combinations(range(voting.ballot_size), size_of_committee):
        score = scoring_function(committee, voting)
        if score > best_score:
            best_score = score
            best_committee = committee
    return best_committee