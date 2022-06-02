import itertools
from ordinal_election import OrdinalElection
from typing import Callable, Iterable, Union

from math import comb
from collections import defaultdict

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
    
    m_candidates = voting.ballot_size
    k_committee = size_of_committee
    
    voters_ws_less = [[0] * m_candidates for _ in range(voting.number_of_voters)]
    voters_ws_greater = [[0] * m_candidates for _ in range(voting.number_of_voters)]
    
    combinations = defaultdict(lambda t: comb(*t))
    
    def delta_wave(candidate, voter, ws_less, ws_greater):
        candidate_pos = voter.pos(candidate)
        w_less, w_greater = ws_less[candidate], ws_greater[candidate]
        
        t_min = w_less + 1
        t_max = min(len(lambdas) - 1, k_committee - 2 - w_greater)
        
        
        l_up = candidate_pos - 1 - w_less
        l_down = -1 - w_less
        r_up = m_candidates - candidate_pos - 1 - w_greater
        r_down = k_committee - 1 - w_greater
        
        if any(p <= 0 for p in (l_up, l_down, r_up, r_down)):
            return 0
        
        c_size = combinations[(l_up, t_min + 1 + l_down )] * combinations[(r_up, r_down - t_min - 1 )]
        
        score = 0
        
        for t in range(t_min + 1, t_max + 1):
            score += c_size * gammas(t, 1)(candidate_pos)
            c_size = c_size / (t + l_down + 1) * (t + l_down)
            # c_size = c_size // (t + l_down + 1) * (t + l_down)
        return score
    
    def delta(other, candidate, voter, ws_less, ws_greater):
        other_pos, candidate_pos = voter.pos(other), voter.pos(candidate)
        w_less, w_greater = ws_less[other], ws_greater[other]
        r_d = int(other_pos < candidate_pos)
        
        t_min = w_less + 1
        t_max = min(len(lambdas) - 1, k_committee - 2 - w_greater)
        
        
        l_up = other_pos - 1 - w_less
        l_down = -1 - w_less
        r_up = m_candidates - other_pos - 1 - w_greater
        r_down = k_committee - 1 - w_greater
        
        if any(p <= 0 for p in (l_up, l_down, r_up, r_down)):
            return 0
        
        c_size = combinations[(l_up, t_min + 1 + l_down )] * combinations[(r_up, r_down - t_min - 1 )]
        
        score = 0
        
        for t in range(t_min + 1, t_max + 1):
            score += c_size * (gammas(t, 1)(other_pos) - gammas(t + r_d, 0)(other_pos))
            c_size = c_size / (t + l_down + 1) * (t + l_down)
            # c_size = c_size // (t + l_down + 1) * (t + l_down)
        return score
    
    def banzhaf_scoring_function(candidate):
        score = 0
        for voter, ws_less, ws_greater in zip(voting, voters_ws_less, voters_ws_greater):
            score += delta_wave(candidate, ws_less, ws_greater) + sum(delta(voter.pos(other), candidate, ws_less, ws_greater) for other in range(m_candidates) if other != candidate)
    
    def update_ws(current_best_candidate):
        for voter, ws_less, ws_greater in zip(voting, voters_ws_less, voters_ws_greater):
            current_best_candidate_pos = voter.pos(current_best_candidate)
            for candidate in range(voting.ballot_size):
                if candidate == current_best_candidate:
                    continue
                candidate_pos = voter.pos(candidate)
                if current_best_candidate_pos < candidate_pos:
                    ws_less[candidate] += 1
                    ws_greater[candidate] -= 1
                else:
                    ws_less[candidate] -= 1
                    ws_greater[candidate] += 1
    
    w_resultant_committee = []
    best_score = 0
    remaining_candidates = set(i for i in range(voting.ballot_size))
    for _ in range(size_of_committee):
        current_best_candidate, current_best_score = -1, best_score
        for candidate in remaining_candidates:
            score = banzhaf_scoring_function(candidate)
            if score > current_best_score:
                current_best_candidate = candidate
                current_best_score = score
        remaining_candidates.remove(current_best_candidate)
        w_resultant_committee.append(current_best_candidate)
        
        update_ws(current_best_candidate)
                    
        best_score = current_best_score

    return w_resultant_committee