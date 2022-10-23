from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from warnings import warn


class Solver(ABC):

    class Sense(Enum):
        MAX = 1
        MIN = 2

    @abstractmethod
    def addVariable(self, name: str, vartype: str, obj: Optional[float],
                    lb: Optional[float], ub: Optional[float]):
        """Adds a variable to the model

        Args:
            name (str): Name of the variable, used to reference the variable and for printing
            vartype (str): Type of the variable ('B' - Binary, 'C' - continuous, 'I' - Integer)
            obj (Optional[float]): Coefficient at the variable in the objective function, default is 0.
            lb (Optional[float]): Lower bound of the variable, defaults are dictated by the solver.
            ub (Optional[float]): Upper bound of the variable, defaults are dictated by the solver.
        Returns:
            vartype: An object representing the variable in the selected solver.
            It has to be used in the 'variables' arg in the addConstraint method
        """
        pass

    @abstractmethod
    def addConstraint(self, name: str, variables: list[object], coeffs: list[float], rhs: float, sense: str):
        """Add a constraint to the model.

        In general, the constraints have to be in the form of:
        <linear combination of variables> < 'L'|'G'|'E' > <independent part of the expression>
        , where 'L'|'G'|'E' are 'less than or equal' | 'greater than or equal' | 'equal' respectively.

        For example:

        2*x1 + 3*x2 >= 8

        would be created by:

        model.addConstraint('example', [x1, x2], [2, 3], 8, 'G')

        Args:
            name (str): Name of the constraint, useful when printing the model.
            variables (list[object]): List of the variables present in the left-hand side of the constraint.
            coeffs (list[float]): Coefficients at the variables, must of the same length and in the same order as <variables>.
            rhs (float): The independent part of the expression
            sense (str): Relation between lhs and rhs, can be one of 'L'|'G'|'E'
        """
        pass

    @abstractmethod
    def solve(self):
        """Solves the model
        """
        pass

    @abstractmethod
    def getValues(self):
        """Get values of all the model variables, in the same order they were added to the model.
        """
        pass


class CPLEX(Solver):

    def __init__(self,
                 sense: Solver.Sense = Solver.Sense.MAX,
                 log: bool = False) -> None:
        super().__init__()
        try:
            import cplex
        except ImportError as err:
            raise ImportError(
                "Failed to import CPLEX, please make sure that you have CPLEX installed"
            )

        self.col_names = []
        self.obj = []
        self.lb = []
        self.ub = []
        self.ctypes = []

        self.rhs = []
        self.row_names = []
        self.senses = []
        self.rows = []

        self.cplex = cplex
        self.model = cplex.Cplex()
        if not log:
            self.model.set_log_stream(None)
            self.model.set_results_stream(None)

        if sense == Solver.Sense.MAX:
            self.model.objective.set_sense(self.model.objective.sense.maximize)
        elif sense == Solver.Sense.MIN:
            self.model.objective.set_sense(self.model.objective.sense.minimize)

    def addVariable(self,
                    name: str,
                    vartype: str,
                    obj: float = 0.0,
                    lb: Optional[float] = None,
                    ub: Optional[float] = None):
        self.colnames.append(name)
        self.obj.append(obj)
        if lb is not None:
            self.lb.append(lb)
        if ub is not None:
            self.ub.append(ub)
        self.ctypes.append(vartype)
        return name

    def addConstraint(self, name: str, variables: list[object], coeffs: list[float], rhs: float, sense: str):
        self.row_names.append(name)
        self.rows.append([variables, coeffs])
        self.rhs.append(rhs)
        self.senses.append(sense)

    def solve(self):
        if len(self.lb) != len(self.ctypes) or len(self.ub) != len(
                self.ctypes):
            if len(self.lb) > 0 or len(self.ub) > 0:
                warn("Warning: You've given bounds for some variables but not for all - please make sure you either set bounds for every variable or for none.\nUsing default bounds...")
            self.model.variables.add(obj=self.obj, types=''.join(
                self.ctypes), names=self.col_names)
        else:
            self.model.variables.add(obj=self.obj,
                                     lb=self.lb,
                                     ub=self.ub,
                                     types=''.join(self.ctypes),
                                     names=self.colnames)
        print(self.rows)
        self.model.linear_constraints.add(lin_expr=self.rows,
                                          senses=''.join(self.senses),
                                          rhs=self.rhs,
                                          names=self.rownames)
        self.model.solve()

    def getValues(self):
        return self.model.solution.get_values()


class Gurobi(Solver):

    def __init__(self,
                 sense: Solver.Sense = Solver.Sense.MAX,
                 log: bool = False) -> None:
        super().__init__()
        try:
            import gurobipy as gp
            self.gp = gp
            from gurobipy import GRB
        except ImportError as _err:
            raise ImportError(
                "Failed to import Gurobi, please make sure that you have Gurobi installed"
            )

        # TODO
        # forcefully disabling Gurobi logs for now, can be replaced by config file later
        env = gp.Env(empty=True)
        if not log:
            env.setParam('OutputFlag', 0)
        env.start()

        self.model = gp.Model(env=env)
        self.var_type_map = {
            'C': GRB.CONTINUOUS,
            'B': GRB.BINARY,
            'I': GRB.INTEGER
        }

        self.objective = []
        if sense == Solver.Sense.MAX:
            self.sense = GRB.MAXIMIZE
        elif sense == Solver.Sense.MIN:
            self.sense = GRB.MINIMIZE

    def addVariable(self, name: str, var_type: str, obj: Optional[float] = None, lb: Optional[float] = None, ub: Optional[float] = None):
        var = self.model.addVar(vtype=self.var_type_map[var_type], name=name)
        if lb is not None:
            self.model.addConstr(var >= lb, name + '_lb')
        if ub is not None:
            self.model.addConstr(var <= ub, name + '_ub')
        if obj != None:
            self.objective.append(obj * var)
        return var

    def addConstraint(self, name: str, variables: list[object],
                      coeffs: list[float], rhs: float, sense: str):
        expr = sum([v * c for v, c in zip(variables, coeffs)])
        if sense == 'L':
            self.model.addConstr(expr <= rhs, name)
        elif sense == 'G':
            self.model.addConstr(expr >= rhs, name)
        elif sense == 'E':
            self.model.addConstr(expr == rhs, name)

    def _setObjective(self):
        self.model.setObjective(sum(self.objective), self.sense)

    def solve(self):
        self._setObjective()
        self.model.optimize()

    def getValues(self):
        return [v.X for v in self.model.getVars()]

    def _debug(self, filename='model_dump.lp'):
        self._setObjective()
        try:
           self.model.computeIIS()
           print("Computed Irreducible Inconsistent Subsystem:")
           for i, c in zip(self.model.IISConstr, self.model.getConstrs()):
                if i == 1:
                    print(c)
        except self.gp.GurobiError:
            print("The model is feasible!")
        self.model.write(filename)
