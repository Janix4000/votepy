from typing import Type, Union
from votepy.ordinal_election import OrdinalElection
from votepy.generic_ilp import CPLEX, Gurobi
from votepy.rules.chamberlin_courant_impl import chamberlin_courant
from votepy.rules.k_borda_impl import k_borda
from votepy.meta.structure import algo, rule, impl
from votepy.solve import solve
from votepy.algorithms.base_ilp import ILP
from votepy.generic_ilp import Solver

import numpy as np


@algo(name='owa')
class OWA(ILP):
    pass


@rule()
def owa(voting: Union[OrdinalElection,
                      list[list[int]]], size_of_committee: int,
        owa_vector: list[float], algorithm: OWA):
    """# Summary
    OWA rule
    ## Args:
        `voting` (`OrdinalElection | list[int]`): Voting for which the function calculates the committee
        `size_of_committee` (`int`): Size of the committee
        `owa_vector` (`list[float]`): Vector of weights as defined in the OWA rule
        `algorithm` (`BaseAlgorithm`): Algorithm to use

    ## Returns:
        `list[int]`: List of chosen candidates

    ## Examples

    """
    return solve(owa,
                 voting,
                 size_of_committee,
                 owa_vector,
                 algorithm=algorithm)


@impl(owa, ILP)
def owa_ilp(voting: Union[OrdinalElection, list[list[int]]],
            size_of_committee: int,
            owa_vector: list[float],
            algorithm: OWA = OWA()):
    """
    ILP implementation of the OWA rule as described by:
    Piotr Skowron, Piotr Faliszewski, Jerome Lang
    Finding a Collective Set of Items: From Proportional Multirepresentation to Group Recommendation
        arXiv:1402.3044

    Variables are named exactly as in the paper, to make cross-checking easier.
    """

    def define_model(voting: OrdinalElection, size_of_committee: int,
                     solver: Union[Type[Gurobi], Type[CPLEX]]):
        """NOTE: owa_vector is passed as closure"""
        # model = solver(Solver.Sense.MIN)
        model = solver()

        N = voting.number_of_voters
        M = voting.ballot_size
        K = size_of_committee

        u = voting.get_positions()
        for i in range(N):
            for j in range(M):
                # In OWA-based rules, [u] is treated as the utility provided to the voter - the bigger, the better
                u[i][j] = M - u[i][j] - 1

        x_i = [model.addVariable(f"x_{i}", 'B') for i in range(M)]

        x_ijk = np.ndarray((N, M, K), object)
        for i in range(N):
            for j in range(M):
                for k in range(K):
                    x_ijk[i, j, k] = model.addVariable(f"x_{i}_{j}_{k}", 'B',
                                                       owa_vector[k] * u[i][j])

        model.addConstraint(f"(a) sum(x_i) == K", x_i, [1] * len(x_i), K, 'E')

        for i in range(N):
            for j in range(M):
                for k in range(K):
                    # Changed to sum over N,M,K instead of N,K^2
                    model.addConstraint(f"(b) x_{i}_{j}_{k} <= x_{j}",
                                        [x_ijk[i, j, k], x_i[j]], [1, -1], 0,
                                        'L')

        for i in range(N):
            for k in range(K):
                vars = x_ijk[i, :, k]
                model.addConstraint(f"(c) sum x_{i}_j_{k} == 1", vars,
                                    [1] * len(vars), 1, 'E')

        for i in range(N):
            for j in range(M):
                vars = x_ijk[i, j, :]
                # Changed to 'less than' from 'equal'
                model.addConstraint(f"(d) sum x_{i}_{j}_k <= 1", vars,
                                    [1] * len(vars), 1, 'L')

        for i in range(N):
            for k in range(K - 1):
                vars = np.concatenate((x_ijk[i, :, k], x_ijk[i, :, k + 1]))
                model.addConstraint(
                    f"(e) sum u_{i}_aj*x_{i}_j_{k} >= sum u_{i}_aj*x_{i}_j_{k+1}",
                    vars, u[i] + list(map(lambda x: -x, u[i])), 0, 'G')

        return model

    algorithm.prepare(define_model)
    return algorithm.solve(voting, size_of_committee)


@impl('owa_k_median', algorithm=OWA)
@rule()
def owa_k_median(voting: Union[OrdinalElection, list[list[int]]], size_of_committee: int, k: int, algorithm: OWA = OWA()):
    """# Calculates committee using owa_ilp with owa_vector set to k-1 zeros, single one and followed by size_of_committee - k zeros

    ### Args:
        `voting` (OrdinalElection | list[list[int]]): Voting for which the function calculates the committee
        `size_of_committee` (int): Size of the committee
        `k` (int): Parameter describing how many zeros precide and follow single one weight in owa_vector
        `algorithm` (`BaseAlgorithm`): algorithm used to calculate owa rule

    ### Returns:
        `list[int]`: List of chosen candidates

    ### Examples
    >>> import votepy as vp
    >>> voting = [
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [4, 3, 1, 2, 5, 0]
    ... ]
    >>> vp.solve('owa_k_median', voting, 3, k=2, algorithm=OWA(Gurobi))
    [0, 1, 3]
    """

    if not 1 <= k <= size_of_committee:
        raise ValueError(
            f"Expected k to be an integer from range 1 to {size_of_committee}, got: {k}")
    owa_vector = [0] * (k - 1) + [1] + [0] * (size_of_committee - k)
    return owa_ilp(voting, size_of_committee, owa_vector, algorithm=algorithm)


