import time
from unittest.mock import MagicMock, call

from pyrandall.commander import Commander2, Flags
from pyrandall.spec import ScenarioGroup
from pyrandall.executors.common import Executor
from pyrandall.types import NoOpSpec, ExecutionMode, AssertionCall

import pytest


class TalkExecutor(Executor):

    def __init__(self, spec, helper):
        super().__init__(spec)
        self.helper = helper

    def execute(self):
        if self.execution_mode is ExecutionMode.SIMULATING:
            time.sleep(0.1)
            self.helper.send()
        elif self.execution_mode is ExecutionMode.VALIDATING:
            time.sleep(0.1)
            self.helper.reply()

        return MagicMock(set_spec=AssertionCall)

    def represent(self):
        print("Running Talk executor (Test Mock)")

@pytest.fixture
def flags():
    return Flags.DESCRIBE | Flags.SIMULATE | Flags.VALIDATE

# it runs a spec feature
#  to start running a feature and its 
#  scenarios
@pytest.mark.skip
def test_it_simulates_then_validates(flags, reporter):
    # given an executor for simulate and validate
    simulator = MagicMock(name="simulator-helper")
    validator = MagicMock(name="validator-helper")
    e1 = TalkExecutor(NoOpSpec(execution_mode=ExecutionMode.SIMULATING), simulator)
    e2 = TalkExecutor(NoOpSpec(execution_mode=ExecutionMode.VALIDATING), validator)
    group1 = MagicMock(steps=[e1, e2], set_spec=ScenarioGroup)
    group2 = MagicMock(steps=[e1, e2], set_spec=ScenarioGroup)
    feature = MagicMock(scenario_groups=[group1, group2])
    # when called
    cmd = Commander2(feature, flags, reporter)
    run_info = cmd.invoke()
    
    assert run_info.total_scenarios == 2
    assert simulator.send.call_count == 2
    assert validator.reply.call_count == 2
    simulator.send.assert_any_call()
    validator.reply.assert_any_call()
    assert False, "validator expected to be called after simulator completed"

@pytest.mark.skip
def test_runs_two_scenario_groups_concurrently():
    assert False
