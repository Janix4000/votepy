
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Union


@dataclass
class Rule:
    shortname: str
    longname: str
    algorithms: tuple[str]
    scoring_function: Callable
    
@dataclass
class Algorithm:
    shortname: str
    longname: str
    algorithm: Callable


RULES: dict[str, Rule] = {}
ALGORITHMS: dict[str, Algorithm] = {}
PREFERRED_IMPLEMENTATION: dict[str, dict[str, Callable]] = defaultdict(dict)


def scoring_function(rule_id: str = None,
                     shortname: str = None,
                     longname: str = None,
                     algorithm: Union[str, tuple] = None):
    
    def decorator(func):
        nonlocal rule_id, shortname, longname, algorithm
        if rule_id is None:
            rule_id = func.__name__
        
        if rule_id in RULES:
            raise ValueError(f'{rule_id} is already defined.')
        
        rule = Rule(shortname, longname, algorithm, func)
        RULES[rule_id] = rule
        
        return func
    return decorator


def algorithm(algorithm_id: str = None,
                     shortname: str = None,
                     longname: str = None):
    
    def decorator(func):
        nonlocal algorithm_id, shortname, longname
        if algorithm_id is None:
            algorithm_id = func.__name__
        
        if algorithm_id in ALGORITHMS:
            raise ValueError(f'{algorithm_id} is already defined.')
        
        algorithm = Algorithm(shortname, longname, func)
        ALGORITHMS[algorithm_id] = algorithm
        
        return func
    return decorator

def preferred_implementation(rule_id: str = None, algorithm_id:str = None):
    def decorator(func):
        nonlocal rule_id, algorithm_id
        algorithms = PREFERRED_IMPLEMENTATION[rule_id]
        if algorithm_id in algorithms:
            raise ValueError(f'{algorithm_id} is already defined for {rule_id}.')
        
        algorithms[algorithm_id] = func
        
        return func
    return decorator