@impl('owa_k_best', algorithm=OWA)
@rule()
def owa_k_best(voting, size_of_committee, k, algorithm: OWA = OWA()):
    """# Calculates committee using owa_ilp with owa_vector set to k ones and size_of_committee - k zeros

    ### Args:
        voting (OrdinalElection | list[list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        k (int): Parameter describing how many ones are at the beginning of owa_vector
        algorithm (`BaseAlgorithm`): algorithm used to calculate owa rule

    ### Returns:
        `list[int]`: List of chosen candidates

    ### Examples
    >>> import votepy as vp
    >>> voting = [
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [4, 3, 1, 2, 5, 0]
    ... ]
    >>> vp.solve('owa_k_best', voting, 3, k=2, algorithm=OWA(Gurobi))
    [0, 1, 5]
    """
    if not 1 <= k <= size_of_committee:
        raise ValueError(
            f"Expected k to be an integer from range 1 to {size_of_committee}, got: {k}")
    owa_vector = [1] * k + [0] * (size_of_committee - k)
    return owa_ilp(voting, size_of_committee, owa_vector, algorithm)


@impl('owa_arithmetic_progression', algorithm=OWA)
@rule()
def owa_arithmetic_progression(voting, size_of_committee, a, algorithm: OWA = OWA()):
    """# Calculates committee using arithmetic progression in owa_vector weights

    ### Args:
        voting (OrdinalElection | list[list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        a (int): Free expression of arithmetic progression
        algorithm (`BaseAlgorithm`): algorithm used to calculate owa rule

    ### Returns:
        `list[int]`: List of chosen candidates

    ### Examples
    >>> import votepy as vp
    >>> voting = [
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [4, 3, 1, 2, 5, 0]
    ... ]
    >>> vp.solve('owa_arithmetic_progression', voting, 3, a=2, algorithm=OWA(Gurobi))
    [0, 1, 5]
    """
    if not a >= 0:
        raise ValueError(
            f"Expected a to be a positive number, got: {a}")
    owa_vector = [a + k for k in range(size_of_committee - 1, -1, -1)]
    return owa_ilp(voting, size_of_committee, owa_vector, algorithm)


@impl('owa_geometric_progression', algorithm=OWA)
@rule()
def owa_geometric_progression(voting, size_of_committee, p, algorithm: OWA = OWA()):
    """# Calculates committee using owa_geometric_progression in owa_vector weights

    ### Args:
        voting (OrdinalElection | list[list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        p (int): Common ratio of geometric progression
        algorithm (`BaseAlgorithm`): algorithm used to calculate owa rule

    ### Returns:
        `list[int]`: List of chosen candidates

    ### Examples
    >>> import votepy as vp
    >>> voting = [
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [4, 3, 1, 2, 5, 0]
    ... ]
    >>> vp.solve('owa_geometric_progression', voting, 3, p=2, algorithm=OWA(Gurobi))
    [0, 1, 5]
    """
    if not p > 1:
        raise ValueError(
            f"Expected p to be greater than 1, got: {p}")
    owa_vector = [p ** k for k in range(size_of_committee - 1, -1, -1)]
    return owa_ilp(voting, size_of_committee, owa_vector, algorithm)


@impl('owa_harmonic', algorithm=OWA)
@rule()
def owa_harmonic(voting, size_of_committee, algorithm: OWA = OWA()):
    """# Calculates committee using harmonic series in owa_vector weights

    ### Args:
        voting (OrdinalElection | list[list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        algorithm (`BaseAlgorithm`): algorithm used to calculate owa rule

    ### Returns:
        `list[int]`: List of chosen candidates

    ### Examples
    >>> import votepy as vp
    >>> voting = [
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [4, 3, 1, 2, 5, 0]
    ... ]
    >>> vp.solve('owa_harmonic', voting, 3, algorithm=OWA(Gurobi))
    [0, 1, 5]
    """
    owa_vector = [1 / k for k in range(1, size_of_committee + 1)]
    return owa_ilp(voting, size_of_committee, owa_vector, algorithm)


@impl('owa_hurwicz', algorithm=OWA)
@rule()
def owa_hurwicz(voting, size_of_committee, p, algorithm: OWA = OWA()):
    """# Calculates committee using owa_vector weights set to (p, 0, 0, ..., 0, 1-p)

    ### Args:
        voting (`OrdinalElection` | `list[list[int]]`): Voting for which the function calculates the committee
        size_of_committee (`int`): Size of the committee
        p (`int`): Parameter used in owa_vectors
        algorithm (`BaseAlgorithm`): algorithm used to calculate owa rule

    ### Returns:
        `list[int]`: List of chosen candidates

    ### Examples
    >>> import votepy as vp
    >>> voting = [
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [0, 1, 2, 4, 5, 3],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [5, 0, 3, 2, 4, 1],
    ...     [4, 3, 1, 2, 5, 0]
    ... ]
    >>> vp.solve('owa_hurwicz', voting, 3, p=0.5, algorithm=OWA(Gurobi))
    [0, 2, 4]
    """
    if not 0 <= p <= 1:
        raise ValueError(
            f"Expected p to be in range 0 to 1, got: {p}")
    owa_vector = [p] + [0] * (size_of_committee - 2) + [1 - p]
    return owa_ilp(voting, size_of_committee, owa_vector, algorithm)


if __name__ == '__main__':
    voting = [[0, 1, 2, 4, 5, 3], [0, 1, 2, 4, 5, 3], [0, 1, 2, 4, 5, 3],
              [5, 0, 3, 2, 4, 1], [5, 0, 3, 2, 4, 1], [4, 3, 1, 2, 5, 0]]
    size_of_committee = 3
    print(chamberlin_courant(voting, size_of_committee, algorithm=ILP(Gurobi)))
    print(owa(voting, size_of_committee, [1, 0, 0], algorithm=OWA(Gurobi)))
    print(owa(voting, size_of_committee, [1, 1, 1], algorithm=OWA(Gurobi)))
    print(k_borda(voting, size_of_committee))
