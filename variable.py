from domain import Domain


class Variable:
    def __init__(self, name: str, values: list[int]):
        self.name = name
        self.domain = Domain(values)
        self.affected_constraints = set()

    def __repr__(self):
        return f"{self.name} = {self.domain.values()}"
