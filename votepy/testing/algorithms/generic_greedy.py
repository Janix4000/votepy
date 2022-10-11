from votepy.ordinal_election import OrdinalElection

from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
from votepy.testing.structure.structure import algo

from typing import Callable, Iterable


@algo(name='greedy')
class Greedy(BaseAlgorithm):
    def __init__(self):
        """A generic greedy algorithm that calculates the winning committee using a given scoring function.
        """
        super().__init__()

    def prepare(self, scoring_function: Callable[[Iterable[int], OrdinalElection, int], int]):
        """Prepare the scoring function. Should be invoked only by the voting rule function.

        Args:
            `scoring_function` (`(Iterable[int], OrdinalElection, int) -> int`): The scoring function used to determine the best committee. It should take the committee, election and candidate as parameters and return the score of that committee.
        """
        self.scoring_function = scoring_function
        super().prepare()

    def _solve(self, voting: OrdinalElection, size_of_committee: int):
        resultant_committee = []
        best_score = 0
        remaining_candidates = set(i for i in range(voting.ballot_size))
        for _ in range(size_of_committee):
            current_best_candidate, current_best_score = -1, best_score
            for candidate in remaining_candidates:
                score = self.scoring_function(
                    resultant_committee, voting, candidate)
                if score > current_best_score:
                    current_best_candidate = candidate
                    current_best_score = score
            remaining_candidates.remove(current_best_candidate)
            resultant_committee.append(current_best_candidate)
            best_score = current_best_score
        return resultant_committee
