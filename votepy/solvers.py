from ordinal_election import OrdinalElection
from typing import Union, Iterable

def solve(voting: Union[OrdinalElection, Iterable[int]], 
    rule: str, 
    strategy: str, 
    **rule_kwargs) -> list[int]: 
    return None