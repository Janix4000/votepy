from votepy.ordinal_election import OrdinalElection

from votepy.testing.structure.structure import rule, get_implementation, imp
from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
from votepy.testing.algorithms.generic_brute_force import BruteForce
from votepy.testing.algorithms.generic_greedy import Greedy

from typing import Union, Iterable


@rule
def chamberlin_courant(voting: Union[OrdinalElection, list[int]], size_of_committee: int, number_of_scored_candidates: int, algorithm: BaseAlgorithm) -> list[int]:
    """Chamberlin-courant rule
    Args:
        `voting` (`Union[OrdinalElection, list[int]]`): Voting for which the function calculates the committee
        `size_of_committee` (`int`): Size of the committee
        `number_of_scored_candidates` (`int`): Number of scored candidates using k-borda rule

    Returns:
        `list[int]`: List of chosen candidates
    """
    implementation = get_implementation(chamberlin_courant, algorithm)
    implementation(voting, size_of_committee,
                   number_of_scored_candidates, algorithm)


@imp(rule=chamberlin_courant, algorithm=BruteForce)
def chamberlin_courant_brute_force(voting, size_of_committee, number_of_scored_candidates, brute_force: BruteForce = BruteForce()) -> list[int]:
    def scoring_function(committee: Iterable[int], voting: OrdinalElection):
        committee = set(committee)
        score = 0
        for vote in voting:
            for i, candidate in enumerate(vote):
                if candidate in committee:
                    score += max(number_of_scored_candidates - i, 0)
                    break
        return score

    brute_force.prepare(scoring_function)
    return brute_force.solve(voting, size_of_committee)


@imp(chamberlin_courant, Greedy)
def chamberlin_courant_greedy(voting, size_of_committee, number_of_scored_candidates, greedy: Greedy = Greedy()) -> list[int]:
    def scoring_function(committee: Iterable[int], voting: OrdinalElection, candidate: int):
        committee = set(committee) | {candidate}
        score = 0
        for vote in voting:
            for i, candidate in enumerate(vote):
                if candidate in committee:
                    score += max(number_of_scored_candidates - i, 0)
                    break
        return score

    greedy.prepare(scoring_function)
    return greedy.solve(voting, size_of_committee)


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
            5,
            algorithm='brute_force'
        )
    )
    print(
        chamberlin_courant(
            election,
            2,
            5,
            algorithm=Greedy()
        )
    )
