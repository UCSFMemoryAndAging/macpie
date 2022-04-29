from pathlib import Path

import openpyxl as pyxl
import pandas as pd
from macpie.collections.mergeableanchoredlist import MergeableAnchoredList
import pytest

from macpie._config import get_option, set_option
from macpie import MacSeriesAccessor, MacDataFrameAccessor

# import fixtures needed across files
from tests.cli.macpie.keepone.fixtures import cli_keepone_big
from tests.cli.macpie.link.fixtures import (
    cli_link_full_no_merge,
    cli_link_small_no_merge,
    cli_link_small_with_merge,
    cli_link_small_with_dups,
)


def pytest_addoption(parser):
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
