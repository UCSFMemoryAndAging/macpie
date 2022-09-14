from pathlib import Path

import pandas as pd
import pytest

from macpie import get_option
from macpie.pandas import read_file


DATA_DIR = Path("tests/data/").resolve()

COL_FILTER_KWARGS = {
    "items": ["link_date", "link_id", get_option("column.system.duplicates")],
    "invert": True,
}


def test_keep_earliest_csv():
    # test earliest
    df = read_file(DATA_DIR / "instr1_primaryall.csv")

    result = df.mac.group_by_keep_one(group_by_col="pidn", date_col_name="dcdate", keep="earliest")

    assert get_option("column.system.duplicates") in result.columns

    expected_result = read_file(DATA_DIR / "instr1_primaryearliest.csv")

    (left, right) = result.mac.conform(
        expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, dtypes=True, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)


@pytest.mark.slow
def test_keep_earliest_xl():
    # test earliest
    df = read_file(DATA_DIR / "instr1_primaryall.xlsx")

    result = df.mac.group_by_keep_one(group_by_col="pidn", date_col_name="dcdate", keep="earliest")
    expected_result = read_file(DATA_DIR / "instr1_primaryearliest.xlsx")

    (left, right) = result.mac.conform(
        expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, dtypes=True, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)


def test_keep_latest_csv():
    # test latest
    df = read_file(DATA_DIR / "instr1_primaryall.csv")

    result = df.mac.group_by_keep_one(group_by_col="pidn", date_col_name="dcdate", keep="latest")
    expected_result = read_file(DATA_DIR / "instr1_primarylatest.csv")

    (left, right) = result.mac.conform(
        expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, dtypes=True, values_order=True
    )
    pd.testing.assert_frame_equal(left, right)
