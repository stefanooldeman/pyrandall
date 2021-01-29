from unittest.mock import MagicMock

import pytest

from pyrandall.executors.common import Executor
from pyrandall.commander import Commander, Flags
from pyrandall.reporter import ResultSet


def test_commander_run_one_for_one(spec_builder, reporter, vcr):
    with vcr.use_cassette("test_commander_run_one_for_one") as cassette:
        reporter.create_and_track_resultset.return_value = MagicMock(ResultSet, unsafe=True)

        c = Commander(spec_builder.feature(), Flags.E2E)
        c.run(reporter)

        reporter.feature.assert_called_once_with("One event"),
        reporter.scenario.assert_any_call("Send words1 event")
        # at least once called
        reporter.simulate.assert_called()
        reporter.validate.assert_called()
        reporter.run_task.assert_called()
        reporter.print_failures.assert_called_once_with()
        reporter.passed.assert_called_once()
        assert len(cassette) == 2
