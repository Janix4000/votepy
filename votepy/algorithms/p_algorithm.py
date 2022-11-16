import random

from votepy.ordinal_election import OrdinalElection
from typing import Callable, Iterable

from votepy.meta.structure import algo, BaseAlgorithm


@algo(name='p_algorithm')
class PAlgorithm(BaseAlgorithm):
    def __init__(self):
        """# Summary
        An algorithm that calculates the winning committee using a scoring function given in votepy/chamberlin_courant.py.
        Algorithm based on https://doi.org/10.1016/j.artint.2015.01.003
        """
        super().__init__()

    def __simple_score(self, vote, committee):
        if not vote:
            return -1
        m = len(vote)
        for idx, vote in enumerate(vote):
            if vote in committee:
                return m - idx - 1

    def __simple_profile_score(self, voting, committee):
        return sum([self.__simple_score(vote, committee) for vote in voting])

    def prepare(self, scoring_function: Callable[[Iterable[int], int, float], list[int]]):
        """# Summary
        Prepare the scoring function. Should be invoked only by the voting rule function.

        ## Args:
            `scoring_function` (`(Iterable[int], int, int) -> float`): The scoring function used to determine the best committee. It should take the committee, election and threshold as the parameters and return the score of that committee.
        """
        self.scoring_function = scoring_function
        super().prepare()

    def _solve(self, voting: OrdinalElection, size_of_committee: int) -> list[int]:
        num_candidates = voting.ballot_size

        best = -1
        best_t = -1
        winners = []

        for threshold in range(1, num_candidates):
            winners_try = self.scoring_function(voting, size_of_committee, threshold)
            curr = self.__simple_profile_score(voting, winners_try)
            if curr > best:
                winners = [winners_try]
                best = curr
                best_t = [threshold]
            elif curr == best:
                winners.append(winners_try)
                best_t.append(threshold)
        return random.choice(winners)
