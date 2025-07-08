import unittest
from random import shuffle
from itertools import combinations
from constraint import NotEqual, Equal, SumUp
from variable import Variable


class TestConstraint(unittest.TestCase):
    def test_equal(self):
        print("Testing Equal Constraint")
        a = Variable("A", [1, 2, 3])
        b = Variable("B", [2, 3, 4, 5])
        a.vid = 0
        b.vid = 1
        variables = [a, b]

        cs = Equal(a, b)
        cs.cid = 0

        cs.prune(variables)

        self.assertListEqual(sorted(a.domain.values()), [2, 3])
        self.assertListEqual(sorted(b.domain.values()), [2, 3])

    def test_not_equal(self):
        print("Testing NotEqual Constraint")
        a = Variable("A", [3])
        b = Variable("B", [2, 3, 4, 5])
        a.vid = 0
        b.vid = 1
        variables = [a, b]

        cs = NotEqual(a, b)
        cs.cid = 0

        cs.prune(variables)

        self.assertListEqual(sorted(a.domain.values()), [3])
        self.assertListEqual(sorted(b.domain.values()), [2, 4, 5])

    def test_sum_up(self):
        print("Testing SumUp Constraint")
        a = Variable("A", [1, 2, 3])
        b = Variable("B", [1, 2, 3])
        c = Variable("C", [1, 2, 3])
        a.vid = 0
        b.vid = 1
        c.vid = 2
        variables = [a, b, c]

        cs = SumUp([a, b], [1, 1], [c], [1])
        cs.cid = 0

        cs.prune(variables)

        # print("After pruning:")
        # print(f"A: {a.domain.values()}")
        # print(f"B: {b.domain.values()}")
        # print(f"C: {c.domain.values()}")

        self.assertListEqual(sorted(a.domain.values()), [1, 2])
        self.assertListEqual(sorted(b.domain.values()), [1, 2])
        self.assertListEqual(sorted(c.domain.values()), [2, 3])
