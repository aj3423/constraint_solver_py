import unittest
from random import shuffle
from itertools import combinations
from domain import Domain


class TestDomain(unittest.TestCase):
    # def test_DomainSet(self):
    #     d = DomainSet(list(range(10)))
    #     self.assertSetEqual(d.values, set(list(range(10))))
    #     self.assertListEqual(d.snapshots, [])

    #     # snapshot
    #     d.snapshot()
    #     self.assertListEqual(d.snapshots, [[]])

    #     # remove
    #     d.remove(0)
    #     self.assertSetEqual(d.values, set(list(range(1, 10))))
    #     d.remove(5)
    #     self.assertSetEqual(d.values, set([1, 2, 3, 4, 6, 7, 8, 9]))

    #     # restore
    #     d.rollback()
    #     self.assertSetEqual(d.values, set(list(range(10))))

    def test_Domain(self):
        COMBINATION_SIZE = 8

        for comb_size in range(1, COMBINATION_SIZE):
            values = list(range(0, 10))
            d = Domain(values)
            copy = values.copy()

            comb = combinations(copy, comb_size)

            for c in comb:
                d.snapshot()
                removing = list(c)
                shuffle(removing)

                for i, v in enumerate(removing):
                    d.remove_at(i)

                d.rollback()
                self.assertListEqual(sorted(list(d.values())), copy)
                self.assertEqual(d.barrier, len(copy))
                self.assertEqual(len(d.snapshots), 0)
