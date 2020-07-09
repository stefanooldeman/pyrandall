from unittest.mock import MagicMock

from pyrandall.commander import Commander2, Flags

import pytest


@pytest.fixture
def flags():
    return Flags.DESCRIBE | Flags.SIMULATE


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

def test_finished_without_scenarios(reporter, flags):
    feature = MagicMock(scenario_items=[])
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.finished.assert_called_with(info)
    assert info.total_scenarios == 0

def test_finished_with_two_scenarios(reporter, flags):
    feature = MagicMock(scenario_items=[1, 2])
    cmd = Commander2(feature, flags, reporter)
    info = cmd.invoke()

    reporter.finished.assert_called_with(info)
    assert info.total_scenarios == 2
