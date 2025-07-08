from itertools import islice

# Inspired by this:
#   https://opensourc.es/blog/constraint-solver-data-structure/
# It uses 2 extra arrays to track
#  - indices[]: the indices of the values
#  - recovery[]: it stores which index was removed

#  A B C D E F|
#  0 1 2 3 4 5|
#  0 0 0 0 0 0|
#
#  1. remove_at(2) as c
#
#  A B F D E|C
#  0 1 5 3 4|2
#  0 0 0 0 0|2
#
#  2. remove_at(3) as D
#
#  A B F E|D C
#  0 1 5 4|3 2
#  0 0 0 0|3 2
#
#  3. remove_at(2, 3) as F, E
#
#    - remove_at(2) as F
#
#    A B E|F D C
#    0 1 5|4 2 3
#    0 0 0|2 3 2
#
#    - remove_at(3) (should be E, but now it's F)
#
#    A B|E F D C
#    0 1|5 4 2 3
#    0 0|2 2 3 2


class Domain:
    def __init__(self, values: list[int]):
        self._values = values.copy()
        self.indices = [i for i in range(len(values))]
        self.recovery = [-1 for _ in range(len(values))]
        self.barrier = len(values)
        self.snapshots = []

    def __str__(self):
        return f"values: {self._values}\nbarrier: {self.barrier}\nindices: {self.indices}\nrecovery: {self.recovery}"

    def values(self):
        return islice(self._values, self.barrier)

    def len(self):
        return self.barrier

    def snapshot(self):
        self.snapshots.append(self.barrier)

    def rollback(self):
        b = self.snapshots.pop()
        while self.barrier < b:
            self.recover_1()

    def remove(self, to_rm: list[int]):
        for i in to_rm:
            self.remove_at(i)

    #  A B C D E F|
    #  0 1 2 3 4 5|
    #
    #  1. remove_at(2) as c
    #
    #  A B F D E|C
    #  0 1 5 3 4|2
    #  0 0 0 0 0|2
    #
    #  2. remove_at(3) as D
    #
    #  A B F E|D C
    #  0 1 5 4|3 2
    #  0 0 0 0|3 2
    #
    #  3. remove_at(2, 3) as F, E
    #
    #    - remove_at(2) as F
    #
    #    A B E|F D C
    #    0 1 5|4 2 3
    #    0 0 0|2 3 2
    #
    #    - remove_at(3) (should be E, but now it's F)
    #
    #    A B|E F D C
    #    0 1|5 4 2 3
    #    0 0|2 2 3 2
    def remove_at(self, i: int):
        self.barrier -= 1
        b = self.barrier

        if i >= b:
            new_i = self.recovery[i]
            if new_i != -1:
                i = new_i

        self.swap_value(i, b)
        self.swap_index(self.indices[i], self.indices[b])
        self.recovery[b] = i

    def recover_1(self):
        b = self.barrier
        i = self.recovery[b]
        self.swap_value(i, b)
        self.swap_index(self.indices[i], self.indices[b])
        self.recovery[b] = -1
        self.barrier += 1

    def swap_value(self, i: int, j: int):
        self._values[i], self._values[j] = self._values[j], self._values[i]

    def swap_index(self, i: int, j: int):
        self.indices[i], self.indices[j] = self.indices[j], self.indices[i]

    def temp_assign(self, value):
        v0 = self._values[0]
        self._values[0] = value
        barr = self.barrier
        self.barrier = 1
        return (v0, barr)

    def temp_restore(self, tup):
        value, barrier = tup
        self._values[0] = value
        self.barrier = barrier
