
from dataclasses import dataclass
from typing import Callable, Union


@dataclass
class Rule:
    shortname: str
    longname: str
    strategies: tuple[str]
    scoring_function: Callable
    
@dataclass
class Algorithm:
    shortname: str
    longname: str
    algorithm: Callable


RULES: dict[str, Rule] = {}
ALGORITHMS: dict[str, Algorithm] = {}


def scoring_function(rule_id: str = None,
                     shortname: str = None,
                     longname: str = None,
                     algorithm: Union[str, tuple] = None):
    
    if rule_id in RULES:
        
    
    def decorator(func):
        return func
    return decorator

