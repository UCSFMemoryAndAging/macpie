from pathlib import Path

import pytest

from macpie import io, util


data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/pandas/operators/group_by_keep_one/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = ['link_date', 'link_id']


def test_keep_first_csv():
    # test first
    df = io.file_to_dataframe(data_dir / "instr1_primaryall.csv")

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='first')

    expected_result = io.file_to_dataframe(data_dir / "instr1_primaryfirst.csv")
    expected_result = result.mac.assimilate(expected_result)

    util.testing.assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)


@pytest.mark.slow
def test_keep_first_xl():
    # test first
    df = io.file_to_dataframe(data_dir / "instr1_primaryall.xlsx")

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='first')

    expected_result = io.file_to_dataframe(data_dir / "instr1_primaryfirst.xlsx")
    expected_result = result.mac.assimilate(expected_result)

    util.testing.assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)


def test_keep_latest_csv():
    # test latest
    df = io.file_to_dataframe(data_dir / "instr1_primaryall.csv")

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='latest')

    expected_result = io.file_to_dataframe(data_dir / "instr1_primarylatest.csv")
    expected_result = result.mac.assimilate(expected_result)

    util.testing.assert_dfs_equal(result, expected_result, cols_ignore=cols_ignore, output_dir=output_dir)
