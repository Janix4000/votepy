from ordinal_election import OrdinalElection
from typing import Callable, Iterable


def greedy(voting: OrdinalElection, size_of_committee: int,
           scoring_function: Callable[[Iterable[int], OrdinalElection, int], int]) -> list[int]:
    """A generic greedy algorithm that calculates the winning committee using a given scoring function
    Args:
        voting (OrdinalElection): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        scoring_function (Callable[[Iterable[int], OrdinalElection], int]): The scoring function used to determine the best committee. It should take the committee, election and candidate as parameters and return the score of that committee.

    Returns:
        list[int]: The winning committee
    """
    resultant_committee = []
    remaining_candidates = set(i for i in range(voting.ballot_size))
    for _ in range(size_of_committee):
        best_score = 0
        current_best_candidate, current_best_score = -1, best_score
        for candidate in remaining_candidates:
            score = scoring_function(resultant_committee, voting, candidate)
            if score > current_best_score:
                current_best_candidate = candidate
                current_best_score = score
        remaining_candidates.remove(current_best_candidate)
        resultant_committee.append(current_best_candidate)
        #best_score = current_best_score
    return resultant_committee

