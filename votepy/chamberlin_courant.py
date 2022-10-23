from votepy.ordinal_election import OrdinalElection
from typing import Type, Union, Iterable
from votepy.generic_brute_force import brute_force
from votepy.generic_greed import greedy
from votepy.generic_ilp import CPLEX, Gurobi


def chamberlin_courant_ilp(voting: Union[OrdinalElection, list[int]], size_of_committee: int,
                           number_of_scored_candidates: int, solver: Union[Type[Gurobi], Type[CPLEX]] = Gurobi) -> list[int]:
    """Implementation of the chamberlin-courant rule, using ILP formulation by:
    Peters, Dominik & Lackner, Martin. (2020).
    Preferences Single-Peaked on a Circle.
    Journal of Artificial Intelligence Research. 68. 463-502. 10.1613/jair.1.11732.

    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidartes using k-borda rule
    Returns:
        list[int]: List of chosen candidates
    """
    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)

    model = solver()
    x = [[model.addVariable(f"x_{i},{r}", 'B', 1)
          for r in range(voting.ballot_size)]
         for i in range(voting.number_of_voters)]

    y = [model.addVariable(f"y_{c}", 'B', 0)
         for c in range(voting.ballot_size)]

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

    model.solve()

    best_committee = []
    for i, v in enumerate(model.getValues()[-voting.ballot_size:]):
        if v == 1:
            best_committee.append(i)
    return best_committee


def chamberlin_courant_ilp_custom(voting: Union[OrdinalElection, list[int]], size_of_committee: int,
                                  number_of_scored_candidates: int, solver: Union[Type[Gurobi], Type[CPLEX]] = Gurobi) -> list[int]:
    """Custom implementation of the chamberlin courant rule.

    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidartes using k-borda rule
    Returns:
        list[int]: List of chosen candidates
    """
    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)
    model = solver()

    x = [model.addVariable(f"x_{i}", 'B') for i in range(voting.ballot_size)]
    # for i in range(voting.ballot_size):
    #     x.append(model.addVariable(f"x_{i}", 'B'))

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

    model.solve()

    best_committee = []
    for i, v in enumerate(model.getValues()[:voting.ballot_size]):
        if v == 1:
            best_committee.append(i)
    return best_committee


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
    print("Brute_force:",
          chamberlin_courant_brute_force(
              election,
              2,
              5
          )
          )
    print(
        "Greedy:",
        chamberlin_courant_greedy(
            election,
            2,
            5
        )
    )
    print(
        "ILP article(Gurobi):",
        chamberlin_courant_ilp(
            election,
            2,
            5,
            Gurobi
        )
    )
    print(
        "ILP article(CPLEX):",
        chamberlin_courant_ilp(
            election,
            2,
            5,
            CPLEX
        )
    )
    print(
        "ILP custom(Gurobi):",
        chamberlin_courant_ilp_custom(
            election,
            2,
            5,
            Gurobi
        )
    )
    print(
        "ILP custom(CPLEX):",
        chamberlin_courant_ilp_custom(
            election,
            2,
            5,
            CPLEX
        )
    )
