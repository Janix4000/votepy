from typing import Callable, Type, Union
from votepy.ordinal_election import OrdinalElection
from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.structure.structure import algo
from votepy.generic_ilp import Gurobi, solver_t, model_t


@algo(name='ilp')
class ILP(BaseAlgorithm):

    def __init__(self, solver: solver_t = Gurobi):
        """Base class for ILP algorithms"""
        super().__init__()
        self.solver = solver

    committee_size_t = int
    def prepare(self, define_model: Callable[
        [OrdinalElection, committee_size_t, solver_t],
            model_t]) -> None:
        self.define_model = define_model
        super().prepare()

    def __get_committee(self, model: model_t, ballot_size: int) -> list[int]:
        """Retrieves the winning committee from the ILP solution. It is assumed
        that the variables representing whether a candidate has been chosen,
        are always the first <ballot_size> binary model variables.
        """
        return [
            i for i, v in enumerate(model.getValues()[:ballot_size]) if v == 1
        ]

    def _solve(self, voting: OrdinalElection,
               size_of_committee: int) -> list[int]:
        model = self.define_model(voting, size_of_committee, self.solver)
        model.solve()
        return self.__get_committee(model, voting.ballot_size)
