from typing import Union, final
from votepy.ordinal_election import OrdinalElection

from abc import abstractmethod, ABC


class BaseAlgorithm(ABC):
    name = None

    def __init__(self) -> None:
        self.__prepared = False

    def prepare(self) -> None:
        self.__prepared = True

    @abstractmethod
    def _solve(self, voting: OrdinalElection, size_of_committee: int) -> list[int]:
        pass

    def solve(self, voting: Union[list[list[int]], OrdinalElection], size_of_committee: int) -> list[int]:
        """# Summary
        Solves a voting using the specified algorithm, which must be fully prepared for the election rule.

        ### Args:
            `voting` (`list[list[int]], OrdinalElection`): Voting for which the algorithm calculates the committee
            `size_of_committee` (`int`): Size of the committee

        ### Raises:
            ValueError: Size of committee needs to be from the range 1 to the number of all candidates.

        ### Returns:
            `list[int]`: The winning committee
        """
        if not self.__prepared:
            raise ValueError(
                f'Algorithm must be initialized with `prepare(self, ...)` method before usage.')

        return self._solve(voting, size_of_committee)
