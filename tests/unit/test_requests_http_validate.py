from unittest.mock import MagicMock, call, patch

import pytest

from pyrandall.executors import RequestHttp
from pyrandall.spec import RequestHttpSpec
from pyrandall.types import Assertion, ExecutionMode
from pyrandall.exceptions import ZeroAssertions



@pytest.fixture
def validator_1():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        url="http://localhost:5000/foo/1",
        events=[],
        method="GET",
        headers={},
        assertions={"status_code": 404},
    )
    return RequestHttp(spec)


@pytest.fixture
def validator_3():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        method="GET",
        headers={},
        url="http://localhost:5000/foo/2",
        assertions={"body": b'{"foo": 2, "bar": false}'},
    )
    return RequestHttp(spec)


@pytest.fixture
def validator_4():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        method="GET",
        headers={},
        url="http://localhost:5000/foo/2",
        assertions={"status_code": 201, "body": b'{"foo": 2, "bar": false}'},
    )
    return RequestHttp(spec)


@pytest.fixture
def validator_5():
    spec = RequestHttpSpec(
        execution_mode=ExecutionMode.VALIDATING,
        events=[],
        method="GET",
        headers={},
        url="http://localhost:5000/foo/2",
        assertions={"status_code": 201, "body": b'{"foo": 2'},
    )
    return RequestHttp(spec)


def test_executor_fails_zero_assertions():
    spec = MagicMock(
        unsafe=True, execution_mode=ExecutionMode.VALIDATING, assertions=[]
    )
    executor = RequestHttp(spec)
    with pytest.raises(ZeroAssertions) as excinfo:
        executor.run()


def test_validate_makes_get_and_match_404(validator_1, vcr):
    # given a request should return 404
    with vcr.use_cassette("test_http_executor_validate_makes_get") as cassette:
        # when called
        assertion_calls = validator_1.run()

        # then
        assert len(assertion_calls) == 2
        # request has been made
        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/1"
        assert r0.body is None
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 404
        if cassette.rewound:
            assert cassette.all_played
        # status matched
        a1 = assertion_calls[0]
        assert a1.field == "status_code"
        assert a1.actual_value == 404
        assert a1.passed()
        # body skipped
        a2 = assertion_calls[1]
        assert a2.field == "body"
        assert not a2.called


def test_validate_makes_get_and_matches_body(validator_3, vcr):
    with vcr.use_cassette(
        "test_http_executor_validate_makes_get_and_matches_body"
    ) as cassette:
        # when called
        assertion_calls = validator_3.run()

        # then
        assert len(assertion_calls) == 2
        # request has been made
        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/2"
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 200
        assert response["body"]["string"] == b'{"foo": 2, "bar": false}'
        if cassette.rewound:
            assert cassette.all_played
        # status
        a1 = assertion_calls[0]
        assert a1.field == "status_code"
        assert a1.passed()
        # body
        a2 = assertion_calls[1]
        assert a2.field == "body"
        assert a2.passed()


def test_validate__matches_body_not_status(validator_4, vcr):
    with vcr.use_cassette(
        "test_http_executor_validate__matches_body_and_status"
    ) as cassette:
        assertion_calls = validator_4.run()

        # then
        assert len(assertion_calls) == 2
        # request has been made
        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/2"
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 200
        assert response["body"]["string"] == b'{"foo": 2, "bar": false}'
        if cassette.rewound:
            assert cassette.all_played
        # status did not match
        a1 = assertion_calls[0]
        assert a1.field == "status_code"
        assert not a1.passed()
        # body did match
        a2 = assertion_calls[1]
        assert a2.field == "body"
        assert a2.passed()



def test_validate_body_and_status_do_not_match(validator_5, vcr):
    # given assertions on status code and body (validator_5)
    with vcr.use_cassette(
        "test_http_executor_validate_body_and_status_do_not_match"
    ) as cassette:
        # when called
        assertion_calls = validator_5.run()

        # then 
        assert len(assertion_calls) == 2
        # request has been made
        assert len(cassette) == 1
        r0 = cassette.requests[0]
        assert r0.url == "http://localhost:5000/foo/2"
        response = cassette.responses_of(r0)[0]
        assert response["status"]["code"] == 200
        assert response["body"]["string"] == b'{"foo": 2, "bar": false}'
        if cassette.rewound:
            assert cassette.all_played
        # status did not match
        a1 = assertion_calls[0]
        assert a1.field == "status_code"
        assert not a1.passed()
        # body did not match
        a2 = assertion_calls[1]
        assert a2.field == "body"
        assert not a2.passed()
