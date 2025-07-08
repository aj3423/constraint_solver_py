from abc import ABC, abstractmethod
from webbrowser import open_new_tab
from variable import Variable
import itertools
from util import exclude


# The very tiny constraint solver:
#  https://choco-solver.org/tinytiny/


class Constraint(ABC):
    @abstractmethod
    def affected_variables(self) -> set[int]:
        pass

    @abstractmethod
    def prune(self) -> (bool, list[int]):
        """
        return value:

        - feasible or not
        - all changed variables
        """
        pass

    @abstractmethod
    def __repr__(self):
        pass


class LessThan(Constraint):
    def __init__(self, v1, v2, include_equal: bool = False):
        self.vid1 = v1.vid
        self.vid2 = v2.vid
        self.name_map = {
            v1.vid: v1.name,
            v2.vid: v2.name,
        }
        self.include_equal = include_equal

    def affected_variables(self) -> set[int]:
        return {self.vid1, self.vid2}

    def __repr__(self):
        n1 = self.name_map[self.vid1]
        n2 = self.name_map[self.vid2]
        return f"{n1} < {n2}"

    def prune(self, variables: list[Variable]) -> (bool, list[int]):
        vid1 = self.vid1
        vid2 = self.vid2
        v1 = variables[vid1]
        v2 = variables[vid2]
        d1 = v1.domain
        d2 = v2.domain
        len1 = d1.len()
        len2 = d2.len()
        if len1 == 0 or len2 == 0:
            return False, None

        min_d1 = min(d1.values())
        max_d2 = max(d2.values())

        to_rm_1 = (
            [i for i, v in enumerate(d1.values()) if v >= max_d2]
            if self.include_equal
            else [i for i, v in enumerate(d1.values()) if v > max_d2]
        )
        if len(to_rm_1) == len1:  # "domain 1" becomes empty...
            return False, None
        to_rm_2 = (
            [i for i, v in enumerate(d2.values()) if v <= min_d1]
            if self.include_equal
            else [i for i, v in enumerate(d2.values()) if v < min_d1]
        )
        if len(to_rm_2) == len2:  # "domain 2" becomes empty...
            return False, None

        # update variable domains
        v1.domain.remove(to_rm_1)
        v2.domain.remove(to_rm_2)

        # return all changed variables
        changed = []
        if len(to_rm_1) > 0:
            changed.append(vid1)
        if len(to_rm_2) > 0:
            changed.append(vid2)
        return True, changed


class Equal(Constraint):
    def __init__(self, v1, v2):
        self.vid1 = v1.vid
        self.vid2 = v2.vid
        self.name_map = {
            v1.vid: v1.name,
            v2.vid: v2.name,
        }

    def affected_variables(self) -> set[int]:
        return {self.vid1, self.vid2}

    def __repr__(self):
        n1 = self.name_map[self.vid1]
        n2 = self.name_map[self.vid2]
        return f"{n1} == {n2}"

    def prune(self, variables: list[Variable]) -> (bool, list[int]):
        vid1 = self.vid1
        vid2 = self.vid2
        v1 = variables[vid1]
        v2 = variables[vid2]
        d1 = v1.domain
        d2 = v2.domain
        len1 = d1.len()
        len2 = d2.len()
        if len1 == 0 or len2 == 0:
            return False, None

        changed = []

        set2 = set(d2.values())
        to_rm_1 = [i for i, v in enumerate(d1.values()) if v not in set2]
        if len(to_rm_1) == len1:  # "domain 1" becomes empty...
            return False, None
        # update variable domains
        v1.domain.remove(to_rm_1)
        if len(to_rm_1) > 0:
            changed.append(vid1)

        set1 = set(d1.values())
        to_rm_2 = [i for i, v in enumerate(d2.values()) if v not in set1]
        if len(to_rm_2) == len2:  # "domain 2" becomes empty...
            return False, None
        # update variable domains
        v2.domain.remove(to_rm_2)
        if len(to_rm_2) > 0:
            changed.append(vid2)

        return True, changed


class NotEqual(Constraint):
    def __init__(self, v1, v2):
        self.vid1 = v1.vid
        self.vid2 = v2.vid
        self.name_map = {
            v1.vid: v1.name,
            v2.vid: v2.name,
        }

    def affected_variables(self) -> set[int]:
        return {self.vid1, self.vid2}

    def __repr__(self):
        n1 = self.name_map[self.vid1]
        n2 = self.name_map[self.vid2]
        return f"{n1} != {n2}"

    def prune(self, variables: list[Variable]) -> (bool, list[int]):
        vid1 = self.vid1
        vid2 = self.vid2
        v1 = variables[vid1]
        v2 = variables[vid2]
        d1 = v1.domain
        d2 = v2.domain
        len1 = d1.len()
        len2 = d2.len()
        if len1 == 0 or len2 == 0:
            return False, None

        # return all changed variables
        changed = []

        if len2 == 1:
            to_rm_1 = [i for i, v in enumerate(d1.values()) if v == d2._values[0]]
            if len(to_rm_1) == len1:  # "domain 1" becomes empty...
                return False, None
            # update variable domains
            v1.domain.remove(to_rm_1)

            if len(to_rm_1) > 0:
                changed.append(vid1)
        if len1 == 1:
            to_rm_2 = [i for i, v in enumerate(d2.values()) if v == d1._values[0]]
            if len(to_rm_2) == len2:  # "domain 2" becomes empty...
                return False, None
            # update variable domains
            v2.domain.remove(to_rm_2)

            if len(to_rm_2) > 0:
                changed.append(vid2)

        return True, changed


