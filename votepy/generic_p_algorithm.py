import random

from ordinal_election import OrdinalElection
from typing import Callable, Iterable


def simple_score(p, C):
    if not p: return -1
    m = len(p)
    for idx, vote in enumerate(p):
        if vote in C:
            return m - idx - 1


def simple_profile_score(P, C):
    return sum([simple_score(p, C) for p in P])


def p_algorithm(voting: OrdinalElection, size_of_committee: int,
                scoring_function: Callable[[Iterable[int], int, int], list[int]]) -> list[int]:
    num_candidates = voting.ballot_size

    best = -1
    best_t = -1
    winners = []

    for threshold in range(1, num_candidates):
        winners_try = scoring_function(voting, size_of_committee, threshold)
        curr = simple_profile_score(voting, winners_try)
        if curr > best:
            winners = [winners_try]
            best = curr
            best_t = [threshold]
        elif curr == best:
            winners.append(winners_try)
            best_t.append(threshold)
    return random.choice(winners)
