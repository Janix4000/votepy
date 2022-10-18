from typing import Type, Union
from ordinal_election import OrdinalElection
from generic_ilp import CPLEX, Gurobi, Solver
from chamberlin_courant import chamberlin_courant_ilp_custom
from k_borda import k_borda


import numpy as np


def owa_ilp(voting, size_of_committee, owa_vector, solver: Union[Type[Gurobi], Type[CPLEX]] = CPLEX, **kwargs):
    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)
    model = solver(**kwargs)

    N = voting.number_of_voters
    M = voting.ballot_size
    K = size_of_committee

    u = voting.get_positions()

    x_i = [model.addVariable(f"x_{i}", 'B') for i in range(M)]

    x_ijk = np.ndarray((N, M, K), object)
    for i in range(N):
        for j in range(M):
            for k in range(K):
                x_ijk[i, j, k] = model.addVariable(
                    f"x_{i}_{j}_{k}", 'B', owa_vector[k]*(M - u[i][j] - 1))

    model.addConstraint(f"(a) sum(x_i) == K", x_i, [1]*len(x_i), K, 'E')

    for i in range(N):
        for j in range(M):
            for k in range(K):
                model.addConstraint(f"(b) x_{i}_{j}_{k} <= x_{j}", [
                                    x_ijk[i, j, k], x_i[j]], [1, -1], 0, 'L')

    for i in range(N):
        for k in range(K):
            vars = x_ijk[i, :, k]
            model.addConstraint(f"(c) sum x_{i}_j_{k} == 1", vars, [1]*len(vars), 1, 'E')

    for i in range(N):
        for j in range(M):
            vars = x_ijk[i, j, :]
            model.addConstraint(f"(d) sum x_{i}_{j}_k <= 1", vars, [1]*len(vars), 1, 'L')

    for i in range(N):
        for k in range(K-1):
            print(np.concatenate(x_ijk[i, :, k],x_ijk[i, :, k+1]))
            model.addConstraint(f"(e) sum u_{i}_aj*x_{i}_j_{k} >= sum u_{i}_aj*x_{i}_j_{k+1}",
                                x_ijk[i, :, k]+x_ijk[i, :, k+1], u[i]+list(map(lambda x: -x, u[i])), 0, 'G')


    model.solve()
    # model._debug()

    best_committee = []
    for i, v in enumerate(model.getValues()[:M]):
        if v == 1:
            best_committee.append(i)
    return best_committee


if __name__ == '__main__':
    m = [
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ]
    # print(chamberlin_courant_ilp_custom(m, 2, 4))
    print(owa_ilp(m, 2, [1, 1, 1, 1]))
    print(k_borda(m, 2, 4))
