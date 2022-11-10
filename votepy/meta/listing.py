from typing import Callable, Type, Union
import votepy.meta.structure as structure
from votepy.algorithms.base_algorithm import BaseAlgorithm


def get_algorithms(rule: Union[str, Callable] = None) -> dict[str, Type[BaseAlgorithm]]:
    """# Summary
    Returns a dict name->algorithm_class with all of the implemented voting solvers or only implemented for the given rule.
    ## Args:
        `rule` (Union[str, Callable], optional): If given, returns algorithms implemented for the given rule. Defaults to `None`.

    ## Returns:
        -> dict[str, Type[BaseAlgorithm]]: name->algorithm_class

    ## Examples
    >>> import votepy
    >>> "greedy" in votepy.get_algorithms()
    True
    >>> "greedy" in votepy.get_algorithms("chamberlin_courant")
    True
    >>> "greedy" in votepy.get_algorithms("k_borda")
    False
    """
    if rule is not None:
        if not isinstance(rule, str):
            rule = rule.__name__
        rule_implementations = structure.implementations[rule]
        algorithms = {name: structure.algorithms[name] for name in rule_implementations}
    else:
        algorithms = structure.algorithms

    return algorithms


def get_rules() -> dict[str, Callable]:
    """# Summary
    Returns a dict name->voting_rule with all of the implemented voting rules.

    ## Returns:
        -> dict[str, Callable]: name->voting_rule

    ## Examples
    >>> import votepy
    >>> "k_borda" in votepy.get_rules()
    True
    """
    return structure.rules
