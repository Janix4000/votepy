from votepy.ordinal_election import OrdinalElection, OrdinalBallot

from typing import Union
import numpy as np


def sntv(voting: Union[OrdinalElection, list[int]], size_of_committee: int) -> list[int]:
    """Function computes a committee of given size using SNTV rule for specified number of scored candidates.
    In this version for multiple results only arbitrary one is returned.

    Args:
        voting (OrdinalElection): voting for which the function calculates the committee
        size_of_committee (int): Size of the committee

    Raises:
        ValueError: Size of commite is a positive number which do not exceeds number of all candidates
        ValueError: Number of candidates scored in SNTV is a positive number which do not exceeds number of all candidates

    Returns:
        list[int]: List of chosen candidates
    """

    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)

    n = voting.ballot_size
    if size_of_committee > n or size_of_committee <= 0:
        raise ValueError(
            f"Size of committee needs to be from the range 1 to the number of all candidates.")

    results = np.zeros(n)
    for vote in voting:
        results[vote[0]] += 1
    committee, _ = zip(
        *sorted(enumerate(results), reverse=True, key=lambda t: t[1]))
    return committee[:size_of_committee]


if __name__ == '__main__':
    print(sntv([
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0],
        [2, 1, 3, 0],
    ], 2))
