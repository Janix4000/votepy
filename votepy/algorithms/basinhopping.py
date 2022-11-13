from votepy.ordinal_election import OrdinalElection
from votepy.meta.structure import algo, BaseAlgorithm

import scipy
import numpy as np
import random

from typing import Callable, Iterable


@algo('basinhopping')
# .
class BasinHopping(BaseAlgorithm):
    def __init__(self, x0: Iterable[int] = None, niter: int = 10, seed: int = None, minimizer_kwargs: dict = {}, **kwargs):
        """# Summary
        Numeric voting solving method based on the `scipy.optimize.basinhopping`

        # Args:
            `x0` (Iterable[int], optional): Initial committee guess. Defaults to `None`.
            `niter` (int, optional): Number of iterations. Defaults to `10`.
            `seed` (int, optional): Random seed. Defaults to `None`.
            `minimizer_kwargs` (dict, optional): Optimizer kwargs. Defaults to `{}`.
        """
        self.niter = niter
        self.minimizer_kwargs = minimizer_kwargs
        self.x0 = x0
        self.seed = seed
        self.kwargs = kwargs
        super().__init__()

    committee_t = Iterable[int]

    def prepare(self, scoring_function: Callable[[committee_t, OrdinalElection], float]) -> None:
        """# Summary
        Prepare the scoring function. Should be invoked only by the voting rule function.

        ## Args:
            `scoring_function` (`(committee, voting) -> score`): The scoring function used to determine the best committee.
            It should take the committee and election as parameters and return the score of that committee. 

        """
        self.scoring_function = scoring_function
        super().prepare()

    def _solve(self, voting: OrdinalElection, size_of_committee: int):
        if size_of_committee == voting.ballot_size:
            return list(range(size_of_committee))

        chosen = np.array(self.x0) if self.x0 is not None else np.arange(size_of_committee, dtype=int)
        rest = np.array(list(set(range(voting.ballot_size)) - set(chosen)))

        print(chosen, rest)

        # rest = np.arange(size_of_committee, voting.ballot_size, dtype=int)

        def optimize(x: np.ndarray):
            nonlocal self, voting
            return -self.scoring_function(x.astype(int), voting)

        def take_step(x):
            nonlocal chosen, rest
            l = random.randint(0, len(chosen) - 1)
            r = random.randint(0, len(rest) - 1)
            chosen[l], rest[r] = rest[r], chosen[l]
            x[l] = chosen[l]
            return x

        res = scipy.optimize.basinhopping(optimize, np.copy(chosen), niter=self.niter, take_step=take_step,
                                          seed=self.seed, minimizer_kwargs=self.minimizer_kwargs, **self.kwargs)
        return res.x.astype(int)
