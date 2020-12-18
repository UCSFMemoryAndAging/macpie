from pathlib import Path

import openpyxl as pyxl
import pandas as pd
import pytest

from macpie.pandas import MacDataFrameAccessor
from macpie.cli.subcommands import link

# import fixtures needed across files
from tests.cli.link.fixtures import link_full_no_merge, link_small_no_merge, link_small_with_merge


class Helpers:
    @staticmethod
    def read_merged_results(f, sheetname: str = link.SHEETNAME_MERGED_RESULTS):
        filename = str(f)
        wb = pyxl.load_workbook(filename)
        ws = wb[sheetname]
        if ws['A2'].value == link.COL_HEADER_ROW_INDEX:
            return pd.read_excel(filename, index_col=0, header=[0, 1], engine='openpyxl')
        else:
            return pd.read_excel(filename, index_col=None, header=[0, 1], engine='openpyxl')


@pytest.fixture
def helpers():
    return Helpers


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


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
