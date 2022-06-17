from typing import Type, Union
from ordinal_election import OrdinalElection
from generic_ilp import CPLEX, Gurobi, Solver


import numpy as np


def owa_ilp(voting, size_of_committee, owa_vector, solver: Union[Type[Gurobi], Type[CPLEX]] = Gurobi):
    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)
    model = solver(Solver.Sense.MIN)

    N = voting.number_of_voters
    M = voting.ballot_size
    K = size_of_committee

    u = voting.get_positions()

    x_i = [model.addVariable(f"x_{i}", 'B') for i in range(M)]

    x_ijk = np.ndarray((N, M, K), object)
    for i, vote in enumerate(voting):
        for w, j in enumerate(vote):
            for k in range(K):
                x_ijk[i, j, k] = model.addVariable(
                    f"x_{i}_{j}_{k}", 'B', owa_vector[k]*(voting.ballot_size-w))
                model.addConstraint(f"(b) x_{i}_{j}_{k} <= x_{j}", [
                                    x_ijk[i, j, k], x_i[j]], [1, -1], 0, 'L')

    model.addConstraint(f"(a) sum(x_i) == K", x_i, [1 for _ in x_i], K, 'E')

    for i in range(N):
        for k in range(K):
            variables = x_ijk[i, :, k]
            model.addConstraint(f"(c) sum x_{i}_j_{k} == 1", variables, [
                                1 for _ in variables], 1, 'E')

    for i in range(N):
        for j in range(M):
            variables = x_ijk[i, j, :]
            model.addConstraint(f"(d) sum x_{i}_{j}_k == 1", variables, [
                                1 for _ in variables], 1, 'E')

    for i in range(N):
        for k in range(K-1):
            model.addConstraint(f"(e) sum u_{i}_aj*x_{i}_j_{k} >= sum u_{i}_aj*x_{i}_j_{k+1}",
                                x_ijk[i, :, k]+x_ijk[i, :, k+1], u[i]+list(map(lambda x: -x, u[i])), 0, 'G')

    best_committee = []
    for i, v in enumerate(model.getValues()[:M]):
        if v == 1:
            best_committee.append(i)
    return best_committee


if __name__ == '__main__':
    print(owa_ilp([
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ], 2, [1, 1, 1, 1]))
