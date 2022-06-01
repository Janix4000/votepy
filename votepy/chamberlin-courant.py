from ordinal_election import OrdinalElection
from typing import Type, Union, Iterable
from generic_brute_force import brute_force
from generic_greed import greedy
from generic_ilp import CPLEX, Gurobi


def chamberlin_courant_brute_force(voting: Union[OrdinalElection, list[int]], size_of_committee: int, number_of_scored_candidates: int) -> list[int]:
    """Brute force implementation of the chamberlin-courant rule
    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidartes using k-borda rule
    Returns:
        list[int]: List of chosen candidates
    """
    def scoring_function(committee: Iterable[int], voting: OrdinalElection, number_of_scored_candidates: int):
        committee = set(committee)
        score = 0
        for vote in voting:
            for i, candidate in enumerate(vote):
                if candidate in committee:
                    score += max(number_of_scored_candidates - i, 0)
                    break
        return score

    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)

    n = voting.ballot_size
    if size_of_committee > n or size_of_committee <= 0:
        raise ValueError(f"Size of committee needs to be from the range 1 to the number of all candidates.")

    return brute_force(voting, size_of_committee, lambda committee, voting: scoring_function(committee,
                                                                                             voting, number_of_scored_candidates))


def chamberlin_courant_greedy(voting: Union[OrdinalElection, list[int]], size_of_committee: int,
                              number_of_scored_candidates: int) -> list[int]:
    """Greedy implementation of the chamberlin-courant rule
    Args:
        voting (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidartes using k-borda rule
    Returns:
        list[int]: List of chosen candidates
    """

    def scoring_function(committee: Iterable[int], voting: OrdinalElection, candidate: int,
                         number_of_scored_candidates: int):
        committee = set(committee) | {candidate}
        score = 0
        for vote in voting:
            for i, candidate in enumerate(vote):
                if candidate in committee:
                    score += max(number_of_scored_candidates - i, 0)
                    break
        return score

    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)

    n = voting.ballot_size
    if size_of_committee > n or size_of_committee <= 0:
        raise ValueError(f"Size of committee needs to be from the range 1 to the number of all candidates.")

    return greedy(voting, size_of_committee,
                  lambda committee, voting, candidate: scoring_function(committee, voting, candidate,
                                                                        number_of_scored_candidates))

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
    x = []
    for i in range(voting.number_of_voters):
        x.append([])
        for r in range(voting.ballot_size):
            x[-1].append(model.addVariable(f"x_{i},{r}", 'B', 1))

    y = []
    for c in range(voting.ballot_size):
        y.append(model.addVariable(f"y_{c}", 'B', 0))

    model.addConstraint('sum(y)', y, [1 for _ in range(len(y))], size_of_committee, 'E')

    for i in range(voting.number_of_voters):
        for r in range(voting.ballot_size):
            model.addConstraint(
                'x[i][r] <= sum(y[c])',
                [x[i][r]] + [y[c] for c in voting[i][:r]],
                [1.0] + [-1.0 for _ in range(len(voting[i][:r]))],
                0,
                'L'
            )

    model.solve()

    best_committee = []
    for i,v in enumerate(model.getValues()[-voting.ballot_size:]):
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

    x = []
    for i in range(voting.ballot_size):
        x.append(model.addVariable(f"x_{i}", 'B'))

    y = []
    for i, vote in enumerate(voting):
        y.append([None]*voting.ballot_size)
        for j, candidate in enumerate(vote):
            y[-1][candidate] = (model.addVariable(f"y_{i}_{j}", "B", voting.ballot_size - j))

    model.addConstraint("sum(x) == k", x, [1]*len(x), size_of_committee, 'E')

    for i in range(voting.number_of_voters):
        model.addConstraint("sum(y[i]) == 1", y[i], [1]*len(y[i]), 1, 'E')
        for j in range(voting.ballot_size):
            model.addConstraint("x[j] >= y[i][j]", [x[j], y[i][j]], [1,-1], 0, 'G')

    model.solve()

    best_committee = []
    for i,v in enumerate(model.getValues()[:voting.ballot_size]):
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
