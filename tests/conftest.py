import os
from unittest.mock import MagicMock

import pyrandall.cli
from pyrandall.spec import Feature
from pyrandall.reporter import Reporter
from pyrandall.types import ResultSet
from pyrandall.spec import SpecBuilder

from vcr import VCR
import pytest

from click.testing import CliRunner
from confluent_kafka.admin import AdminClient, ClusterMetadata


@pytest.fixture
def vcr_headers_filter():
    return [("User-Agent", None)]

@pytest.fixture
def vcr_match_on():
    return ["body", "headers"]

@pytest.fixture
def vcr(request):
    defaults = ["method", "scheme", "host", "port", "path", "query"]
    defaults += request.getfixturevalue("vcr_match_on")

    # record_mode = {once, new_episodes, none, all}
    # https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    return VCR(
        filter_headers=request.getfixturevalue("vcr_headers_filter"),
        record_mode=os.environ.get("VCR_MODE", "once"),
        cassette_library_dir="tests/fixtures/vcr",
        match_on=defaults,
        path_transformer=VCR.ensure_suffix(".yaml"),
    )

# Internal Class Mocks, Stubs etc.

@pytest.fixture
def feature():
    return MagicMock(spec_set=Feature)

@pytest.fixture
def reporter():
    return MagicMock(spec_set=Reporter)


@pytest.fixture
def spec_builder():
    return SpecBuilder(
        specfile=open("examples/scenarios/v2.yaml"),
        dataflow_path="examples/",
        default_request_url="http://localhost:5000",
    )

@pytest.fixture
def resultset():
    # Also see Reporter().create_and_track_resultset()
    # if this creates issues, move to MagicMock
    # for now it works to use this tiny object
    return MagicMock(spec_set=ResultSet, unsafe=True)


# Helper functions
# for example: file, http, kafka utilities or Cli Runner

@pytest.fixture
def kafka_cluster_info() -> ClusterMetadata:
    # this fixture can be used to assert the connection is configured
    # correctly and functioning
    kafka = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
    admin = AdminClient({"bootstrap.servers": kafka})
    cluster = admin.list_topics()
    assert ('{1: BrokerMetadata(1, %s)}' % kafka) == str(cluster.brokers)
    return cluster

@pytest.fixture
def pyrandall_cli():
    return PyrandallCli()


class PyrandallCli():

    def invoke(self, command):
        runner = CliRunner()
        return runner.invoke(pyrandall.cli.main, command, catch_exceptions=False)


def dictmock(dictdata):
    mock = MagicMock()
    def getitem(key):
        try:
            return dictdata[key]
        except KeyError as e:
            # assuming no range args are given
            return Mock(name=e.args[0])
    mock.__getitem__.side_effect = getitem
    return mock
