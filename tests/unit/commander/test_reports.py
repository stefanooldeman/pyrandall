from unittest.mock import MagicMock, call

from pyrandall.commander import Commander2, Flags
from pyrandall.spec import ScenarioGroup

import pytest


@pytest.fixture
def flags():
    # return Flags.DESCRIBE | Flags.SIMULATE
    return None


@pytest.fixture
def scenario_groups():
    return [MagicMock(description="send hello", set_spec=ScenarioGroup),
         MagicMock(description="reply hi", set_spec=ScenarioGroup)]

# it reports when commander is going
#  to start running a feature and its
#  scenarios

def test_describe_startup_1(reporter, flags):
    feature = MagicMock(description = "greeting")
    cmd = Commander2(feature, flags, reporter)
    cmd.invoke()

    reporter.feature.assert_called_with("greeting")

def test_describe_startup_2(reporter, flags):
    feature = MagicMock(description = "other")
    cmd = Commander2(feature, flags, reporter)
    cmd.invoke()

    reporter.feature.assert_called_with("other")

# it reports when commander has completed
#  running all scenarios

def test_finished_without_scenarios(reporter, flags):
    feature = MagicMock(scenario_groups=[])
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.finished.assert_called_with(info)
    assert info.total_scenarios == 0

def test_finished_with_two_scenarios(reporter, flags, scenario_groups):
    feature = MagicMock(scenario_groups=scenario_groups)
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.finished.assert_called_with(info)
    assert info.total_scenarios == 2

# it reports the description of a scenarios
# when run

def test_describe_zero_scenarios(reporter, flags):
    feature = MagicMock(scenario_groups=[])
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.scenario.assert_not_called()
    reporter.finished.assert_called_with(info)
    assert info.total_scenarios == 0

def test_describe_two_scenario_en(reporter, flags, scenario_groups):
    # given two scenarios
    # and commander
    feature = MagicMock(scenario_groups=scenario_groups)
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.scenario.assert_has_calls([
        call("send hello"),
        call("reply hi")
    ])

def test_describe_two_scenario_it(reporter, flags):
    # given two scenarios
    s = [MagicMock(description="send ciao", set_spec=ScenarioGroup),
         MagicMock(description="reply pronto", set_spec=ScenarioGroup)]
    # and commander
    feature = MagicMock(scenario_groups=s)
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.scenario.assert_has_calls([
        call("send ciao"),
        call("reply pronto")
    ])
