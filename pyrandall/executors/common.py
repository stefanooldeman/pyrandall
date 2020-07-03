from pyrandall.types import AssertionCall
from pyrandall.exceptions import ZeroAssertions

from abc import ABC, abstractmethod


class Executor(ABC):

    def __init__(self, spec):
        self.spec = spec
        self.execution_mode = spec.execution_mode

    def run(self):
        if not self.spec.assertions:
            # TODO: Reporter should say "zero assertions found / specified"
            raise ZeroAssertions("zero assertions specified for executor")

        return list(self.execute())

    @abstractmethod
    def execute(self) -> [AssertionCall]:
        ...

    @abstractmethod
    def represent(self):
        ...
