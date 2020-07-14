import time
from typing import NamedTuple
from unittest import mock
from unittest.mock import MagicMock

import pytest

from pyrandall.executors.common import Executor
from pyrandall.commander import Commander, Flags
from pyrandall.types import Spec, Assertion, AssertionCall


class AssertPoliteness(Assertion):
    def __init__(self, spec, assertion_call):
        field = "greeting"
        spec = spec.__dict__
        on_fail_text = "you did not greet with 'hello'"
        self.assertion_call = assertion_call
        super().__init__(field, spec, on_fail_text, resultset)

    def create_assertion():
        return self.assertion_call


class MoodSpec(NamedTuple, Spec):
    greeting: str
    assertions: Assertion


class TalkExecutor(Executor):
    def __init__(self, spec, reply):
        self.spec = spec
        # configure the reply to test pass / fail
        self.reply = reply

    def execute(self):
        with Assertion(
            "reply", self.spec.assertions, "greeting expects a reply"
        ) as a:
            a.actual_value = self.reply
            yield a

    def represent(self):
        print("Running Talk executor (Test Mock)")


def test_assertion_passed_and_tracked(resultset, feature):
    # given synchronous commander
    cmd = Commander(feature, Flags.E2E)
    # and a spec that expects hello back
    spec = MoodSpec(greeting="hi", assertions={"reply": "hello"})
    # and configure hello
    executor = TalkExecutor(spec, reply="hello")
    # when called
    cmd.run_executor(executor, resultset)

    resultset.assertion_failed.assert_not_called()
    assert (
        1 == resultset.assertion_passed.call_count
    ), 'expected method "assertion_passed(ANY)" to be called twice'


def test_assertion_failed_and_tracked(resultset, feature):
    # given synchronous commander
    cmd = Commander(feature, Flags.E2E)
    # and a spec that expects hello back
    spec = MoodSpec(greeting="hi", assertions={"reply": "hello"})
    # and configure no reply
    executor = TalkExecutor(spec, reply=None)
    # when called
    cmd.run_executor(executor, resultset)

    resultset.assertion_passed.assert_not_called()
    assert (
        1 == resultset.assertion_failed.call_count
    ), 'expected method "assertion_passed(ANY)" to be called twice'

def test_async_assertion_failed_and_tracked(resultset, feature):
    # given synchronous commander
    cmd = Commander(feature, Flags.E2E)
    # and a spec that expects hello back
    spec = MoodSpec(greeting="hi", assertions={"reply": "hello"})
    # and configure no reply
    executor = TalkExecutor(spec, reply=None)
    # when called
    cmd.run_executor(executor, resultset)

    resultset.assertion_passed.assert_not_called()
    assert (
        1 == resultset.assertion_failed.call_count
    ), 'expected method "assertion_passed(ANY)" to be called twice'
