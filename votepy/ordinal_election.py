from collections.abc import Iterable, Sequence


class OrdinalBallot(list):
    def __init__(self, ordering: Iterable[int], mapping: Sequence=None):
        super().__init__(ordering)
        
        self.mapping = mapping
        
        length = len(self)
        
        for candidate in self:
            if not isinstance(candidate, (int,)):
                raise TypeError(f"Candidates have to be of integer type, objects of type {str(type(candidate))} are not supported")
            if candidate < 0 or candidate >= length:
                raise ValueError(f"The candidates must be from the range [0, <ordering_length>-1]. Found {candidate}")
        
        if length != len(set(self)):
            raise ValueError(f"All candidates inside the ordering must be unique integers")
            
    def __str__(self) -> str:
        if self.mapping is not None:
            return str([self.mapping[candidate] for candidate in self])
        return str([self])
    
    
class OrdinalElection(list):
    def __init__(self, preference_orders: Iterable[Iterable[int]], mapping: Sequence=None):
        super().__init__()
        
        self.mapping = mapping
        preference_orders = list(preference_orders)
        self.candidates = set() if preference_orders else set(preference_orders[0])
        
        for preference in preference_orders:
            preference = list(preference)
            if len(self.candidates) != len(preference):
                raise ValueError(f"Preference orders must be of the same lengths")
            self.append(OrdinalBallot(preference, mapping))
        self.ballot_size = len(preference_orders[0])
        self.number_of_voters = len(preference_orders)
            
    def update_mapping(self, mapping: Sequence) -> None:
        self.mapping = mapping
        
    def __str__(self) -> str:
        return "\n".join(map(str, self))
        
        
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
        
            
        