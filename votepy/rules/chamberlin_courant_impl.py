import collections

from votepy.algorithms.p_algorithm import PAlgorithm
from votepy.ordinal_election import OrdinalElection

from votepy.meta.structure import rule, impl
from votepy.solve import solve

from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.algorithms.brute_force import BruteForce
from votepy.algorithms.greedy import Greedy
from votepy.algorithms.basinhopping import BasinHopping
from votepy.algorithms.ilp import ILP
from votepy.generic_ilp import CPLEX, Gurobi, model_t, solver_t

from typing import Type, Union, Iterable


@rule()
def chamberlin_courant(voting: Union[OrdinalElection, list[int]], size_of_committee: int, algorithm: BaseAlgorithm) -> \
        list[int]:
    """# Summary
    Chamberlin-Courant rule
    ## Args:
        `voting` (`OrdinalElection | list[int]`): Voting for which the function calculates the committee
        `size_of_committee` (`int`): Size of the committee

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
    Scoring function for Chamberlin-Courant rule. Calculates score for the given committee, under CC rule and given voting

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


# Based on https://arxiv.org/abs/1901.09217
@impl(chamberlin_courant, PAlgorithm)
def chamberlin_courant_p_algorithm(voting: Union[OrdinalElection, list[int]], size_of_committee: int,
                                   algorithm: PAlgorithm = PAlgorithm()) -> list[int]:
    def scoring_function(voting: OrdinalElection, size_of_committee: int, threshold: int) -> list[int]:
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


@impl(chamberlin_courant, BasinHopping)
def chamberlin_courant_basinhopping(voting: Union[OrdinalElection, list[int]], size_of_committee: int,
                                    algorithm: BasinHopping = BasinHopping()):
    algorithm.prepare(scoring_function)
    return algorithm.solve(voting, size_of_committee)


@impl(chamberlin_courant, ILP)
def chamberlin_courant_ilp(voting: Union[OrdinalElection, list[list[int]]], size_of_committee: int, algorithm: ILP = ILP(Gurobi)) -> list[int]:
    """Implementation of the chamberlin-courant rule, using ILP formulation by:
    Peters, Dominik & Lackner, Martin. (2020).
    Preferences Single-Peaked on a Circle.
    Journal of Artificial Intelligence Research. 68. 463-502. 10.1613/jair.1.11732.

    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
    Returns:
        list[int]: List of chosen candidates
    """
    def define_model(voting: OrdinalElection, size_of_committee: int, solver: solver_t) -> model_t:
        model = solver()

        y = [model.addVariable(f"y_{c}", 'B', 0)
             for c in range(voting.ballot_size)]

        x = [[model.addVariable(f"x_{i},{r}", 'B', 1)
              for r in range(voting.ballot_size)]
             for i in range(voting.number_of_voters)]

        model.addConstraint(
            'sum(y)', y, [1]*len(y), size_of_committee, 'E')

        for i in range(voting.number_of_voters):
            for r in range(voting.ballot_size):
                top_r_candidates = [y[c] for c in voting[i][:r]]
                model.addConstraint(
                    f'x_{i}_{r} <= sum(top_{r}_candidates)',
                    [x[i][r]] + top_r_candidates,
                    [1.0] + [-1.0]*len(voting[i][:r]),
                    0,
                    'L'
                )
        return model

    algorithm.prepare(define_model)
    return algorithm.solve(voting, size_of_committee)


# For now leaving without annotation - if it's easy to add different
# implementations of the same rule and algorithm, then I think we should do
# that. To use this function, you need to call it explicitly.
def chamberlin_courant_ilp_custom(voting: Union[OrdinalElection, list[list[int]]], size_of_committee: int, algorithm: ILP = ILP(Gurobi)) -> list[int]:
    """Custom implementation of the chamberlin courant rule.

    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
    Returns:
        list[int]: List of chosen candidates
    """

    def define_model(voting: OrdinalElection, size_of_committee: int, solver: solver_t) -> model_t:
        model = solver()
        x = [model.addVariable(f"x_{i}", 'B') for i in range(voting.ballot_size)]

        y = []
        for i, vote in enumerate(voting):
            y.append([None]*voting.ballot_size)
            for j, candidate in enumerate(vote):
                y[-1][candidate] = (model.addVariable(
                    f"y_{i}_{j}", "B", voting.ballot_size - j))

        model.addConstraint("sum(x) == k", x, [1]*len(x), size_of_committee, 'E')

        for i in range(voting.number_of_voters):
            model.addConstraint(f"sum(y[{i}]) == 1", y[i], [1]*len(y[i]), 1, 'E')
            for j in range(voting.ballot_size):
                model.addConstraint(f"x_{j} >= y_{i}_{j}", [
                                    x[j], y[i][j]], [1, -1], 0, 'G')

        return model

    algorithm.prepare(define_model)
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
    print(
        chamberlin_courant(
            election,
            2,
            algorithm=PAlgorithm()
        )
    )
    print(
        chamberlin_courant(
            election,
            2,
            algorithm=ILP(Gurobi)
        )
    )
    print(
        chamberlin_courant(
            election,
            2,
            algorithm=ILP(CPLEX)
        )
    )

    print(
        chamberlin_courant_ilp_custom(
            election,
            2,
            algorithm=ILP(Gurobi)
        )
    )
    print(
        chamberlin_courant_ilp_custom(
            election,
            2,
            algorithm=ILP(CPLEX)

        )
    )
