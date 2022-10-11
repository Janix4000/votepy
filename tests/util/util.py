import json
from typing import Callable, Iterable, Iterator


Election = list[list[int]]
CommitteeSize = int
Score = float


def load_tests(filepath: str) -> Iterator[tuple[Election, CommitteeSize, Score]]:
    """# Summary
    Yields (election, committee_size, expected_score) test triples from the json file.

    ## Args:
        `filepath` (str): Filepath to the json file containing testing elections.

    ## Yields:
        -> Iterator[tuple[Election, CommitteeSize, Score]]: (election, committee_size, expected_score) triple
    """
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
    """Generates json file containing testing elections, described by (n_candidates, n_voters) pairs in `election`, generated using `generator` and solved with `solver`.

    # Args:
        `filepath` (str): File path of newly generated test file
        `elections` (Iterable[tuple[Candidates, Voters]]): Collections of (n_candidates, n_voters) pairs, describing elections for generator
        `generator` (Callable[[Candidates, Voters], Election]): Function generating elections based on (n_candidates, n_voters) arguments
        `solver` (Callable[[Election, CommitteeSize], Score]): Function returning the score of the committee, for the given election
    """
    all_tests = []
    for candidates_size, voters_size in elections:
        election = generator(candidates_size, voters_size)
        test = {"election": election, "scores": []}
        for committee_size in range(1, candidates_size):
            score = solver(election, committee_size)
            test["scores"].append([committee_size, score])
        all_tests.append(test)
    with open(filepath, "w") as file:
        json.dump({"tests": all_tests}, file)
