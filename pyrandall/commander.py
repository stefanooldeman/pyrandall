from typing import NamedTuple

from . import executors
from .reporter import Reporter
from .executors.common import Executor
from .spec import Feature, Adapter
from .types import Flags, RunInfo

class Commander2:

    def __init__(self, feature: Feature, flags, reporter):
        self.feature = feature
        self.reporter = reporter

    def invoke(self):
        self.reporter.feature(self.feature.description)

        for scenario in self.feature.scenario_items:
            self.reporter.scenario(scenario.description)

        run_info = RunInfo(total_scenarios=len(self.feature.scenario_items))
        self.reporter.finished(run_info)
        return run_info


class Commander:
    def __init__(self, feature: Feature, flags: Flags):
        self.feature = feature
        self.flags = flags

    def invoke(self):
        success = self.run(Reporter())
        if success:
            raise SystemExit(0)
        else:
            raise SystemExit(1)

    def run(self, reporter):
        # options allow to:
        # - only simulate
        # - only validate
        # - consecutively simulate and validate
        reporter.feature(self.feature.description)
        self.run_scenarios(self.feature.scenario_items, reporter)
        reporter.print_failures()
        return reporter.passed()

    def run_scenarios(self, scenario_items, reporter):
        for scenario in scenario_items:
            # Commander responsible to implement how these functions are executed
            # for example in parallel, blocking, non blocking etc.
            # as a consequence: total execution time needs to be measured here,
            # Reporter is responsible for overall passing or failing of a test
            # 2 things:
            # 1. success/failure per test and overall
            # 2. call output interface
            reporter.scenario(scenario.description)

            if self.flags.has_simulate():
                reporter.simulate()
                resultset = reporter.create_and_track_resultset()
                for spec in scenario.simulate_tasks:
                    e = self.executor_factory(spec)
                    reporter.run_task(e.represent())
                    self.run_executor(e, resultset)

            if self.flags.has_validate():
                reporter.validate()
                resultset = reporter.create_and_track_resultset()
                for spec in scenario.validate_tasks:
                    e = self.executor_factory(spec)
                    reporter.run_task(e.represent())
                    self.run_executor(e, resultset)

    def run_executor(self, executor: Executor, resultset):
        # interacting with the Executor API
        for assertion_call in executor.run():
            assertion_call.report(resultset)

    def executor_factory(self, spec):
        # each spec can be run with an executor
        # based on the adapter defined on the spec
        if spec.adapter == Adapter.REQUESTS_HTTP:
            return executors.RequestHttp(spec)
        elif spec.adapter == Adapter.REQUEST_HTTP_EVENTS:
            return executors.RequestHttpEvents(spec)
        elif spec.adapter == Adapter.BROKER_KAFKA:
            return executors.BrokerKafka(spec)
        else:
            raise NotImplementedError("no such adapter implemented")
