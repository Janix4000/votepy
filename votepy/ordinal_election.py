
from typing import Iterable


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
            return str([f"({candidate} -> {self.mapping[candidate]})" for candidate in self])
        return super().__str__()
    
        
            
        