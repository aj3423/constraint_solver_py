# It uses a set for pushing and popping values,
#  slower but more intuitive than using indices(see below).
class DomainSet:
    def __init__(self, values: list[int]):
        self.values = set(values)
        self.snapshots = []

    def __repr__(self):
        return f"{self.values}, snapshots = {self.snapshots}"

    def assign(self, values: set[int]):
        to_remove = self.values - values
        for v in to_remove:
            self.remove(v)
        to_add = values - self.values
        for v in to_add:
            self.add(v)

    def add(self, value):
        if value not in self.values:
            self.values.add(value)
            self.snapshots[-1].remove(value)

    def remove(self, value):
        self.values.remove(value)
        self.snapshots[-1].add(value)

    def snapshot(self):
        self.snapshots.append(set[int]())

    def rollback(self):
        removed = self.snapshots.pop()
        for v in removed:
            self.values.add(v)

    def discard(self):
        self.snapshots = []
