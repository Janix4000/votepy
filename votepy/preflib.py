from votepy.ordinal_election import OrdinalElection


def load(source: str) -> OrdinalElection:
    """# Summary
    Loads voting from file in the preflib format.

    ## Args:
        `source` (str): Path to the file with voting

    ## Returns:
        ->OrdinalElection: Election

    ## Examples
    >>> load('votepy/tests/preflib/data/voting_no_dups.txt')
    [[0, 1, 2, 3], [3, 2, 1, 0], [2, 1, 3, 0]]
    """
    raise NotImplementedError()
