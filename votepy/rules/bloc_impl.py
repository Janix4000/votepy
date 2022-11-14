from votepy.ordinal_election import OrdinalElection
from votepy.meta.structure import rule, impl

from typing import Union


@impl('bloc', algorithm=None)
@rule()
def bloc(voting: Union[list[list[int]], OrdinalElection], size_of_committee: int) -> list[int]:
    """# Summary
    Function computes a committee of given size using Bloc rule for specified number of favorite candidates.

    ## Args:
        `voting` (`list[list[int]]` | `OrdinalElection`): Voting for which the function calculates the committee
        `size_of_committee` (`int`): Size of the committee

    ## Returns:
        `list[int]`: List of chosen candidates

    ## Examples
    >>> import votepy as vp
    >>> election = [
    ...     [0,1,2,3,4],
    ...     [4,0,1,3,2],
    ...     [3,0,1,2,4],
    ...     [2,1,3,4,0],
    ...     [2,1,4,0,3],
    ...     [1,2,3,4,0]
    ... ]
    >>> bloc(election, 2)
    [1, 0]
    >>> vp.solve('bloc', election, 2)
    [1, 0]
    """

    n = voting.ballot_size
    results = [0] * n

    for vote in voting:
        for candidate in vote[:size_of_committee]:
            results[candidate] += 1
    committee, _ = zip(
        *sorted(enumerate(results), reverse=True, key=lambda t: t[1]))
    return committee[:size_of_committee]


if __name__ == '__main__':
    election = OrdinalElection([
        [0, 1, 2, 3, 4],
        [4, 0, 1, 3, 2],
        [3, 0, 1, 2, 4],
        [2, 1, 3, 4, 0],
        [2, 1, 4, 0, 3],
        [1, 2, 3, 4, 0]
    ], {
        0: 'a',
        1: 'b',
        2: 'c',
        3: 'd',
        4: 'e'
    })
    print(election)
    print(
        bloc(
            election,
            2
        )
    )
