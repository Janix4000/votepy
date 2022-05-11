from ordinal_election import OrdinalElection
from typing import Callable, Iterable
from itertools import combinations
import random

def default_prob(temp: int, initial_temp: int, p: float=0.02, q: float=0.999) -> float:
    """Default probability function proposed by Faliszewski, with default parameters also proposed by Faliszewski.

    Args:
        temp (int): Current temperature/iteration of the algorithm.
        initial_temp (int): Initial temperature of the usingalgorithm.
        p (float, optional): Initial probability of accepting committee with worse score than the current one. Defaults to 0.02.
        q (float, optional): Variable modelling the speed of which porobability p decays with iteration number. Defaults to 0.999.

    Returns:
        float: Probability of accepting committee with worse score than the current one. Defaults
    """
    return p * pow(q, temp)
    


def simulated_annealing(voting: OrdinalElection, size_of_committee: int, scoring_function: Callable[[Iterable[int], OrdinalElection], int], initial_temp: int, temp_prob: Callable[[int, int, dict], float] = default_prob, **temp_kwargs) -> list[int]:
    """A simulated annealing algorithm that calculates the winning committee using a given scoring function

    Args:
        voting (OrdinalElection): Voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        scoring_function (Callable[[Iterable[int], OrdinalElection], int]): The scoring function used to determine the best committee. It should take the committee and election as parameters and return the score of that committee.
        initial_temp (int): Number of iterations
        temp_prob: (Callable[[int, int, dict], float]): The probability that worse result is chosen. It is function of current temperature, initial temperature and additional **temp_kwargs.
        **temp_kwargs: Additional temp_prob arguments.
    Returns:
        list[int]: The winning committee
    """
    current_committee = random.sample(range(voting.ballot_size), size_of_committee)
    
    current_score = scoring_function(current_committee, voting)
    best_committee, best_score = current_committee, current_score

    rest_candidates = list(set(range(voting.ballot_size)) - set(current_committee))
    
    for temperature in range(initial_temp, 0, -1):
        remove_idx = random.randint(0, len(current_committee) - 1)
        add_idx = random.randint(0, len(rest_candidates) - 1)
        current_committee[remove_idx], rest_candidates[add_idx] = rest_candidates[add_idx], current_committee[remove_idx]
        new_score = scoring_function(current_committee, voting)
        if new_score > best_score or random.random() < temp_prob(temperature, initial_temp, **temp_kwargs):
            best_committee, best_score = current_committee, current_score
        else:
            current_committee[remove_idx], rest_candidates[add_idx] = rest_candidates[add_idx], current_committee[remove_idx]
    
    return best_committee