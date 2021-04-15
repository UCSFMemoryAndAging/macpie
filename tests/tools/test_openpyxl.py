from pathlib import Path

import openpyxl as pyxl
import pandas as pd

from macpie import openpyxltools
from macpie.testing import assert_dfs_equal

data_dir = Path("tests/data/").resolve()
io_data_dir = Path('tests/io/data/').resolve()


def test():
    f = io_data_dir / 'multi_index.xlsx'
    wb = pyxl.load_workbook(str(f))

    df_1_0_expected = pd.read_excel(f, sheet_name='1_0', header=0, index_col=None)
    df_1_0_result = openpyxltools.ws_to_df(wb['1_0'], num_header=1, num_idx=0)
    assert_dfs_equal(df_1_0_result, df_1_0_expected)

    df_1_1_expected = pd.read_excel(f, sheet_name='1_1', header=0, index_col=0)
    df_1_1_result = openpyxltools.ws_to_df(wb['1_1'], num_header=1, num_idx=1)
    assert_dfs_equal(df_1_1_result, df_1_1_expected)

    df_2_1_expected = pd.read_excel(f, sheet_name='2_1', header=[0, 1], index_col=0)
    df_2_1_result = openpyxltools.ws_to_df(wb['2_1'], num_header=2, num_idx=1)
    assert_dfs_equal(df_2_1_result, df_2_1_expected)

    df_2_2_expected = pd.read_excel(f, sheet_name='2_2', header=[0, 1], index_col=[0, 1])
    df_2_2_result = openpyxltools.ws_to_df(wb['2_2'], num_header=2, num_idx=2)
    assert_dfs_equal(df_2_2_result, df_2_2_expected)

    df_0_0_expected = pd.read_excel(f, sheet_name='0_0', header=None, index_col=None)
    df_0_0_result = openpyxltools.ws_to_df(wb['0_0'], num_header=0, num_idx=0)

    # pandas.read_excel must have a bug with header=None and index_col=0
    # because it's not returning the expected result, so creating expected result another way
    # df_0_1_expected = pd.read_excel(f, sheet_name='0_1', header=None, index_col=0)
    df_0_1_expected = df_1_1_expected.copy()
    df_0_1_expected.columns = list(range(9))
    df_0_1_result = openpyxltools.ws_to_df(wb['0_1'], num_header=0, num_idx=1)

    # assert_dfs_equal uses the .str accessor, which can only be used with string values.
    # These two dataframes have integers auto-created for their column labels, so using
    # native pandas equals method for assertion check
    assert df_0_0_result.equals(df_0_0_expected)
    assert df_0_1_result.equals(df_0_1_expected)
    # assert_dfs_equal(df_0_0_result, df_0_0_expected)
    # assert_dfs_equal(df_0_1_result, df_0_1_expected)
