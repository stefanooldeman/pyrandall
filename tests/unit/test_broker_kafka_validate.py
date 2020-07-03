from unittest import mock
from unittest.mock import MagicMock

import pytest

from pyrandall.executors import BrokerKafka
from pyrandall.spec import BrokerKafkaSpec
from pyrandall.types import Assertion, SkipAssertionCall, ExecutionMode


def new_executor(assertions):
    spec = BrokerKafkaSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        topic="foo",
        assertions=assertions,
    )
    return BrokerKafka(spec)


MESSAGE_JSON = b'{\n  "uri": "iphone://settings/updates",\n  "session": "111",\n  "timestamp": 2\n}\n'


# given consumer returns a list with 0 messages
@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.check_connection", return_value=True)
@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume", return_value=[])
def test_validate_fail_zero_messages(_consume, _check):
    # given the expected value is 1
    validator = new_executor({"total_events": 1})
    # when called
    assertion_calls = validator.run()

    # then get two results
    assert len(assertion_calls) == 2
    # first one failed
    a1 = assertion_calls[0]
    assert a1.field == "total_events"
    assert a1.called
    assert not a1.passed()
    # second one failed
    a2 = assertion_calls[1]
    assert a2.field == "unordered"
    assert not a2.called
    assert isinstance(a2, SkipAssertionCall)



@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.check_connection", return_value=True)
@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume")
def test_validate_fail_one_messages_body(consume, _check):
    # given a value that is empty json
    consume.return_value = [{"value": b"{}"}]
    # and a assertion on a full example json
    validator = new_executor(
        {"total_events": 1, "unordered": [{"value": MESSAGE_JSON}]}
    )
    # when called
    assertion_calls = validator.run()

    # then get two results
    assert len(assertion_calls) == 2
    assert len(assertion_calls) == 2
    # expect totals to pass
    a1 = assertion_calls[0]
    assert a1.field == "total_events"
    assert a1.called
    assert a1.passed()
    # expect diff to fail
    a2 = assertion_calls[1]
    assert a2.field == "unordered"
    assert a2.called
    assert not a2.passed()


@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.check_connection", return_value=True)
@mock.patch("pyrandall.executors.broker_kafka.KafkaConn.consume")
def test_validate_matches_all(consume, _check):
    # given a message with bytes json
    consume.return_value = [MESSAGE_JSON]
    # and validators
    validator = new_executor(
        {"total_events": 1, "unordered": [MESSAGE_JSON]}
    )
    # when called
    assertion_calls = validator.run()

    # then get two results
    assert len(assertion_calls) == 2
    assert len(assertion_calls) == 2
    # expect to pass
    a1 = assertion_calls[0]
    assert a1.field == "total_events"
    assert a1.called
    assert a1.passed()
    # and no diff, thus pass
    a2 = assertion_calls[1]
    assert a2.field == "unordered"
    assert a2.called
    assert a2.passed()
