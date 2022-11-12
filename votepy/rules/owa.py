from typing import Type, Union
from votepy.ordinal_election import OrdinalElection
from votepy.generic_ilp import CPLEX, Gurobi
from votepy.rules.chamberlin_courant import chamberlin_courant
from votepy.rules.k_borda import k_borda
from votepy.meta.structure import algo, rule, impl
from votepy.solve import solve
from votepy.algorithms.base_ilp import ILP

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
                # In OWA-based rules, [u] is treated as the utility provided to the voter - the bigger the better
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


if __name__ == '__main__':
    voting = [[0, 1, 2, 4, 5, 3], [0, 1, 2, 4, 5, 3], [0, 1, 2, 4, 5, 3],
              [5, 0, 3, 2, 4, 1], [5, 0, 3, 2, 4, 1], [4, 3, 1, 2, 5, 0]]
    size_of_committee = 3
    print(chamberlin_courant(voting, size_of_committee, algorithm=ILP(Gurobi)))
    print(owa(voting, size_of_committee, [1, 0, 0], algorithm=ILP(Gurobi)))
    print(owa(voting, size_of_committee, [1, 1, 1], algorithm=ILP(Gurobi)))
    print(k_borda(voting, size_of_committee))
