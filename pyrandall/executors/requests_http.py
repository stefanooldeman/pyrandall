import requests

from pyrandall import const
from pyrandall.types import Assertion, ResultSet

from .common import Executor


class RequestHttp(Executor):

    def __init__(self, spec, *args, **kwargs):
        super().__init__(spec)
        self.execution_mode = spec.execution_mode
        self.spec = self.add_custom_headers(spec)

    def execute(self, resultset: ResultSet):
        spec = self.spec
        # TODO: assert / tests the request happened without exceptions
        # act on __exit__ codes
        # with Assertion("response", spec.assertions, "http response", reporter) as a:
        if spec.body:
            response = requests.request(
                spec.method, spec.url, headers=spec.headers, data=spec.body
            )
        else:
            response = requests.request(spec.method, spec.url, headers=spec.headers)

        with Assertion(
            "status_code", spec.assertions, "http response status_code", resultset
        ) as a:
            a.actual_value = response.status_code
            yield a

        with Assertion("body", spec.assertions, "http response body", resultset) as a:
            # a.result = event.json_deep_equals(a.expected, response.content)
            a.actual_value = response.content
            yield a

    def add_custom_headers(self, spec):
        version = const.get_version()
        spec.headers['User-Agent'] = f"{const.PYRANDALL_USER_AGENT}/{version}"
        return spec

    def represent(self):
        return f"RequestHttp {self.spec.execution_mode.represent()} {self.spec.method} to {self.spec.url}"


class RequestHttpEvents(Executor):

    def __init__(self, spec, *args, **kwargs):
        super().__init__(spec)
        self.nr_of_requests = len(spec.requests)

    def run(self, resultset: ResultSet):
        if self.nr_of_requests == 0:
            # TODO: Reporter should say "zero events found / specified"
            return False

        return all([RequestHttp(r).run(resultset) for r in self.spec.requests])

    def execute(self, _resultset):
        pass

    def represent(self):
        return f"RequestHttpEvents {self.spec.execution_mode.represent()} {self.nr_of_requests} events"
