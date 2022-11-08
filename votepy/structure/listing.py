from typing import Callable, Union
import votepy.structure.structure as structure
from votepy.algorithms.base_algorithm import BaseAlgorithm


def algorithms(rule: Union[str, Callable] = None) -> dict[str, BaseAlgorithm]:
    if rule is not None:
        if not isinstance(rule, str):
            rule = rule.__name__
        rule_implementations = structure.implementations[rule]
        algorithms = {name: structure.algorithms[name] for name in rule_implementations}
    else:
        algorithms = structure.algorithms

    return algorithms


def rules() -> dict[str, Callable]:
    return structure.rules
