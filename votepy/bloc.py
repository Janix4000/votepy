from ordinal_election import OrdinalElection
from typing import Union

def bloc(voting: Union[OrdinalElection, list[int]], size_of_committee: int) -> list[int]:
    """Function computes a committee of given size using Bloc rule for specified number of favorite candidates.

    Args:
        voting (OrdinalElection | list): voting for which the function calculates the committee
        size_of_committee (int): Size of the committee

    Raises:
        ValueError: Size of commite is a positive number which do not exceeds number of all candidates
        ValueError: Number of candidates scored in Bloc is a positive number which do not exceeds number of all candidates

    Returns:
        list: List of chosen candidates
    """
    
    if not isinstance(voting, OrdinalElection): 
        voting=OrdinalElection(voting)
    
    n = voting.ballot_size
    results = [0] * n
    if size_of_committee > n or size_of_committee <= 0:
        raise ValueError(f"Size of committee needs to be from the range 1 to the number of all candidates.")
    for vote in voting:
        for candidate in vote[:size_of_committee]:
            results[candidate] += 1
    committee, _ = zip(*sorted(enumerate(results), reverse=True, key=lambda t: t[1]))
    return committee[:size_of_committee]


if __name__ == '__main__':
    election = OrdinalElection([
                [0,1,2,3,4],
                [4,0,1,3,2],
                [3,0,1,2,4],
                [2,1,3,4,0],
                [2,1,4,0,3],
                [1,2,3,4,0]
            ], {
                0:'a',
                1:'b',
                2:'c',
                3:'d',
                4:'e'
            })
    print(election)
    print(
        bloc(
            election,
            2
        )
    )