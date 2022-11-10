from votepy.ordinal_election import OrdinalElection

from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.meta.structure import algo, impl, rule
from votepy.solve import solve

from typing import Union


@algo(name='k_borda')
class KBorda(BaseAlgorithm):
    def _solve(self, voting: OrdinalElection, size_of_committee: int) -> list[int]:
        n = voting.ballot_size
        candidates_scores = [0] * n
        m = n

        for vote in voting:
            for i, candidate in enumerate(vote):
                candidates_scores[candidate] += m - i

        committee, _ = zip(
            *sorted(enumerate(candidates_scores), reverse=True, key=lambda t: t[1]))
        return committee[:size_of_committee]


@rule(default_algorithm=KBorda)
def k_borda(voting: Union[OrdinalElection, list[int]], size_of_committee: int, algorithm: KBorda = KBorda()) -> list[int]:
    """Function computes a committee of given size using k-borda rule for specified number of scored candidates.
    In this version for multiple results only arbitrary one is returned.

    Args:
        voting (OrdinalElection): voting for which the function calculates the committee
        size_of_committee (int): Size of the committee

    Raises:
        ValueError: Size of committee is a positive number which do not exceeds number of all candidates

    Returns:
        OrdinalBallot: List of chosen candidates wrapped in ordinalBallot
    """
    return solve(k_borda, voting, size_of_committee, algorithm=algorithm)


@impl(k_borda, KBorda)
def k_borda_impl(voting, size_of_committee, algorithm: KBorda = KBorda()):
    algorithm.prepare()

    return algorithm.solve(voting, size_of_committee)


if __name__ == '__main__':
    res = k_borda([
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ], 2)
    print(res)
