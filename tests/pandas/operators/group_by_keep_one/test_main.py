from pathlib import Path

import pytest

from macpie._config import get_option
from macpie.pandas import file_to_dataframe
from macpie.testing import assert_dfs_equal


data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/pandas/operators/group_by_keep_one/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = ['link_date', 'link_id', get_option("column.system.duplicates")]


def test_keep_earliest_csv():
    # test earliest
    df = file_to_dataframe(data_dir / "instr1_primaryall.csv")

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='earliest')

    assert get_option("column.system.duplicates") in result.columns

    expected_result = file_to_dataframe(data_dir / "instr1_primaryearliest.csv")

    assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)


@pytest.mark.slow
def test_keep_earliest_xl():
    # test earliest
    df = file_to_dataframe(data_dir / "instr1_primaryall.xlsx")

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='earliest')

    expected_result = file_to_dataframe(data_dir / "instr1_primaryearliest.xlsx")

    assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)


def test_keep_latest_csv():
    # test latest
    df = file_to_dataframe(data_dir / "instr1_primaryall.csv")

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='latest')

    expected_result = file_to_dataframe(data_dir / "instr1_primarylatest.csv")

    assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)
