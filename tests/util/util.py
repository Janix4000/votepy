def assert_approximation(committee: list, scoring_function, expected_score: float, alpha: float) -> None:
    score = scoring_function(committee)
    to_expected_prop = score / expected_score
    assert to_expected_prop >= alpha