from variable import Variable
from abc import ABC, abstractmethod
from functools import cmp_to_key

type VarId = int
type Val = int


def Degree_MRV(
    unassigned: set[int],
    variables: list[Variable],
) -> Variable:
    def fn(a: int, b: int) -> int:
        va = variables[a]
        vb = variables[b]

        if len(va.affected_constraints) < len(vb.affected_constraints):
            return 1
        if va.domain.len() < vb.domain.len():
            return -1
        return 0

    sorted_ = sorted(unassigned, key=cmp_to_key(fn))
    first_vid = sorted_[0]
    return variables[first_vid]


def no_sorter(s):
    return list(s)


class Solver(ABC):
    def __init__(
        self,
    ):
        self.variables = []
        self.constraints = []
        self.solutions = []

    def print(self):
        print("Solver:")
        for var in self.variables:
            print(f"\t{var.name} ({var.vid}): {list(var.domain.values())}")
        for c in self.constraints:
            print(f"\t{c.cid}: {c}")

    def add_variable(self, variable):
        variable.vid = len(self.variables)  # Assign an ID to the variable
        self.variables.append(variable)

    def add_variables(self, variables):
        for v in variables:
            self.add_variable(v)

    def add_constraint(self, constraint):
        constraint.cid = len(self.constraints)
        self.constraints.append(constraint)

        # Initialize affected constraints for each variable
        for v in self.variables:
            if v.vid in constraint.affected_variables():
                v.affected_constraints.add(constraint.cid)

    def add_constraints(self, constraints):
        for c in constraints:
            self.add_constraint(c)

    @abstractmethod
    def solve(self, all: bool = False):
        pass


class BTSolver(Solver):
    def __init__(self):
        super().__init__()
        self.next_variable_picker = Degree_MRV
        self.values_orderer = no_sorter
        self.find_all = False  # find all solutions or just one

    # return: feasible or not
    def fix_point(
        self,
        forward_checkers: set[int],
    ) -> bool:
        while len(forward_checkers) > 0:
            cid = forward_checkers.pop()
            c = self.constraints[cid]
            feasible, changed_vars = c.prune(self.variables)
            if not feasible:
                return False  # infeasible

            # add affected constraints to forward checkers
            for vid in changed_vars:
                v = self.variables[vid]
                for cid in v.affected_constraints:
                    if cid != c.cid:
                        forward_checkers.add(cid)

        return True  # feasible

    def solve(self):
        unassigned = set(v.vid for v in self.variables)

        if not self.pre_check(unassigned):
            return

        self.dfs(unassigned)

    def pre_check(self, unassigned: set[int]) -> bool:
        # all constraints
        forward_checkers = {c.cid for c in self.constraints}

        for vid in unassigned:
            self.variables[vid].domain.snapshot()

        if not self.fix_point(forward_checkers):  # infeasible
            return False

        return True  # feasible

    def dfs(self, unassigned: set[int]) -> bool:
        if len(unassigned) == 0:
            self.solutions.append(  #
                {v.name: v.domain._values[0] for v in self.variables}
            )
            return True

        var = self.next_variable_picker(unassigned, self.variables)

        unassigned.remove(var.vid)

        ordered_values = self.values_orderer(var.domain.values())

        prev = var.domain.temp_assign(0)  # snapshot before assigning

        for val in ordered_values:
            var.domain._values[0] = val

            for vid in unassigned:
                self.variables[vid].domain.snapshot()

            if self.fix_point(var.affected_constraints.copy()):  # if feasible
                found_solution = self.dfs(unassigned)
                if found_solution and not self.find_all:
                    return True

            for vid in unassigned:
                self.variables[vid].domain.rollback()

        unassigned.add(var.vid)
        var.domain.temp_restore(prev)  # restore the snapshot

        return False
