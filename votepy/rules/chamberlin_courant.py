import collections
from votepy.generic_p_algorithm import PAlgorithm
from votepy.ordinal_election import OrdinalElection

from votepy.structure.structure import rule, get_implementation, impl
from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.algorithms.generic_brute_force import BruteForce
from votepy.algorithms.generic_greedy import Greedy

from typing import Union, Iterable


@rule()
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


@impl(chamberlin_courant, BruteForce)
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


@impl(chamberlin_courant, Greedy)
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


@impl(chamberlin_courant, PAlgorithm)
def chamberlin_courant_p_algorithm(voting, size_of_committee, number_of_scored_candidates, algorithm: PAlgorithm) -> list[int]:

    def scoring_function(voting: OrdinalElection, size_of_committee: int, threshold: int):
        scores = collections.defaultdict(int)
        winners = []
        vs = [v[:threshold] for v in voting]
        for vote in vs:
            for candidate in vote:
                scores[candidate] += 1
        for _ in range(size_of_committee):
            best_candidate = max((val, key) for key, val in scores.items())[1]

            for idx, cs in enumerate(vs):
                if best_candidate in cs:
                    for c in cs:
                        scores[c] -= 1
                    vs[idx] = []
            del scores[best_candidate]
            winners.append(best_candidate)
        return winners

    algorithm.prepare(scoring_function)

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
    print(
        chamberlin_courant(
            election,
            2,
            5,
            algorithm='p_algorithm'
        )
    )
