from typing import Iterable, Sequence


class OrdinalBallot(list):
    def __init__(self, ordering: Iterable, mapping=None):
        super().__init__(ordering)
        
        self.mapping = mapping
        
        for candidate in ordering:
            if not isinstance(candidate, (int,)):
                raise TypeError(f"Only integer candidates are allowed, object of type {str(type(candidate))} is not supported")
            if candidate < 0:
                raise ValueError(f"Only non-negative integers are valid candidates, value {candidate} was supplied")
            
    def __str__(self) -> str:
        if self.mapping is not None:
            return str([self.mapping[candidate] for candidate in self])
        return str([self])
    
    
class OrdinalElection(list):
    def __init__(self, preference_orders: list, mapping=None):
        super().__init__()
        
        self.mapping = mapping
        self.candidates = set() if len(preference_orders) == 0 else set(preference_orders[0])
        
        for preference in preference_orders:
            if len(self.candidates) != len(preference):
                raise ValueError(f"Preference orders are of different lengths")
            for candidate in preference:
                if candidate not in self.candidates:
                    raise ValueError(f"Candidate sets in preference orders differ: candidate {candidate} is not present in every preference order")
            self.append(OrdinalBallot(preference, mapping))
        self.ballot_size = len(preference_orders[0])
        self.number_of_votes = len(preference_orders)
            
    def update_mapping(self, mapping: Sequence) -> None:
        self.mapping = mapping
        
    def __str__(self) -> str:
        return "\n".join(map(lambda x: str(x), self))
        
        
if __name__ == '__main__':
    #note: temporary test
    print(OrdinalElection([
        [0,1,2,3],
        [3,2,1,0],
        [2,1,3,0]
    ]))
    print("With mapping")
    print(OrdinalElection([
        [3,2,1,0]
    ], {0:"siedem", 1:"trzy", 2:"jeden", 3:"dwa"}))
        
            
        