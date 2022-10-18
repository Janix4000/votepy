from votepy.ordinal_election import OrdinalElection
from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.structure.structure import algo

from itertools import combinations
from typing import Callable, Iterable


@algo(name='brute_force')
class BruteForce(BaseAlgorithm):
    def __init__(self):
        """A generic brute force algorithm that calculates the winning committee using a given scoring function
        """
        super().__init__()

    def prepare(self, scoring_function: Callable[[Iterable[int], OrdinalElection], int]) -> None:
        """Prepare the scoring function. Should be invoked only by the voting rule function.

        Args:
            `scoring_function` (`(Iterable[int], OrdinalElection) -> int`): The scoring function used to determine the best committee. It should take the committee and election as parameters and return the score of that committee.
        """
        self.scoring_function = scoring_function
        super().prepare()

    def _solve(self, voting: OrdinalElection, size_of_committee: int) -> list[int]:
        best_committee, best_score = None, -1
        for committee in combinations(range(voting.ballot_size), size_of_committee):
            score = self.scoring_function(committee, voting)
            if score > best_score:
                best_score = score
                best_committee = committee
        return list(best_committee)
