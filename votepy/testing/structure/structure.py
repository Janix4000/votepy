from votepy.testing.algorithms.base_algorithm import BaseAlgorithm

from functools import wraps
from typing import Callable


implementations: dict[str, dict[str, Callable]] = dict()
algorithms: dict[str, BaseAlgorithm] = dict()
rules: dict[str, Callable] = dict()


def impl(rule: Callable, algorithm: BaseAlgorithm):
    def inner(fun):
        rule_name = rule if isinstance(rule, str) else rule.__name__
        algorithm_name = algorithm if isinstance(
            algorithm, str) else algorithm.name
        implementations[rule_name][algorithm_name] = fun
        return fun
    return inner


def get_implementation(rule: Callable, algorithm: BaseAlgorithm):
    rule_name = rule if isinstance(rule, str) else rule.__name__
    algorithm_name = algorithm if isinstance(
        algorithm, str) else algorithm.name
    return implementations[rule_name][algorithm_name]


def algo(name: str):
    def inner(Algorithm):
        Algorithm.name = name
        algorithms[name] = Algorithm
        return Algorithm
    return inner


def rule(name: str = None, auto_imp: bool = False):
    def actual_decorator(rule: Callable):
        @wraps(rule)
        def wrapper(*args, **kwargs):
            if auto_imp:
                raise NotImplementedError()
            else:
                return rule(*args, **kwargs)

        rule_name = name if name is not None else rule.__name__
        rules[rule_name] = wrapper

        return wrapper
    return actual_decorator
