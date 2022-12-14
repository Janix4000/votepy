from votepy.ordinal_election import OrdinalElection

__meta_tokens = {
    'FILE NAME',
    'TITLE',
    'DESCRIPTION',
    'DATA TYPE',
    'MODIFICATION TYPE',
    'RELATES TO',
    'RELATED FILES',
    'PUBLICATION DATE',
    'MODIFICATION DATE',
    'NUMBER ALTERNATIVES',

    'NUMBER VOTERS',
    'NUMBER UNIQUE ORDERS',
}


def load(source: str) -> OrdinalElection:
    """# Summary
    Loads election from file in the preflib format.

    ## Args:
        `source` (str): Path to the file with voting

    ## Returns:
        ->OrdinalElection: Election

    ## Examples
    >>> load('tests/fixtures/preflib/voting_no_dups.txt')
    [[0, 1, 2, 3], [3, 2, 1, 0], [2, 1, 3, 0]]
    """
    with open(source, 'r') as f:
        lines = f.readlines()
        mapping = {}

        election = []

        for line in lines:
            if line.isspace():
                continue

            if line.startswith('# '):
                token, value = line[2:].split(': ')
                if token.startswith('ALTERNATIVE NAME'):
                    _, _, alternative_id = token.split()
                    mapping[int(alternative_id) - 1] = value.strip()
            else:
                n_voters, ballot = line.split(': ')
                n_voters = int(n_voters)
                ballot = ballot.replace('{', '').replace('}', '').strip().split(',')
                ballot = list(map(lambda x: int(x) - 1, ballot))
                election.extend([ballot] * n_voters)

        if not mapping:
            mapping = None

        return OrdinalElection(election, mapping=mapping)
