import pytest

from unittest.mock import MagicMock, call, patch, Mock

from pyrandall.types import ExecutionMode
from pyrandall.spec import ScenarioGroup

def test_scenario_group_has_two_steps(spec_builder):
    feature = spec_builder.feature()
    assert len(feature.scenario_groups) == 2
    group = feature.scenario_groups.pop()
    assert len(group.simulate_tasks) == 1
    assert len(group.validate_tasks) == 2

def test_scenario_group_builds_spec_class(spec_builder):
    feature = spec_builder.feature()
    assert len(feature.scenario_groups) == 2
    group = feature.scenario_groups.pop()

    assert len(group.simulate_tasks) == 1
    spec1 = group.simulate_tasks.pop()
    assert spec1.execution_mode == ExecutionMode.SIMULATING
    assert spec1.assertions != None

    assert len(group.validate_tasks) == 2
    spec2 = group.validate_tasks.pop()
    assert spec2.execution_mode == ExecutionMode.VALIDATING
    assert spec1.assertions != None
    assert spec1.assertions != None
