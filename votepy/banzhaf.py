import itertools
from ordinal_election import OrdinalElection
from typing import Callable, Iterable, Union

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
        
        def banzhaf_scoring_function_vote(w, vote, candidate, m, k):
            
            def c_size(pos_d, t, m, k, w_a, w_b):
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
            
            def c_sum(pos_d, w, m, k):
                s = 0
                k = size_of_committee
                w_a, w_b = get_w_a_b(w, d)
                for t in range(1, k + 1):
                    s += c_size(pos_d, t, m, k, w_a, w_b)
                    
            def delta(d, m, k, w):
                pos_d = vote.pos(d)
                s = c_sum(pos_d, w, m, k)
                k = size_of_committee
                return (scoring_function(pos_d, k) - scoring_function(pos_d, k - 1)) * s
            
            def delta_prime(c, m, k, w):
                pos_c = vote.pos(c)
                s = c_sum(pos_c, w, m, k)
                return scoring_function(pos_c, k) * s
            
            
            
            
            res = delta_prime(candidate, m, k, w)
            for d in range(len(voting)):
                if d == candidate:
                    continue
                res += delta(d, m, k, w)

            return res
        
        res = 0
        k = size_of_committee
        m = voting.ballot_size
        for vote in voting:
            res += banzhaf_scoring_function_vote(w, vote, c, m, k)
        return res
    
    
    return greedy(voting, size_of_committee, banzhaf_scoring_function)

PosScoringFunction = Callable[[int], float]


def is_strictly_decreasing_sequence(sequence):
    first, second = itertools.tee(sequence)
    next(second)
    return all(earlier > later for earlier, later in zip(first, second))

def all_nonnegative(sequence):
    return all(x >= 0 for x in sequence)

def banzhaf(voting: OrdinalElection, size_of_committee: int, 
            scoring_functions: Union[PosScoringFunction, tuple[PosScoringFunction, PosScoringFunction]],
            lambdas: list[float]=None
            ):
    lambdas = list(lambdas) if lambdas is not None else [1] * size_of_committee
    if not is_strictly_decreasing_sequence(lambdas):
        raise ValueError('lambdas parameter must be strictly decreasing sequence!')
    if not all_nonnegative(lambdas):
        raise ValueError('lambdas parameter must contain only non-negative elements!')
    lambdas = lambdas + [0]
    
    if isinstance(scoring_functions, Callable):
        scoring_functions = (scoring_functions, scoring_functions)
    elif not isinstance(scoring_functions, tuple) or len(scoring_functions) < 2:
        raise ValueError('scoring_functions must be a function or tuple of two functions!')    
     
    
    gammas = lambda t, k: lambda pos: lambdas[t] * scoring_functions[k](pos) 
    
    
    