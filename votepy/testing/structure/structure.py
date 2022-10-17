from votepy.testing.algorithms.base_algorithm import BaseAlgorithm

from functools import wraps
from typing import Callable, Union
import inspect


implementations: dict[str, dict[str, Callable]] = dict()
algorithms: dict[str, BaseAlgorithm] = dict()
rules: dict[str, Callable] = dict()


def algo(name: str):
    """# Summary
    Decorator used to register voting solving algorithm classes.
    Voting algorithm must derive from the `BaseAlgorithm`.

    ## Args:
        `name` (str): Identification name of the algorithm.

    ## Examples
    >>> from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
    >>> 
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def _solve():
    ...         pass
    >>>
        get_algorithm('name') == Algo()
    True
    """
    def inner(Algorithm):
        Algorithm.name = name
        algorithms[name] = Algorithm
        return Algorithm
    return inner


def get_algorithm(algorithm: Union[str, BaseAlgorithm], *args, **kwargs) -> BaseAlgorithm:
    """# Summary
    Returns initialized algorithm object, registered with `@algo(name=)` decorator.

    ## Args:
        `algorithm` (str | BaseAlgorithm): Name identification of the algorithm, class deriving from `BaseAlgorithm` or already initialized algorithm. 

    ## Raises:
        `ValueError`: Algorithm has not been registered.
        `TypeError`: Object did not derived from the `BaseAlgorithm`.

    ## Returns:
        -> BaseAlgorithm: Ready to use algorithm object. If the given algorithm is already an object, it is passed by.

    ## Examples
    >>> from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
    >>> 
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def _solve():
    ...         pass
    >>>
        get_algorithm('name') == Algo()
    True
        get_algorithm(Algo) == Algo()
    True
        get_algorithm(Algo()) == Algo()
    True
    """

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


def rule(name: str = None):
    """# Summary
    Decorator used to register a voting rule function.

    ### IT MUST BE USED WITH PARENTHESES, EVEN WITHOUT SPECIFYING `NAME` ARGUMENT.

    ## Args:
        `name` (str, optional): Identification name of the voting rule. Defaults to the name of the function.

    ## Examples
    >>> @rule()
    ... def some_rule():
    ...     pass
    """

    def actual_decorator(rule: Callable):
        @wraps(rule)
        def wrapper(*args, **kwargs):
            return rule(*args, **kwargs)

        rule_name = name if name is not None else rule.__name__
        rules[rule_name] = wrapper
        implementations[rule_name] = {}

        return wrapper
    return actual_decorator


def impl(rule: Union[Callable, str], algorithm: BaseAlgorithm):
    """# Summary
    Decorator used to register specific implementation of the voting rule solving function, using algorithm. 

    Implementation function must have `algorithm` argument.

    ## Args:
        `rule` (Callable): Rule function or its identification name.
        `algorithm` (BaseAlgorithm): Algorithm class or its identification name.

    ## Examples
    >>> from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
    >>> 
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def _solve():
    ...         pass
    >>>
    >>> @rule()
    ... def some_rule():
    ...     pass
    >>>
    >>> @impl(some_rule, Algo)
    ... def some_rule_algo(algorithm):
    ...     pass
    >>> 
    >>> get_implementation(some_rule, Algo) == some_rule_algo
    True
    """
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
