# own_cc.py
from votepy.meta.structure import rule, impl
from votepy.solve import solve
from votepy.algorithms import BaseAlgorithm, Greedy, BruteForce
from votepy.ordinal_election import OrdinalElection


@rule()
def my_cc(voting: list[list[int]], committee_size: int, algorithm: BaseAlgorithm) -> list[int]:
    return solve(my_cc, voting, committee_size, algorithm=algorithm)


@impl(my_cc, algorithm=Greedy)
def __my_cc_greedy(voting: OrdinalElection, committee_size: int, algorithm: Greedy) -> list[int]:

    def greedy_scoring_function(current_committee: list[int], voting: OrdinalElection, candidate: int) -> float:
        candidate_committee = set(current_committee) | {candidate}
        return __cc_scoring_function(candidate_committee, voting)

    algorithm.prepare(greedy_scoring_function)
    return algorithm.solve(voting, committee_size)


def __cc_scoring_function(committee: list[int], voting: OrdinalElection) -> float:
    committee = set(committee)
    score = 0
    m = voting.ballot_size
    for voter in voting:
        score += max(m - voter.pos(candidate) for candidate in committee)
    return score


@impl(my_cc, algorithm=BruteForce)
def __my_cc_brute_force(voting: OrdinalElection, committee_size: int, algorithm: BruteForce) -> list[int]:
    algorithm.prepare(__cc_scoring_function)
    return algorithm.solve(voting, committee_size)
