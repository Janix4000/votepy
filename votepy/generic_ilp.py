from abc import ABC,abstractmethod
from enum import Enum
from typing import Optional

class Solver(ABC):
    class Sense(Enum):
        MAX = 1
        MIN = 2
    @abstractmethod
    def addVariable(self, name: str, obj: float, lb: float, ub: float, vartype: str):
        pass

    @abstractmethod
    def addConstraint(self, name: str, variables: list[object], coeffs: list[float], rhs: float, sense: str):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def getValues(self):
        pass


class CPLEX(Solver):
    def __init__(self, sense: Solver.Sense = Solver.Sense.MAX) -> None:
        super().__init__()
        try:
            import cplex
        except ImportError as err:
            print("[Error]: Failed to import {}".format(err.args[0]))
            exit(1)

        self.colnames = []
        self.obj = []
        self.lb = []
        self.ub = []
        self.ctypes = []

        self.rhs = []
        self.rownames = []
        self.senses = []
        self.rows = []

        self.model = cplex.Cplex()
        if sense == Solver.Sense.MAX:
            self.model.objective.set_sense(self.model.objective.sense.maximize)
        elif sense == Solver.Sense.MIN:
            self.model.objective.set_sense(self.model.objective.sense.minimize)


    def addVariable(self, name: str, obj: float, lb: float, ub: float, vartype: str):
        self.colnames.append(name)
        self.obj.append(obj)
        self.lb.append(lb)
        self.ub.append(ub)
        self.ctypes.append(vartype)
        return name

    def addConstraint(self, name: str, variables: list[object], coeffs: list[float], rhs: float, sense: str):
        self.rownames.append(name)
        self.rows.append([variables, coeffs])
        self.rhs.append(rhs)
        self.senses.append(sense)

    def solve(self):
        self.model.variables.add(obj=self.obj, lb=self.lb, ub=self.ub, types=''.join(self.ctypes), names=self.colnames)
        self.model.linear_constraints.add(lin_expr=self.rows, senses=''.join(self.senses), rhs=self.rhs, names=self.rownames)
        self.model.solve()

    def getValues(self):
        return self.model.solution.get_values()


class Gurobi(Solver):
    def __init__(self, sense: Solver.Sense = Solver.Sense.MAX) -> None:
        super().__init__()
        try:
            import gurobipy as gp
            from gurobipy import GRB
        except ImportError as err:
            print("[Error]: Failed to import {}".format(err.args[0]))
            exit(1)

        self.model = gp.Model()
        self.vartypemap = {
            'C': GRB.CONTINUOUS,
            'B': GRB.BINARY,
            'I': GRB.INTEGER
        }

        self.objective = []

    def addVariable(self, name: str, vartype: str, obj: Optional[float] = None, lb: Optional[float] = None, ub: Optional[float] = None):
        var = self.model.addVar(vtype=self.vartypemap[vartype], name=name)
        if lb is not None:
            self.model.addConstr(var >= lb, name+'_lb')
        if ub is not None:
            self.model.addConstr(var <= ub, name+'_ub')
        if obj != None:
            self.objective.append(obj*var)
        return var

    def addConstraint(self, name: str, variables: list[object], coeffs: list[float], rhs: float, sense: str):
        expr = sum([v*c for v,c in zip(variables, coeffs)])
        if sense == 'L':
            self.model.addConstr(expr <= rhs, name)
        elif sense == 'G':
            self.model.addConstr(expr >= rhs, name)
        elif sense == 'E':
            self.model.addConstr(expr == rhs, name)

    def solve(self):
        self.model.optimize()

    def getValues(self):
        return [v.X for v in self.model.getVars()]
