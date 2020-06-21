from pyrandall.types import ResultSet

from abc import ABC, abstractmethod


class Executor(ABC):

    def __init__(self, spec):
        self.spec = spec
        self.execution_mode = spec.execution_mode

    def run(self, resultset: ResultSet):
        if len(self.spec.assertions) == 0:
            # TODO: Reporter should say "zero assertions found / specified"
            return False

        assertions = self.execute(resultset)
        return all([a.passed() for a in assertions])

    @abstractmethod
    def execute(self, resultset: ResultSet):
        ...

    @abstractmethod
    def represent(self):
        ...
