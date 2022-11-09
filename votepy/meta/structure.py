from votepy.algorithms.base_algorithm import BaseAlgorithm

from functools import wraps
from typing import Callable, Iterable, Union
import inspect

from votepy.ordinal_election import OrdinalElection


algorithms: dict[str, BaseAlgorithm] = dict()
default_algorithms: dict[str, BaseAlgorithm] = dict()
rules: dict[str, Callable] = dict()
implementations: dict[str, dict[str, Callable]] = dict()


def algo(name: str):
    """# Summary
    Decorator used to register voting solving algorithm classes.
    Voting algorithm must derive from the `BaseAlgorithm`.

    ## Args:
        `name` (str): Identification name of the algorithm.

    ## Examples
    >>> from votepy.algorithms.base_algorithm import BaseAlgorithm
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
    Returns initialized algorithm object, registered with `@algo(name=)` decorator

    ## Args:
        `algorithm` (str | BaseAlgorithm): Name identification of the algorithm, class deriving from `BaseAlgorithm` or already initialized algorithm

    ## Raises:
        `ValueError`: Algorithm has not been registered.
        `TypeError`: Object did not derived from the `BaseAlgorithm`.

    ## Returns:
        -> BaseAlgorithm: Ready to use algorithm object. If the given algorithm is already an object, it is passed by.

    ## Examples
    >>> from votepy.algorithms.base_algorithm import BaseAlgorithm
    >>>
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def __init__(self, arg=0):
    ...         self.arg = arg
    ...
    ...     def _solve():
    ...         pass
    ...
    ...     def __eq__(self, rhs):
    ...         return self.arg == rhs.arg
    >>>
    >>> get_algorithm('name') == Algo()
    True
    >>> get_algorithm(Algo) == Algo()
    True
    >>> get_algorithm(Algo()) == Algo()
    True
    >>> get_algorithm(Algo(arg=10)) == Algo(arg=10)
    True
    """

    if algorithm is None:
        return None

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


def rule(name: str = None, default_algorithm: Union[BaseAlgorithm, str] = None):
    """# Summary
    Decorator used to register a voting rule function.

    ### IT MUST BE USED WITH PARENTHESES, EVEN WITHOUT SPECIFYING `NAME` ARGUMENT.

    ## Args:
        `name` (str, optional): Identification name of the voting rule. Defaults to the name of the function
        `default_algorithm` (BaseAlgorithm | str): Default algorithm class or its identification name. Defaults to None (no default algorithm)

    ## Examples
    >>> @rule()
    ... def some_rule():
    ...     pass
    """

    def actual_decorator(rule: Callable):
        @wraps(rule)
        def wrapper(voting, size_of_committee, *args, **kwargs):
            if not isinstance(voting, OrdinalElection) and isinstance(voting, Iterable):
                voting = OrdinalElection(voting)
            if isinstance(voting, OrdinalElection):
                n = voting.ballot_size
                if size_of_committee > n or size_of_committee <= 0:
                    raise ValueError(
                        f"Size of committee needs to be from the range 1 to the number of all candidates.")

            result = rule(voting, size_of_committee, *args, **kwargs)
            if isinstance(result, Iterable):
                result = list(result)
            return result

        rule_name = name if name is not None else rule.__name__
        rules[rule_name] = wrapper
        implementations[rule_name] = {}
        if default_algorithm is not None:
            default_algorithms[rule_name] = get_algorithm(default_algorithm).__class__
        else:
            default_algorithms[rule_name] = None

        return wrapper
    return actual_decorator


