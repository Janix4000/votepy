from typing import Callable, Iterable, Union
from votepy.ordinal_election import OrdinalElection
from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.meta.structure import get_algorithm, get_default_algorithm, get_implementation, has_default_implementation


def solve(rule: Union[Callable, str], voting: Union[list[list[int]], OrdinalElection], size_of_committee: int, *rule_args, algorithm: BaseAlgorithm = None, **rule_kwargs) -> list[int]:
    """# Summary
    Calculates committee of the given size, based on the voting rule, using algorithm.

    ## Args:
        `rule` (Callable | str): Voting rule function or its identification name
        `voting` (Union[list[list[int]], OrdinalElection]): Voting for which the function calculates the committee
        `size_of_committee` (`int`): Size of the committee
        `algorithm` (BaseAlgorithm): Voting solving algorithm or its identification name.
        `*rule_args`: Additional voting functions' arguments
        `*rule_kwargs`: Additional voting functions' positional arguments

    ## Returns:
        -> list[int]: List of chosen candidates

    ## Examples
    >>> solve('k_borda', [
    ...     [0, 1, 2, 3],
    ...     [3, 2, 1, 0],
    ...     [2, 1, 3, 0]
    ... ], 2)
    [2, 1]
    """
    if algorithm is None:
        if not has_default_implementation(rule):
            raise ValueError(
                f"{rule} has no default implementation. If rule does not need any algorithm, its rule function should be additionally decorated with `@impl(rule='name', algorithm=None)`. See `@impl` docs.")
        algorithm = get_default_algorithm(rule)

    implementation = get_implementation(rule, algorithm)
    algorithm = get_algorithm(algorithm)

    if algorithm is None:
        result = implementation(voting, size_of_committee, *rule_args, **rule_kwargs)
    else:
        result = implementation(voting, size_of_committee, *rule_args, algorithm=algorithm, **rule_kwargs)

    if isinstance(result, Iterable):
        return list(result)
    else:
        return result


if __name__ == '__main__':
    from votepy.rules.k_borda_rule import k_borda
    solve(k_borda, [
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ], 2, 3)
