# my_bloc.py
from votepy.meta.structure import rule, impl


@impl('my_bloc', algorithm=None)
@rule()
def my_bloc(voting: list[list[int]], committee_size: int) -> list[int]:
    n = len(voting[0])

    candidates_scores = [0] * n
    for vote in voting:
        for candidate in vote[:committee_size]:
            candidates_scores[candidate] += 1

    sorted_indices_by_score, _sorted_scores = zip(
        *sorted(enumerate(candidates_scores), reverse=True, key=lambda idx_score: idx_score[1]))

    committee = sorted_indices_by_score[:committee_size]
    return committee
