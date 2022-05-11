from ordinal_election import OrdinalElection
from typing import Union, Iterable

import rules

def solve(voting: Union[OrdinalElection, Iterable[int]], 
    rule: str, 
    algorithm: str = None, 
    **rule_kwargs) -> list[int]: 
    
    
    if rule in rules.PREFERRED_IMPLEMENTATION and algorithm in rules.PREFERRED_IMPLEMENTATION[rule]:
        solver = rules.PREFERRED_IMPLEMENTATION[rule][algorithm]
    else:
        if rule not in rules.RULES:
            raise ValueError(f'{rule} has been not implemented nor registered yet.')
        if not rules.ALGORITHMS[algorithm]:
            raise ValueError(f'{algorithm} has been not implemented nor registered yet.')
        
        scoring_function = rules.RULES[rule].scoring_function
        algorithm_function = rules.ALGORITHMS[algorithm].algorithm
        
        solver = lambda voting, **rule_kwargs: algorithm_function(voting, scoring_function, **rule_kwargs)

    return solver(voting, **rule_kwargs)