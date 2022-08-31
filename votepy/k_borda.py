from ordinal_election import OrdinalElection, OrdinalBallot
from typing import Union


def k_borda(voting: Union[OrdinalElection, list[int]], size_of_committee: int, number_of_scored_candidates: int, m: int = None) -> list[int]:
    """Function computes a committee of given size using k-borda rule for specified number of scored candidates.
    In this version for multiple results only arbitrary one is returned.

    Args:
        voting (OrdinalElection): voting for which the function calculates the committee
        size_of_committee (int): Size of the committee
        number_of_scored_candidates (int): Number of scored candidates using k-borda rule
        m (int): m parameter used by β Borda scoring function. By default equals to `number_of_scored_candidates`

    Raises:
        ValueError: Size of committee is a positive number which do not exceeds number of all candidates
        ValueError: Number of candidates scored in k-borda is a positive number which do not exceeds number of all candidates. 

    Returns:
        OrdinalBallot: List of chosen candidates wrapped in ordinalBallot
    """

    if not isinstance(voting, OrdinalElection):
        voting = OrdinalElection(voting)

    n = voting.ballot_size
    if size_of_committee > n or size_of_committee <= 0:
        raise ValueError(
            f"Size of committee needs to be from the range 1 to the number of all candidates.")
    if number_of_scored_candidates > n or number_of_scored_candidates <= 0:
        raise ValueError(
            f"Number of candidates scored in k-borda needs to be from range 1 to the number of all candidates.")

    candidates_scores = [0] * n

    m = m if m is not None else number_of_scored_candidates

    for vote in voting:
        for i, candidate in enumerate(vote[:number_of_scored_candidates]):
            candidates_scores[candidate] += m - i
    committee, _ = zip(
        *sorted(enumerate(candidates_scores), reverse=True, key=lambda t: t[1]))
    return list(committee[:size_of_committee])


if __name__ == '__main__':
    print(k_borda([
        [0, 1, 2, 3],
        [3, 2, 1, 0],
        [2, 1, 3, 0]
    ], 3, 3))