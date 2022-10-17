from typing import Callable, Union
from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
from votepy.testing.structure.structure import get_algorithm, get_implementation


def solve(rule: Union[Callable, str], *rule_args, algorithm: BaseAlgorithm, **rule_kwargs):
    implementation = get_implementation(rule, algorithm)
    algorithm = get_algorithm(algorithm)
    return implementation(*rule_args, algorithm=algorithm, **rule_kwargs)
