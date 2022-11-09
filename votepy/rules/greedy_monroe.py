from votepy.ordinal_election import OrdinalElection, OrdinalBallot
from typing import Union

from votepy.meta.structure import algo, BaseAlgorithm, rule, impl
from votepy.solve import solve


@algo(name='greedy_monroe')
class GreedyMonroe(BaseAlgorithm):
    def _solve(self, voting: Union[OrdinalElection, list[int]], size_of_committee: int) -> list[int]:
        m_candidates = voting.ballot_size
        n_votes = len(voting)
        if size_of_committee > m_candidates or size_of_committee <= 0:
            raise ValueError(f"Size of committee needs to be from the range 1 to the number of all candidates.")
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

        for i in range(size_of_committee):
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


@rule(default_algorithm=GreedyMonroe)
def greedy_monroe(voting: Union[OrdinalElection, list[int]], size_of_committee: int, algorithm: GreedyMonroe = GreedyMonroe()) -> \
        list[int]:
    """Function computes a committee of given size using greedy monroe procedure.
    In this version for multiple results only arbitrary one is returned.

    Args:
        voting (OrdinalElection): voting for which the function calculates the committee
        size_of_committee (int): Size of the committee

    Raises:
        ValueError: Size of committee is a positive number which does not exceed number of all candidates
        ValueError: Number of candidates scored in k-borda is a positive number which does not exceed number of all candidates

    Returns:
        OrdinalBallot: List of chosen candidates wrapped in ordinalBallot

    Examples:
    >>> voting = [
    ...     [1, 0, 2, 3, 4],
    ...     [3, 2, 4, 1, 0],
    ...     [2, 4, 1, 3, 0]
    ... ]
    >>> size_of_committee = 2
    >>> greedy_monroe(voting, size_of_committee)
    [1, 2]
    """
    return solve(greedy_monroe, voting, size_of_committee, algorithm=algorithm)


@impl(greedy_monroe, GreedyMonroe)
def greedy_monroe_impl(voting, size_of_committee, algorithm: GreedyMonroe):
    algorithm.prepare()
    return algorithm.solve(voting, size_of_committee)


if __name__ == '__main__':
    print(greedy_monroe([
        [1, 0, 2, 3, 4],
        [3, 2, 4, 1, 0],
        [2, 4, 1, 3, 0]
    ], 2))
