from votepy.ordinal_election import OrdinalElection
from votepy.algorithms.base_algorithm import BaseAlgorithm
from votepy.structure.structure import algo
from votepy.generic_ilp import CPLEX, Gurobi


@algo(name='ilp')
class ILP(BaseAlgorithm):

    def __init__(self, solver=Gurobi):
        """Base class for ILP algorithms"""
        super().__init__()
        self.solver = solver

    def prepare(self, define_model):
        self.define_model = define_model
        super().prepare()

    def __get_committee(self, model, ballot_size):
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
