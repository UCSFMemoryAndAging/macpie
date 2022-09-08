from pathlib import Path

import pytest


# import fixtures needed across files
from tests.cli.macpie.keepone.fixtures import cli_keepone_big
from tests.cli.macpie.link.fixtures import (
    cli_link_full_no_merge,
    cli_link_small_no_merge,
    cli_link_small_with_merge,
    cli_link_small_with_dups,
)


def pytest_addoption(parser):
    parser.addoption(
        "--debugdir", action="store_true", default=False, help="assist with debugging tests"
    )
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def debugdir(request):
    val = request.config.getoption("--debugdir")
    if val is True:
        this_dir = Path(__file__).parent.absolute()
        base_dir = this_dir / "test_output"
        try:
            node_name = request.node.name
            module_name = request.module.__name__
            folder_name = module_name + "." + node_name
            output_dir = Path(base_dir / folder_name)
        except Exception:
            output_dir = base_dir
        return output_dir
    return False
