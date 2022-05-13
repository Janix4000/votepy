from ordinal_election import OrdinalElection
from typing import Callable, Iterable

from generic_greed import greedy


def banzhaf_naive_impl(voting: OrdinalElection, size_of_committee: int,
           scoring_function: Callable[[int, OrdinalElection, int], int]) -> list[int]:
    """A generic greedy algorithm that calculates the winning committee using a given scoring function
    Args:
        voting (OrdinalElection): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        scoring_function (Callable[[int, OrdinalElection, int], int]): The single-winner scoring function. It should take the candidate index, election, size of the committee and return the single score of that candidate. Scoring function of the committee must be expressed as ∑γ(pos(voter)).

    Returns:
        list[int]: The winning committee
    """
    
    
    def banzhaf_scoring_function(w, voting, c):
        def delta(d):
            return 0
        
        def delta_prime(c):
            return 0
        
        return 0
    
    
    return greedy(voting, size_of_committee, banzhaf_scoring_function)

