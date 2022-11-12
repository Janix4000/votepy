from typing import Type, Union
from votepy.ordinal_election import OrdinalElection
from votepy.generic_ilp import CPLEX, Gurobi, Solver
from votepy.rules.chamberlin_courant import chamberlin_courant_ilp_custom, chamberlin_courant_ilp
from votepy.rules.k_borda import k_borda

import numpy as np


def owa_ilp(voting,
            size_of_committee,
            owa_vector,
            solver: Union[Type[Gurobi], Type[CPLEX]] = CPLEX):
    """
    ILP implementation of the OWA rule as described by:
    Piotr Skowron, Piotr Faliszewski, Jerome Lang
    Finding a Collective Set of Items: From Proportional Multirepresentation to Group Recommendation
	arXiv:1402.3044

    Variables are named exactly as in the paper, to make cross-checking easier.
    """
    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)
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
                                    [x_ijk[i, j, k], x_i[j]], [1, -1], 0, 'L')

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
                f"(e) sum u_{i}_aj*x_{i}_j_{k} >= sum u_{i}_aj*x_{i}_j_{k + 1}",
                vars, u[i] + list(map(lambda x: -x, u[i])), 0, 'G')

    model.solve()

    best_committee = []
    for i, v in enumerate(model.getValues()[:M]):
        if v == 1:
            best_committee.append(i)
    return best_committee


def owa_k_median(voting, size_of_committee, k, solver):
    if not 1 <= k <= size_of_committee:
        raise ValueError(
            f"Expected k to be an integer from range 1 to {size_of_committee}, got: {k}")
    owa_vector = [0] * (k - 1) + [1] + [0] * (size_of_committee - k)
    owa_ilp(voting, size_of_committee, owa_vector, solver)


def owa_k_best(voting, size_of_committee, k, solver):
    if not 1 <= k <= size_of_committee:
        raise ValueError(
            f"Expected k to be an integer from range 1 to {size_of_committee}, got: {k}")
    owa_vector = [1] * k + [0] * (size_of_committee - k)
    owa_ilp(voting, size_of_committee, owa_vector, solver)


def owa_arithmetic_progression(voting, size_of_committee, a, solver):
    if not a >= 0:
        raise ValueError(
            f"Expected a to be a positive number, got: {a}")
    owa_vector = [a + k for k in range(size_of_committee-1, -1, -1)]
    owa_ilp(voting, size_of_committee, owa_vector, solver)


def owa_geometric_progression(voting, size_of_committee, p, solver):
    if not p > 1:
        raise ValueError(
            f"Expected p to be greater than 1, got: {p}")
    owa_vector = [p ** k for k in range(size_of_committee-1, -1, -1)]
    owa_ilp(voting, size_of_committee, owa_vector, solver)


def owa_harmonic(voting, size_of_committee, solver):
    owa_vector = [1 / k for k in range(1, size_of_committee+1)]
    owa_ilp(voting, size_of_committee, owa_vector, solver)


def owa_hurwicz(voting, size_of_committee, p, solver):
    if not 0 <= p <= 1:
        raise ValueError(
            f"Expected p to be in range 0 to 1, got: {p}")
    owa_vector = [p] + [0] * (size_of_committee-2) + [1-p]
    owa_ilp(voting, size_of_committee, owa_vector, solver)



if __name__ == '__main__':
    voting = [
        [0, 1, 2, 4, 5, 3],
        [0, 1, 2, 4, 5, 3],
        [0, 1, 2, 4, 5, 3],
        [5, 0, 3, 2, 4, 1],
        [5, 0, 3, 2, 4, 1],
        [4, 3, 1, 2, 5, 0]
    ]
    size_of_committee = 3
    print(chamberlin_courant_ilp(voting, size_of_committee))
    print(owa_ilp(voting, size_of_committee, [1, 0, 0], solver=Gurobi))
    print(owa_ilp(voting, size_of_committee, [1, 1, 1], solver=Gurobi))
    print(k_borda(voting, size_of_committee))
