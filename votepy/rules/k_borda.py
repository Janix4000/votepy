from votepy.ordinal_election import OrdinalElection

from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.structure.structure import algo, impl, rule
from votepy.solve import solve

from typing import Union


@algo(name='k_borda')
class KBorda(BaseAlgorithm):
    def prepare(self, number_of_scored_candidates: int) -> None:
        self.number_of_scored_candidates = number_of_scored_candidates
        super().prepare()

    def _solve(self, voting: OrdinalElection, size_of_committee: int) -> list[int]:
        n = voting.ballot_size
        results = [0] * n

        for vote in voting:
            m = self.number_of_scored_candidates
            for candidate in vote[:self.number_of_scored_candidates]:
                results[candidate] += m
                m -= 1
        committee, _ = zip(
            *sorted(enumerate(results), reverse=True, key=lambda t: t[1]))
        return committee[:size_of_committee]


@rule(default_algorithm=KBorda)
def k_borda(voting: Union[OrdinalElection, list[int]], size_of_committee: int, number_of_scored_candidates: int, algorithm: KBorda = KBorda()) -> list[int]:
    """Function computes a committee of given size using k-borda rule for specified number of scored candidates.
    In this version for multiple results only arbitrary one is returned.

    Args:
        voting (OrdinalElection): voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidates using k-borda rule

    Raises:
        ValueError: Size of committee is a positive number which do not exceeds number of all candidates
        ValueError: Number of candidates scored in k-borda is a positive number which do not exceeds number of all candidates

    Returns:
        OrdinalBallot: List of chosen candidates wrapped in ordinalBallot
    """
    n = voting.ballot_size
    if number_of_scored_candidates > n or number_of_scored_candidates <= 0:
        raise ValueError(
            f"Number of candidates scored in k-borda needs to be from range 1 to the number of all candidates.")

    return solve(k_borda, voting, size_of_committee, number_of_scored_candidates, algorithm=algorithm)


@impl(k_borda, KBorda)
def k_borda_impl(voting, size_of_committee, number_of_scored_candidates, algorithm: KBorda):
    algorithm.prepare(number_of_scored_candidates)

    return algorithm.solve(voting, size_of_committee)


if __name__ == '__main__':
    print(k_borda([
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ], 2, 3))
