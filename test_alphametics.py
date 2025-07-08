from rich import print
from datetime import datetime
import unittest
from variable import Variable
from constraint import LessThan, SumUp, AllUnique
from solver import Solver, BTSolver


def parse_question(s: str) -> Solver:
    solver = BTSolver()

    # Split input string by '+' or '=' and clean up
    lines = [x.strip() for x in s.replace("+", "=").split("=") if x.strip()]

    # Get all unique characters
    all_chars = [x for x in set("".join(lines))]

    # --------------- Variables ---------------
    variables = dict[str, Variable]()

    # All characters are 0-9
    non_0_chars = set(line[0] for line in lines)
    for ch in all_chars:
        if ch in non_0_chars:
            variables[ch] = Variable(ch, list(range(1, 10)))
        else:
            variables[ch] = Variable(ch, list(range(0, 10)))

    # Carries
    max_column = len(lines[-1])
    max_carry = 0
    for col in range(max_column - 1):
        char_count_at_col = sum(1 for line in lines[:-1] if len(line) > col)
        max_carry = (9 * char_count_at_col + max_carry) // 10

        variables[f"c{col}"] = Variable(f"c{col}", list(range(max_carry + 1)))

    for v in variables.values():
        solver.add_variable(v)

    # -------------- Constraints ------------
    # 1. Letters not equal to each other
    non_carry_variables = [v for v in variables.values() if not v.name.startswith("c")]
    solver.add_constraints(AllUnique(non_carry_variables))

    # 2. All chars on the left most column must be < the char at last_line[0]
    # e.g.: for SEND+MORE=GOLD, this means S<G and M<G
    # If there's only one, then it must == char0_last_line
    char0_last_line = lines[-1][0]
    for line in lines[:-1]:
        if len(line) == max_column:
            solver.add_constraint(
                LessThan(
                    variables[line[0]],
                    variables[char0_last_line],
                    include_equal=True,
                )
            )

    # 3. Column sum up
    for col in range(max_column):
        laddends = []
        lcoeffs = []
        raddends = []
        rcoeffs = []

        for line in lines[:-1]:  # except the last line
            if col < len(line):
                char = line[-(col + 1)]
                laddends.append(variables[char])
                lcoeffs.append(1)

        # add the sum char as -1*sum_char
        sum_char = lines[-1][-(col + 1)]
        raddends.append(variables[sum_char])
        rcoeffs.append(1)

        # TODO: handle carry greater than 10, such as 20?

        # Add carry from previous column
        if col > 0:
            laddends.append(variables[f"c{col - 1}"])
            lcoeffs.append(1)  # carry is always 1

        # Sub carry for this column
        if col != max_column - 1:
            raddends.append(variables[f"c{col}"])
            rcoeffs.append(10)  # always -10

        solver.add_constraint(SumUp(laddends, lcoeffs, raddends, rcoeffs))

    return solver


