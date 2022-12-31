from votepy.ordinal_election import OrdinalElection, OrdinalBallot
from typing import Union

from votepy.meta.structure import algo, BaseAlgorithm, rule, impl
from votepy.solve import solve


@impl('greedy_monroe', algorithm=None)
@rule()
def greedy_monroe(voting: Union[list[list[int]], OrdinalElection], size_of_committee: int) -> \
        list[int]:
    """# Summary
    Function computes a committee of given size using greedy monroe procedure.
    In this version for multiple results only arbitrary one is returned.

    ## Args:
        voting (`list[list[int]]` | `OrdinalElection`): voting for which the function calculates the committee
        size_of_committee (`int`): Size of the committee

    ## Returns:
        `list[int]`: List of chosen candidates

    ## Examples:
    >>> voting = [
    ...     [1, 0, 2, 3, 4],
    ...     [3, 2, 4, 1, 0],
    ...     [2, 4, 1, 3, 0]
    ... ]
    >>> size_of_committee = 2
    >>> greedy_monroe(voting, size_of_committee)
    [1, 2]
    """
    m_candidates = voting.ballot_size
    n_votes = len(voting)
    resultant_committee = []

    def map_votes(vs):
        mapping = {p: {} for p in range(n_votes)}
        for i in range(n_votes):
            for j in range(m_candidates):
                mapping[i][vs[i][j]] = m_candidates - j - 1
        return mapping

    mapping = map_votes(voting)
    kk = size_of_committee
    curr_candidates = set(range(m_candidates))

    n = n_votes

    def calculate_score(mapping, candidate):
        return [(j, mapping[j][candidate]) for j in range(n_votes) if mapping[j] is not None]

    for _ in range(size_of_committee):
        curr_size = n // kk
        best_score, best_candidate = -1, -1
        best_votes, best_candidate_voters = None, None
        for candidate in curr_candidates:
            scoring = calculate_score(mapping, candidate)
            votes, scores = zip(*(sorted(scoring, key=lambda x: -x[1])[:curr_size]))
            summed_score = sum(scores)
            if summed_score > best_score:
                best_score = summed_score
                best_candidate_voters = (candidate, votes)
        best_votes = best_candidate_voters[1]
        best_candidate = best_candidate_voters[0]

        resultant_committee.append(best_candidate)
        curr_candidates.remove(best_candidate)
        for k in best_votes:
            voting[k] = None
            mapping[k] = None

        n -= curr_size
        kk -= 1
    return resultant_committee


if __name__ == '__main__':
    print(greedy_monroe([
        [1, 0, 2, 3, 4],
        [3, 2, 4, 1, 0],
        [2, 4, 1, 3, 0]
    ], 2))
