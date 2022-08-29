import json
from typing import Callable, Iterable


def assert_approximation(committee: list, scoring_function, expected_score: float, alpha: float) -> None:
    score = scoring_function(committee)
    to_expected_prop = score / expected_score
    assert to_expected_prop >= alpha


Election = list[list[int]]
CommitteeSize = int
Score = float


def load_tests(filepath: str) -> Iterable[tuple[Election, CommitteeSize, Score]]:
    with open(filepath, 'r') as file:
        tests = json.load(file)["tests"]
    for election in tests:
        scores = election["scores"]
        election = election["election"]
        for committee_size, score in scores:
            yield election, committee_size, score


Candidates = int
Voters = int


def generate_tests(
    filepath: str,
    elections: Iterable[tuple[Candidates, Voters]],
    generator: Callable[[Candidates, Voters], Election],
    solver: Callable[[Election, CommitteeSize], Score]
) -> None:
    all_tests = []
    for candidates_size, voters_size in elections:
        election = generator(candidates_size, voters_size)
        test = {}
        test["election"] = election
        test["scores"] = []
        for committee_size in range(1, candidates_size):
            score = solver(election, committee_size)
            test["scores"].append([committee_size, score])
        all_tests.append(test)
    with open(filepath, "w") as file:
        json.dump({"tests": all_tests}, file)
