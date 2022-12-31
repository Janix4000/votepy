from votepy.ordinal_election import OrdinalElection
from votepy.meta.structure import rule, impl

from typing import Union
import numpy as np


@impl('sntv', algorithm=None)
@rule()
def sntv(voting: Union[list[list[int]], OrdinalElection], size_of_committee: int) -> list[int]:
    """# Summary
    Function computes a committee of given size using SNTV rule for specified number of scored candidates.
    In this version for multiple results only arbitrary one is returned.

    ## Args:
        voting (`list[list[int]]` | `OrdinalElection`): voting for which the function calculates the committee
        size_of_committee (`int`): Size of the committee

    Returns:
        `list[int]`: List of chosen candidates

    ## Examples
        >>> import votepy as vp
        >>> voting = [
        ...     [0, 1, 2, 3],
        ...     [3, 2, 1, 0],
        ...     [2, 1, 3, 0],
        ...     [2, 1, 3, 0],
        ... ]
        >>> sntv(voting, 2)
        [2, 0]
        >>> vp.solve('sntv', voting, 2)
        [2, 0]
    """
    n = voting.ballot_size
    results = np.zeros(n)
    for vote in voting:
        results[vote[0]] += 1
    committee, _ = zip(
        *sorted(enumerate(results), reverse=True, key=lambda t: t[1]))
    return committee[:size_of_committee]


if __name__ == '__main__':
    import votepy as vp
    voting = [
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0],
        [2, 1, 3, 0],
    ]
    print(sntv(voting, 2))
    print(vp.solve(sntv, voting, 2))
