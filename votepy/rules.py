
from dataclasses import dataclass
from typing import Callable


@dataclass
class Rule:
    name: str
    shortname: str
    longname: str
    strategies: tuple[str]
    scoring_function: Callable
    
@dataclass
class Algorithm:
    name: str
    shortname: str
    longname: str
    algorithm: Callable


