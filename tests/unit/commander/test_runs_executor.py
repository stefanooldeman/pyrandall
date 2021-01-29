import time
from unittest.mock import MagicMock, call

from pyrandall.commander import Commander2, Flags
from pyrandall.spec import ScenarioGroup
from pyrandall.executors.common import Executor
from pyrandall.types import NoOpSpec, ExecutionMode, AssertionCall
from pyrandall.spec import SpecBuilder
from ...helper import TalkExecutor

import pytest

@pytest.fixture
def flags():
    return Flags.DESCRIBE | Flags.SIMULATE | Flags.VALIDATE

@pytest.fixture
def spec_builder():
    return SpecBuilder(
        specfile=open("examples/scenarios/one_event_within.yaml"),
        dataflow_path="examples/",
        default_request_url="http://localhost:5000",
    )

# it runs a spec feature
#  to start running a feature and its 
#  scenarios
def test_it_simulates_then_validates(flags, spec_builder, reporter):
    # given an executor for simulate and validate
    feature = spec_builder.feature()
    # when called
    cmd = Commander2(feature, flags, reporter)
    run_info = cmd.invoke()
    
    assert run_info.total_scenarios == 2
    assert False, "validator expected to be called after simulator completed"

@pytest.mark.skip
def test_runs_two_scenario_groups_concurrently():
    assert False
