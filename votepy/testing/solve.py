from typing import Callable, Union
from votepy.ordinal_election import OrdinalElection
from votepy.testing.algorithms.base_algorithm import BaseAlgorithm
from votepy.testing.structure.structure import get_algorithm, get_implementation


def solve(rule: Union[Callable, str], voting: Union[OrdinalElection, list[int]], size_of_committee: int, *rule_args, algorithm: BaseAlgorithm, **rule_kwargs) -> list[int]:
    """# Summary
    Calculates committee of the given size, based on the voting rule, using algorithm. 

    ## Args:
        `rule` (Callable | str): Voting rule function or its identification name
        `voting` (Union[OrdinalElection, list[int]]): Voting for which the function calculates the committee
        `size_of_committee` (int): Size of the committee
        `algorithm` (BaseAlgorithm): Voting solving algorithm or its identification name.
        `*rule_args`: Additional voting functions' arguments
        `*rule_kwargs`: Additional voting functions' positional arguments

    ## Returns:
        -> list[int]: List of chosen candidates

    ## Examples

    """
    implementation = get_implementation(rule, algorithm)
    algorithm = get_algorithm(algorithm)
    return list(implementation(voting, size_of_committee, *rule_args, algorithm=algorithm, **rule_kwargs))
