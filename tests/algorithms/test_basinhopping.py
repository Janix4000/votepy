from votepy.algorithms.basinhopping import BasinHopping
from votepy.ordinal_election import OrdinalElection
from votepy.rules.chamberlin_courant_impl import chamberlin_courant as cc, scoring_function as cc_score

voting = OrdinalElection([
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


def test_cc_basinhopping():
    exact_res = cc(voting, 2, 'brute_force')
    greedy_res = cc(voting, 2, 'greedy')
    bh_res = cc(voting, 2, BasinHopping(niter=20, x0=[1, 4], seed=2137))

    assert cc_score(greedy_res, voting) <= cc_score(bh_res, voting) <= cc_score(exact_res, voting)


if __name__ == '__main__':
    test_cc_basinhopping()