def AllUnique(variables: list[Variable]) -> list[NotEqual]:
    ret = []
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            ret.append(NotEqual(variables[i], variables[j]))
    return ret


# 3*x + 2*y + 5*z + ... == 4*a + 6*b + 7*c + ...
class SumUp(Constraint):
    # 1. Remove all repeated variables, e.g.:
    #   3x + ... =  x + ...
    #     -> 2x + ... = ...
    # 2. Move negative coeff to the other side, e.g.:
    #   3x = -5y + z
    #     -> 3x + 5y = z
    def __init__(
        self,
        lvars: list[Variable],
        lcoeffs: list[int],
        rvars: list[Variable],
        rcoeffs: list[int],
    ):
        all = dict[int, int]()

        # 1. add left side to `all`
        for i in range(len(lvars)):
            vid = lvars[i].vid
            co = lcoeffs[i]
            if vid in all:
                all[vid] += co
            else:
                all[vid] = co
        # 2. add right side to `all`
        for i in range(len(rvars)):
            vid = rvars[i].vid
            co = rcoeffs[i]
            if vid in all:
                all[vid] -= co
            else:
                all[vid] = -co

        # 3. split into left and right side
        self.lvids = list[int]()
        self.lcoeffs = list[int]()
        self.rvids = list[int]()
        self.rcoeffs = list[int]()
        for vid, co in all.items():
            if co == 0:
                continue
            if co < 0:
                self.rvids.append(vid)
                self.rcoeffs.append(-co)
            else:
                self.lvids.append(vid)
                self.lcoeffs.append(co)

        self.name_map = {v.vid: v.name for v in itertools.chain(lvars, rvars)}

    def affected_variables(self) -> set[int]:
        return set[int](self.lvids + self.rvids)

    def __repr__(self):
        lterms = " + ".join(
            list(
                map(
                    lambda vid, coeff: f"{self.name_map[vid]}*{coeff}",
                    self.lvids,
                    self.lcoeffs,
                )
            )
        )
        rterms = " + ".join(
            list(
                map(
                    lambda vid, scoeff: f"{self.name_map[vid]}*{scoeff}",
                    self.rvids,
                    self.rcoeffs,
                )
            )
        )

        return f"Sum:  {lterms} == {rterms}"

    def min_max_of_each_variable(
        self, variables: list[Variable], vids: list[int]
    ) -> list[tuple[int, int]]:
        ret = []  # the min, max value of domain Xi
        for vid in vids:
            var = variables[vid]
            min_v = 0
            max_v = 0
            for i, v in enumerate(var.domain.values()):
                if i == 0 or v < min_v:
                    min_v = v
                if i == 0 or v > max_v:
                    max_v = v
            ret.append((min_v, max_v))

        return ret

    # https://youtu.be/SCcOrHzdHxI?t=1446
    def prune(self, variables: list[Variable]) -> (bool, list[int]):
        # 1. Get the intersection of left part and right part
        l_min_max = self.min_max_of_each_variable(variables, self.lvids)
        r_min_max = self.min_max_of_each_variable(variables, self.rvids)

        LMIN = 0  # the minimum possible summary of left side
        LMAX = 0
        for n in range(len(self.lvids)):
            LMIN += l_min_max[n][0] * self.lcoeffs[n]
            LMAX += l_min_max[n][1] * self.lcoeffs[n]

        RMIN = 0  # the minimum possible summary of right side
        RMAX = 0
        for n in range(len(self.rvids)):
            RMIN += r_min_max[n][0] * self.rcoeffs[n]
            RMAX += r_min_max[n][1] * self.rcoeffs[n]

        # the intersection of left and right side:
        MIN = max(LMIN, RMIN)
        MAX = min(LMAX, RMAX)

        if MIN > MAX:
            return False, None

        # Both Left and Right sides should be in range of [MIN, MAX]
        #  MIN <= Left <= MAX
        #  MIN <= Right <= MAX

        changed_vids = set[int]()

        # 2. Prune left_side:
        for i, vid in enumerate(self.lvids):
            var = variables[vid]
            coeff = self.lcoeffs[i]

            # For min:
            #    co1*X1 + co2*X2 + ... >= MIN
            # -> with: Left = co1*X1 + co2*X2 + ..., if max(Left) if still less than MIN, then it's infeasible
            # -> max(Left) >= MIN
            # -> co1*X1 >= MIN - (max(Left) - co1*Max(X1))    # this applies to all X
            # For max:
            #    co1*X1 + co2*X2 + ... <= MAX
            # -> ...
            # -> co1*X1 <= MAX - (min(Left) - co1*Min(X1))
            to_rm = [
                rm
                for rm, v in enumerate(var.domain.values())
                if coeff * v < (MIN - (LMAX - coeff * l_min_max[i][1]))
                or coeff * v > (MAX - (LMIN - coeff * l_min_max[i][0]))
            ]
            if len(to_rm) == var.domain.len():  # "domain" becomes empty...
                return False, None

            if len(to_rm) > 0:
                changed_vids.add(vid)

            var.domain.remove(to_rm)

        # 2.2 Prune right_side:
        for i, vid in enumerate(self.rvids):
            var = variables[vid]
            coeff = self.rcoeffs[i]

            to_rm = [
                rm
                for rm, v in enumerate(var.domain.values())
                if coeff * v < (MIN - (RMAX - coeff * r_min_max[i][1]))
                or coeff * v > (MAX - (RMIN - coeff * r_min_max[i][0]))
            ]

            if len(to_rm) == var.domain.len():  # "domain" becomes empty...
                return False, None

            if len(to_rm) > 0:
                changed_vids.add(vid)

            var.domain.remove(to_rm)

        # TODO:
        # More accurate pruning

        return True, list(changed_vids)
