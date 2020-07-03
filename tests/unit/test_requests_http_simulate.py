from unittest.mock import MagicMock

import pytest

from pyrandall.executors import RequestHttp, RequestHttpEvents
from pyrandall.spec import RequestEventsSpec, RequestHttpSpec
from pyrandall.types import Assertion, ExecutionMode
from pyrandall.exceptions import ZeroEvents


STATUS_CODE_ASSERTION = {"status_code": 201}


@pytest.fixture
def simulator_1():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b'{"foo": "bar"}',
        method="POST",
        headers={},
    )
    return RequestHttp(spec)


@pytest.fixture
def simulator_2():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b"",
        method="POST",
        headers={},
    )
    return RequestHttp(spec)


@pytest.fixture
def simulator_3():
    r1 = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b"",
        method="POST",
        headers={},
    )
    r2 = RequestHttpSpec(
        execution_mode=ExecutionMode.SIMULATING,
        assertions=STATUS_CODE_ASSERTION,
        url="http://localhost:5000/users",
        body=b'{"foo": "bar"}',
        method="POST",
        headers={},
    )
    spec = RequestEventsSpec(requests=[r1, r2])
    return RequestHttpEvents(spec)


def test_simulate_fails_zero_requests():
    # given a spec with no assertions
    spec = RequestEventsSpec(requests=[])
    # when called
    executor = RequestHttpEvents(spec)
    # then
    with pytest.raises(ZeroEvents) as excinfo:
        executor.run()


def test_simulate__post_201_repsonse(simulator_1, vcr):
    with vcr.use_cassette("test_http_executor_simulate_post_201") as cassette:
        # when called
        assertion_calls = simulator_1.run()

        # then
        assert len(assertion_calls) == 2
        # request has been made
        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.body == b'{"foo": "bar"}'
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 201
        if cassette.rewound:
            assert cassette.all_played
        # status matched
        a1 = assertion_calls[0]
        assert a1.field == "status_code"
        assert a1.actual_value == 201
        assert a1.passed()
        # body skipped
        a2 = assertion_calls[1]
        assert a2.field == "body"
        assert not a2.called



def test_simulate_post_400_response(simulator_2, vcr):
    with vcr.use_cassette("test_http_executor_simulate_post_400_response") as cassette:
        # when called
        assertion_calls = simulator_2.run()

        # then
        assert len(assertion_calls) == 2
        # request has been made
        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.body is None
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 400
        if cassette.rewound:
            assert cassette.all_played
        # status did not matched
        a1 = assertion_calls[0]
        assert a1.field == "status_code"
        assert a1.actual_value == 400
        assert not a1.passed()
        # body skipped
        a2 = assertion_calls[1]
        assert a2.field == "body"
        assert not a2.called


def test_simulate_post_200_and_400(simulator_3, vcr):
    with vcr.use_cassette("test_http_executor_simulate_post_201_and_400") as cassette:
        # when called
        assertion_calls = simulator_3.run()

        # then
        assert len(assertion_calls) == 4
        # two requests made
        assert len(cassette) == 2
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/users"
        assert r0.body is None
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 400

        r1 = cassette.requests[1]
        assert r1.url == "http://localhost:5000/users"
        assert r1.body == b'{"foo": "bar"}'
        response = cassette.responses_of(r1)[0]
        assert response["status"]["code"] == 201
        if cassette.rewound:
            assert cassette.all_played