def impl(rule: Union[Callable, str], algorithm: BaseAlgorithm):
    """# Summary
    Decorator used to register specific implementation of the voting rule solving function, using algorithm

    Implementation function must have `algorithm` argument

    ## Args:
        `rule` (Callable): Rule function or its identification name
        `algorithm` (BaseAlgorithm): Algorithm class or its identification name

    ## Examples
    >>> from votepy.algorithms.base_algorithm import BaseAlgorithm
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

        algorithm_name = __get_algo_name(algorithm)

        implementations[rule_name][algorithm_name] = wrapper

        return wrapper
    return actual_decorator


def get_implementation(rule: Union[Callable, str], algorithm: BaseAlgorithm) -> Callable:
    """# Summary
    Returns `@impl` decorated function implementation for a given rule and algorithm

    ## Args:
        `rule` (Callable | str): Rule function or its identification name
        `algorithm` (BaseAlgorithm): Name identification of the algorithm, class deriving from `BaseAlgorithm` or already initialized algorithm

    ## Raises:
        `ValueError`: Rule is not registered
        `ValueError`: Algorithm is not adapted for the given rule

    ## Returns:
        -> Callable: Implementation of the given rule, using algorithm to find a committee

    ## Examples
    >>> from votepy.algorithms.base_algorithm import BaseAlgorithm
    >>>
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def _solve():
    ...         pass
    >>> @rule()
    ... def some_rule():
    ...     pass
    >>>
    >>> @impl(some_rule, Algo)
    ... def some_rule_algo(algorithm):
    ...     pass
    >>> get_implementation(some_rule, Algo) == some_rule_algo
    True
    >>> get_implementation("some_rule", Algo) == some_rule_algo
    True
    >>> get_implementation(some_rule, "name") == some_rule_algo
    True
    >>> get_implementation("some_rule", "name") == some_rule_algo
    True
    """
    rule_name = rule if isinstance(rule, str) else rule.__name__
    algorithm_name = __get_algo_name(algorithm)

    if rule_name not in implementations:
        raise ValueError(f"Rule {rule_name} has not been registered. Remember to register the main rule function with `@rule()` decorator.")

    rule_implementations = implementations[rule_name]

    if algorithm_name not in rule_implementations:
        raise ValueError(f"Algorithm {algorithm_name} has not been adapted to {rule_name}. Remember to register algorithm usage with `@impl()` decorator.")

    return rule_implementations[algorithm_name]


def get_default_algorithm(rule: Union[Callable, str]) -> Union[BaseAlgorithm, None]:
    """# Summary
    Returns default algorithm class for the given rule.

    Algorithm must be specified as a `default_algorithm` parameter in the `@rule` decorator and implemented (using `impl` decorator)

    ## Args:
        `rule` (Callable | str): Rule function or its identification name.

    ## Returns:
        -> BaseAlgorithm | None: Default algorithm or None if rule has no default algorithm

    ## Examples
    >>> from votepy.algorithms.base_algorithm import BaseAlgorithm
    >>>
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def _solve():
    ...         pass
    >>>
    >>> @rule(default_algorithm=Algo)
    ... def some_rule():
    ...     pass
    >>>
    >>> @impl(some_rule, Algo)
    ... def some_rule_algo(algorithm):
    ...     pass
    >>>
    >>> get_default_algorithm(some_rule) == Algo
    True
    """
    rule_name = rule if isinstance(rule, str) else rule.__name__
    if rule_name not in default_algorithms:
        return None
    return default_algorithms[rule_name]


def get_default_implementation(rule: Union[Callable, str]) -> Callable:
    """# Summary
    Returns implementation for the given rule using the default algorithm

    # Args:
        `rule` (Callable | str): Rule function or its identification name.

    # Returns:
        -> Callable: Implementation of the given rule, using default algorithm to find a committee

    # Examples
    >>> from votepy.algorithms.base_algorithm import BaseAlgorithm
    >>>
    >>> @algo(name='name')
    ... class Algo(BaseAlgorithm):
    ...     def _solve():
    ...         pass
    >>>
    >>> @rule(default_algorithm=Algo)
    ... def some_rule():
    ...     pass
    >>>
    >>> @impl(some_rule, Algo)
    ... def some_rule_algo(algorithm):
    ...     pass
    >>>
    >>> get_default_algorithm(some_rule) == Algo
    True
    >>> get_default_algorithm("some_rule") == Algo
    True
    """
    default_algorithm = get_default_algorithm(rule)
    return get_implementation(rule, default_algorithm)


def __get_algo_name(algorithm):
    if algorithm is None:
        return None
    elif isinstance(algorithm, str):
        return algorithm
    else:
        return algorithm.name
