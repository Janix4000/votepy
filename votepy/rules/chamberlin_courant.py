from votepy.ordinal_election import OrdinalElection

from votepy.structure.structure import rule, impl
from votepy.solve import solve

from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.algorithms.generic_brute_force import BruteForce
from votepy.algorithms.generic_greedy import Greedy

from typing import Union, Iterable


@rule()
def chamberlin_courant(voting: Union[OrdinalElection, list[int]], size_of_committee: int, algorithm: BaseAlgorithm) -> list[int]:
    """# Summary
    Chamberlin-Courant rule
    ## Args:
        `voting` (`OrdinalElection | list[int]`): Voting for which the function calculates the committee
        `size_of_committee` (`int`): Size of the committee
        `number_of_scored_candidates` (`int`): Number of scored candidates using k-borda rule

    ## Returns:
        `list[int]`: List of chosen candidates

    ## Examples
    >>> election = [
    ...     [0, 1, 2, 3, 4],
    ...     [4, 0, 1, 3, 2],
    ...     [3, 0, 1, 2, 4],
    ...     [2, 1, 3, 4, 0],
    ...     [2, 1, 4, 0, 3],
    ...     [1, 2, 3, 4, 0]
    ... ]
    >>> chamberlin_courant(election, 2, algorithm='brute_force')
    [0, 2]
    >>> chamberlin_courant(election, 2, algorithm='greedy')
    [1, 0]
    """
    return solve(chamberlin_courant, voting, size_of_committee, algorithm=algorithm)


def scoring_function(committee: Iterable[int], voting: OrdinalElection) -> float:
    """# Summary
    Scoring function for Chamberlin-Courant rule. Calculates score for the given committee, under CC rule and given voting.ballot_size

    ## Args:
        `committee` (Iterable[int]): Chosen committee
        `voting` (OrdinalElection): Voting

    ## Returns:
        -> float: Score of the committee

    ## Examples
    """
    committee = set(committee)
    score = 0
    m = voting.ballot_size
    for voter in voting:
        score += max(m - voter.pos(candidate) for candidate in committee)
    return score


@impl(chamberlin_courant, BruteForce)
def chamberlin_courant_brute_force(voting, size_of_committee, algorithm: BruteForce = BruteForce()) -> list[int]:
    algorithm.prepare(scoring_function)
    return algorithm.solve(voting, size_of_committee)


@impl(chamberlin_courant, Greedy)
def chamberlin_courant_greedy(voting, size_of_committee, algorithm: Greedy = Greedy()) -> list[int]:
    def greedy_scoring_function(committee: Iterable[int], voting: OrdinalElection, candidate: int):
        committee = set(committee) | {candidate}
        return scoring_function(committee, voting)

    algorithm.prepare(greedy_scoring_function)
    return algorithm.solve(voting, size_of_committee)


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
        chamberlin_courant(
            election,
            2,
            algorithm='brute_force'
        )
    )
    print(
        chamberlin_courant(
            election,
            2,
            algorithm=Greedy()
        )
    )
