from ordinal_election import OrdinalElection
from typing import Callable, Iterable

from generic_greed import greedy
from math import comb


def banzhaf_naive_impl(voting: OrdinalElection, size_of_committee: int,
           scoring_function: Callable[[int, int], int]) -> list[int]:
    """A generic greedy algorithm that calculates the winning committee using a given scoring function
    Args:
        voting (OrdinalElection): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        scoring_function (Callable[[int, int], int]): The single-winner scoring function. It should take the position of the candidate and size of the committee and return the single score of that candidate. Scoring function of the committee must be expressed as ∑γ(pos(voter)).

    Returns:
        list[int]: The winning committee
    """
    
    
    def banzhaf_scoring_function(w, voting, c):
        
        def banzhaf_scoring_function_vote(w, vote, c):
            
            def c_size(pos_d, t, w_a, w_b):
                m = len(voting)
                k = size_of_committee
                if t > w_a:
                    return comb(pos_d - 1 - w_a, t - 1 - w_a) * comb(m - pos_d - w_b, t - k - w_b)
                else:
                    return 0
            
            def get_w_a_b(w, d):
                w_a = 0
                for c in w:
                    if vote.pos(c) < d:
                        w_a += 1
                return w_a, len(w) - w_a
            
            def c_sum(pos_d, w):
                s = 0
                k = size_of_committee
                w_a, w_b = get_w_a_b(w, d)
                for t in range(1, k + 1):
                    s += c_size(pos_d, t, w_a, w_b)
                    
            def delta(d):
                pos_d = vote.pos(d)
                s = c_sum(pos_d, w)
                k = size_of_committee
                return (scoring_function(pos_d, k) - scoring_function(pos_d, k - 1)) * s
            
            def delta_prime(c):
                pos_c = vote.pos(c)
                s = c_sum(pos_c, w)
                k = size_of_committee
                return scoring_function(pos_c, k) * s
            
            res = delta_prime(c)
            for d in range(len(voting)):
                if d == c:
                    continue
                res += delta(d)

            return res
        
        res = 0
        for vote in voting:
            res += banzhaf_scoring_function_vote(w, vote, c)
        return res
    
    
    return greedy(voting, size_of_committee, banzhaf_scoring_function)

