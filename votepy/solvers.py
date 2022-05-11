from ordinal_election import OrdinalElection
from typing import Union, Iterable

import rules

def solve(voting: Union[OrdinalElection, Iterable[int]], 
    size_of_committee: int,
    rule: str, 
    algorithm: str = None,
    algorithm_kwargs: dict = None, 
    **rule_kwargs) -> list[int]: 
    
    if algorithm_kwargs is None:
        algorithm_kwargs = {}
        
    if not isinstance(voting, OrdinalElection): 
        voting=OrdinalElection(voting)
    
    if size_of_committee > voting.ballot_size or size_of_committee <= 0:
        raise ValueError(f"Size of committee needs to be from the range 1 to the number of all candidates.")
    
    if rule in rules.PREFERRED_IMPLEMENTATION and algorithm in rules.PREFERRED_IMPLEMENTATION[rule]:
        solver = rules.PREFERRED_IMPLEMENTATION[rule][algorithm]
        return solver(voting, size_of_committee, rule_kwargs, algorithm_kwargs)
    else:
        if rule not in rules.RULES:
            raise ValueError(f'{rule} has been not implemented nor registered yet.')
        if not rules.ALGORITHMS[algorithm]:
            raise ValueError(f'{algorithm} has been not implemented nor registered yet.')
        
        scoring_function = rules.RULES[rule].scoring_function
        algorithm_function = rules.ALGORITHMS[algorithm].algorithm
        
        return algorithm_function(voting, size_of_committee, scoring_function, rule_kwargs=rule_kwargs, **algorithm_kwargs)