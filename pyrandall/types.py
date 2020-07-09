from abc import ABCMeta, abstractmethod
from enum import Enum, Flag, auto
from typing import Any, Dict, List, NamedTuple, NamedTupleMeta

import jsondiff
from deepdiff import DeepDiff


class ExecutionMode(Enum):
    SIMULATING = auto()
    VALIDATING = auto()

    def represent(self):
        return self.name.lower()


class Adapter(Enum):
    REQUEST_HTTP_EVENTS = "request/http/events"
    REQUESTS_HTTP = "request/http"
    BROKER_KAFKA = "broker/kafka"

    def __str__(self):
        return f"adapter: {self.value}"


class Flags(Flag):
    NOOP = 0  # No Operation
    
    DESCRIBE = auto()

    BLOCKING = auto()
    # REALTIME = auto()

    SIMULATE = auto()
    VALIDATE = auto()

    E2E = BLOCKING | SIMULATE | VALIDATE

    # def run_realtime(self):
    #     return self & Flags.REALTIME

    def has_validate(self):
        return Flags.VALIDATE in self

    def has_simulate(self):
        return Flags.SIMULATE in self


class Assertion:

    def __init__(self, field: str, spec: Dict, on_fail_text):
        self.field = field
        self.spec = spec
        self.on_fail_text = on_fail_text
        if self.field in self.spec:
            self.call = self.create_assertion(self.spec[self.field])
        else:
            self.call = SkipAssertionCall(self.field)

    def __enter__(self):
        return self.call

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # TODO: check that no errors where raised
        # (to check a http / socket connection was successfull without exceptions)
        pass

    def create_assertion(self, value):
        return AssertionCall(field=self.field, expected_value=value)


class UnorderedDiffAssertion(Assertion):
    def __init__(self, field: str, spec: Dict, on_fail_text):
        super().__init__(field, spec, on_fail_text)

    def create_assertion(self, value):
        return UnorderedCompare(self.field, expected_value=value)


class AssertionCall:
    def __init__(self, field, expected_value):
        self.field = field
        self.expected = expected_value
        self.actual = None
        self.called = False
        self.result = None

    @property
    def actual_value(self):
        return self.actual

    @actual_value.setter
    def actual_value(self, value):
        self.actual = value
        self.eval(value)

    def eval(self, actual_value):
        self.called = True
        self.result = self.expected == actual_value
        return self.result

    def passed(self):
        return self.called and self.result

    def report(self, resultset):
        # think twice about if this method should be here
        if self.passed():
            resultset.assertion_passed(self)
        elif self.called:
            resultset.assertion_failed(self, str(self))
        else:
            resultset.assertion_skipped(self)

    def __str__(self):
        if self.passed():
            return f"assertion passed on {self.field}, expected {self.expected}, and got {self.actual}"
        else:
            return f"assertion failed on {self.field}, expected {self.expected}, but got {self.actual}"


class UnorderedCompare(AssertionCall):
    def __init__(self, field, expected_value):
        super().__init__(field, expected_value)
        self.diff = None

    def eval(self, actual_value):
        self.called = True
        self.diff = DeepDiff(
            self.expected,
            actual_value,
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
        )
        self.result = self.diff == {}
        return self.result

    def __str__(self):
        if self.passed():
            return super().__str__()
        else:
            return (
                f"assertion failed {self.field}, "
                f"got: {self.expected}"
                f"diff: {self.diff}"
                f"See https://github.com/seperman/deepdiff for more info on how to read the diff"
            )


def json_deep_equals(expected, actual):
    result = jsondiff.diff(expected, actual)
    return result == {}


class SkipAssertionCall(AssertionCall):
    def __init__(self, field):
        super().__init__(field, None)

    def eval(self, actual_value):
        pass

    def passed(self):
        return True

    def __str__(self):
        return f"assertion skipped"


class RunInfo(NamedTuple):
    total_scenarios: int


class ResultSet:
    def __init__(self, reporter):
        self.assertions = []
        self.reporter = reporter

    def all(self, assertions=None):
        return len(self.assertions) != 0 and all(self.assertions)

    def assertion_failed(self, assertion_call, fail_text):
        self.reporter.print_assertion_failed(assertion_call, fail_text)
        self.assertions.append(False)

    def assertion_passed(self, assertion_call: AssertionCall):
        self.reporter.print_assertion_passed(assertion_call)
        self.assertions.append(True)

    def assertion_skipped(self, assertion_call: AssertionCall):
        self.reporter.print_assertion_skipped(assertion_call)
        # True right?
        self.assertions.append(True)


# implicit Data interface of records below:
# - field execution_mode is present
# - field adapter is constant
# - field assertions is present
class NamedTupleABCMeta(ABCMeta, NamedTupleMeta):
    pass

class Spec(metaclass=NamedTupleABCMeta):
    pass


class RequestHttpSpec(NamedTuple, Spec):
    execution_mode: ExecutionMode
    # general request options
    method: str
    url: str
    headers: Dict[str, str]
    # simulate fields
    body: bytes = None
    # TODO: remove all events from here
    events: List[str] = []
    # validate fields
    # assert_that_responded translated to fields
    assertions: Dict[str, Any] = {}
    adapter: Adapter = Adapter.REQUESTS_HTTP


class RequestEventsSpec(NamedTuple, Spec):
    # general request options
    requests: List[RequestHttpSpec]
    execution_mode = ExecutionMode.SIMULATING
    adapter: Adapter = Adapter.REQUESTS_HTTP
    # skip assertions
    assertions = True


class BrokerKafkaSpec(NamedTuple, Spec):
    execution_mode: ExecutionMode
    # general broker options
    topic: str
    # simulate fields
    events: List[str] = []
    # validate fields
    # assert_that_responded translated to fields
    assertions: Dict[str, Any] = {}
    adapter: Adapter = Adapter.BROKER_KAFKA


__all__ = [
    "ExecutionMode",
    "Adapter",
    "Flags",
    "Assertion",
    "AssertionCall",
    "SkipAssertionCall",
    "Spec",
    "RequestHttpSpec",
    "RequestEventsSpec",
    "BrokerKafkaSpec",
]
