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


def rule(auto_imp: bool = False):
    def inner(rule: Callable):
        rule_name = rule if isinstance(rule, str) else rule.__name__
        rules[rule_name] = rule
        if auto_imp:
            raise NotImplementedError()
            # @wraps(rule)
            # def auto_fun(*args, algorithm=None, **kwargs):
            #     algorithm_name = algorithm if isinstance(
            #         algorithm, str) else algorithm.name
            #     implementation = implementations[rule_name][algorithm_name]
            #     return implementation(*args, algorithm=algorithm, **kwargs)
            # return auto_fun
        else:
            return rule
    return inner