class TestAlphametics(unittest.TestCase):
    def setUp(self):
        self.tick = datetime.now()

    def tearDown(self):
        self.tock = datetime.now()
        print(self.tock - self.tick)

    def solve(self, question: str, solution: bool, expected: dict[str, int]):
        solver = parse_question(question)
        # solver.find_all = True
        solver.solve()

        if len(solver.solutions) == 0:
            self.assertFalse(solution, f"No solution found for: {question}")
        else:
            self.assertDictEqual(solver.solutions[0], expected)

    def test_send_more_money(self):
        question = "SEND + MORE = MONEY"
        expected = { 'S': 9, 'E': 5, 'N': 6, 'M': 1, 'Y': 2, 'D': 7, 'R': 8, 'O': 0, 'c0': 1, 'c1': 1, 'c2': 0, 'c3': 1 }  # fmt: off
        self.solve(question, True, expected)

    def test_i_bb_ill(self):
        question = "I + BB == ILL"
        expected = {'L': 0, 'B': 9, 'I': 1, 'c0': 1, 'c1': 1}  # fmt: off
        self.solve(question, True, expected)

    def test_as_a_mom(self):
        question = "AS + A == MOM"
        expected = {'O': 0, 'S': 2, 'A': 9, 'M': 1, 'c0': 1, 'c1': 1}  # fmt: off
        self.solve(question, True, expected)

    def test_no_no_too_late(self):
        question = "NO + NO + TOO == LATE"
        expected = {'A': 0, 'E': 2, 'N': 7, 'L': 1, 'T': 9, 'O': 4, 'c0': 1, 'c1': 1, 'c2': 1}  # fmt: off
        self.solve(question, True, expected)

    def test_he_sees_the_light(self):
        question = "HE + SEES + THE == LIGHT"
        expected = { 'S': 9, 'G': 2, 'E': 4, 'H': 5, 'L': 1, 'I': 0, 'T': 7, 'c0': 1, 'c1': 1, 'c2': 1, 'c3': 1 }  # fmt: off
        self.solve(question, True, expected)

    def test_a_a_a_a_a_a_a_a_a_a_b_bcc(self):
        question = "A + A + A + A + A + A + A + A + A + A + A + B == BCC"
        expected = {'B': 1, 'C': 0, 'A': 9, 'c0': 10, 'c1': 1}  # fmt: off
        self.solve(question, True, expected)

    def test_and_a_strong_offense_as_a_good_defense(self):
        question = "AND + A + STRONG + OFFENSE + AS + A + GOOD == DEFENSE"
        expected = { "S": 6, "G": 8, "A": 5, "E": 4, "N": 0, "F": 7, "D": 3, "R": 1, "T": 9, "O": 2, "c0": 3, "c1": 1, "c2": 1, "c3": 1, "c4": 1, "c5": 1, }  # fmt: off
        self.solve(question, True, expected)

    def test_long_1(self):
        question = "TEN + HERONS + REST + NEAR + NORTH + SEA + SHORE + AS + TAN + TERNS + SOAR + TO + ENTER + THERE + AS + HERONS + NEST + ON + STONES + AT + SHORE + THREE + STARS + ARE + SEEN + TERN + SNORES + ARE + NEAR == SEVVOTH"
        expected = { "S": 1, "A": 2, "E": 5, "H": 3, "N": 7, "V": 8, "R": 6, "T": 9, "O": 4, "c0": 13, "c1": 14, "c2": 13, "c3": 10, "c4": 7, "c5": 1 }  # fmt: off
        self.solve(question, True, expected)

    def test_long_2(self):
        question = "SO + MANY + MORE + MEN + SEEM + TO + SAY + THAT + THEY + MAY + SOON + TRY + TO + STAY + AT + HOME +  SO + AS + TO + SEE + OR + HEAR + THE + SAME + ONE + MAN + TRY + TO + MEET + THE + TEAM + ON + THE + MOON + AS + HE + HAS + AT + THE + OTHER + TEN == TESTS"
        expected = { "S": 3, "A": 7, "E": 0, "N": 6, "M": 2, "Y": 4, "H": 5, "R": 8, "T": 9, "O": 1, "c0": 14, "c1": 20, "c2": 14, "c3": 8 }  # fmt: off
        self.solve(question, True, expected)

    def test_long_3(self):
        question = "THIS + A + FIRE + THEREFORE + FOR + ALL + HISTORIES + I + TELL + A + TALE + THAT + FALSIFIES + ITS + TITLE + TIS + A + LIE + THE + TALE + OF + THE + LAST + FIRE + HORSES + LATE + AFTER + THE + FIRST + FATHERS + FORESEE + THE + HORRORS + THE + LAST + FREE + TROLL + TERRIFIES + THE + HORSES + OF + FIRE + THE + TROLL + RESTS + AT + THE + HOLE + OF + LOSSES + IT + IS + THERE + THAT + SHE + STORES + ROLES + OF + LEATHERS + AFTER + SHE + SATISFIES + HER + HATE + OFF + THOSE + FEARS + A + TASTE + RISES + AS + SHE + HEARS + THE + LEAST + FAR + HORSE + THOSE + FAST + HORSES + THAT + FIRST + HEAR + THE + TROLL + FLEE + OFF + TO + THE + FOREST + THE + HORSES + THAT + ALERTS + RAISE + THE + STARES + OF + THE + OTHERS + AS + THE + TROLL + ASSAILS + AT + THE + TOTAL + SHIFT + HER + TEETH + TEAR + HOOF + OFF + TORSO + AS + THE + LAST + HORSE + FORFEITS + ITS + LIFE + THE + FIRST + FATHERS + HEAR + OF + THE + HORRORS + THEIR + FEARS + THAT + THE + FIRES + FOR + THEIR + FEASTS + ARREST + AS + THE + FIRST + FATHERS + RESETTLE + THE + LAST + OF + THE + FIRE + HORSES + THE + LAST + TROLL + HARASSES + THE + FOREST + HEART + FREE + AT + LAST + OF + THE + LAST + TROLL + ALL + OFFER + THEIR + FIRE + HEAT + TO + THE + ASSISTERS + FAR + OFF + THE + TROLL + FASTS + ITS + LIFE + SHORTER + AS + STARS + RISE + THE + HORSES + REST + SAFE + AFTER + ALL + SHARE + HOT + FISH + AS + THEIR + AFFILIATES + TAILOR + A + ROOFS + FOR + THEIR + SAFE == FORTRESSES"
        expected = { "S": 4, "A": 1, "E": 0, "H": 8, "L": 2, "F": 5, "I": 7, "T": 9, "R": 3, "O": 6, "c0": 66, "c1": 87, "c2": 92, "c3": 67, "c4": 54, "c5": 22, "c6": 9, "c7": 5, "c8": 4 }  # fmt: off
        self.solve(question, True, expected)
