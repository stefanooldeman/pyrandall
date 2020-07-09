from sys import stdout
import jsondiff

from pyrandall.types import Assertion, AssertionCall, ResultSet, RunInfo

SPACE = "  - "
ONE_SPACE = "    - "
TWO_SPACE = "      - "


class Reporter(object):
    def __init__(self, printer=None):
        # instances off ResultSet
        self.results = []
        # failures are kept for printing at the end of a run
        self.failures = []
        if not printer:
            self.printer = stdout.write
        else:
            self.printer = printer

    def print(self, *args, **kwargs):
        self.printer(*args, **kwargs)

    def feature(self, text):
        """
            adds "scenario.feature" construct to the output buffer

            uses Scenario interface to get the title / description data
        """
        self.print(f"Feature: {text}")

    def scenario(self, text: str):
        """
            adds "scenario.feature.scenario" construct to the output buffer

            uses Scenario interface to get the title / description data
        """
        self.print(f"{SPACE}Scenario {text}")

    def finished(self, rinfo: RunInfo):
        self.print(f"completed running {rinfo.total_scenarios} scenarios")

    # TODO: move this to commander
    def create_and_track_resultset(self):
        rs = ResultSet(self)
        self.results.append(rs)
        return rs

    def simulate(self):
        """
            stores "scenario.feature.senario.simulate[]" items to the output buffer

            uses Scenario interface to get the title / description data
        """
        self.print(f"{ONE_SPACE}Simulate")

    def validate(self):
        """
            stores "scenario.feature.senario.validate[]" items to the output buffer

            uses Scenario interface to get the title / description data
        """
        self.print(f"{ONE_SPACE}Validate")

    def run_task(self, text):
        self.print(f"{ONE_SPACE}{text}")

    def print_assertion_failed(self, assertion_call, fail_text):
        # TODO: add assertion type (equal, greater than)
        self.print(
            f"{TWO_SPACE}assertion failed: {fail_text} did not equal, "
            f"{assertion_call}"
        )
        # This is redundant to the ResultSet tracking state
        self.failures.append(assertion_call)

    def print_assertion_passed(self, assertion_call: AssertionCall):
        self.print(f"{TWO_SPACE}{assertion_call}")

    def print_assertion_skipped(self, assertion_call: AssertionCall):
        self.print(f"{TWO_SPACE}{assertion_call}")
        pass

    def assertion(self, field, spec):
        return Assertion(field, spec, self)

    def print_failures(self):
        if self.failures:
            self.print("\nFailures:")
            for failed_assertion in self.failures:
                self.print(f"{ONE_SPACE}{failed_assertion}")

    def passed(self):
        return len(self.results) != 0 and all([rs.all() for rs in self.results])

    def failed_assertions(self):
        return self.failures

    def json_diff_report(expected, actual):
        return jsondiff.diff(expected, actual, syntax="explicit")
