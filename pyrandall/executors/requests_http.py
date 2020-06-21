import requests

from pyrandall.types import Assertion, ResultSet

from .common import Executor


class RequestHttp(Executor):

    def __init__(self, spec, *args, **kwargs):
        super().__init__(spec)

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
