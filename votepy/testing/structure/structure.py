from votepy.testing.algorithms.base_algorithm import BaseAlgorithm

from functools import wraps
from typing import Callable, Union
import inspect


implementations: dict[str, dict[str, Callable]] = dict()
algorithms: dict[str, BaseAlgorithm] = dict()
rules: dict[str, Callable] = dict()


def algo(name: str):
    def inner(Algorithm):
        Algorithm.name = name
        algorithms[name] = Algorithm
        return Algorithm
    return inner


def get_algorithm(algorithm: Union[str, BaseAlgorithm], *args, **kwargs) -> BaseAlgorithm:
    if isinstance(algorithm, str):
        if algorithm not in algorithms:
            raise ValueError(
                f"Algorithm {algorithm} not registered. Remember to register algorithm class and give it proper name with `@algo(name=)` decorator.")
        algorithm = algorithms[algorithm]

    if inspect.isclass(algorithm):
        return algorithm(*args, **kwargs)

    if isinstance(algorithm, BaseAlgorithm):
        return algorithm

    if isinstance(algorithm, object):
        raise TypeError(f"Algorithm {algorithm} must derive from the `BaseAlgorithm`")


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
        implementations[rule_name] = {}

        return wrapper
    return actual_decorator


def impl(rule: Callable, algorithm: BaseAlgorithm):
    def actual_decorator(implementation):

        @wraps(implementation)
        def wrapper(*args, **kwargs):
            return implementation(*args, **kwargs)

        rule_name = rule if isinstance(rule, str) else rule.__name__
        algorithm_name = algorithm if isinstance(
            algorithm, str) else algorithm.name
        implementations[rule_name][algorithm_name] = wrapper

        return wrapper
    return actual_decorator


def get_implementation(rule: Callable, algorithm: BaseAlgorithm) -> Callable:
    rule_name = rule if isinstance(rule, str) else rule.__name__
    algorithm_name = algorithm if isinstance(
        algorithm, str) else algorithm.name

    if rule_name not in implementations:
        raise ValueError(f"Rule {rule_name} has not been registered. Remember to register the main rule function with `@rule()` decorator.")

    rule_implementations = implementations[rule_name]

    if algorithm_name not in rule_implementations:
        raise ValueError(f"Algorithm {algorithm_name} has not been adapted to {rule_name}. Remember to register algorithm use with `@impl()` decorator.")

    return rule_implementations[algorithm_name]
