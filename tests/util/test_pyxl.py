from pathlib import Path

import openpyxl as pyxl
import pandas as pd

from macpie import util

data_dir = Path("tests/data/").resolve()
current_dir = Path('tests/io/data/').resolve()


def test():
    f = current_dir / 'multi_index.xlsx'
    wb = pyxl.load_workbook(str(f))

    df_0_0_expected = pd.read_excel(f, sheet_name='0_0', header=None, index_col=None, engine='openpyxl')
    df_0_0_result = util.pyxl.ws_to_df(wb['0_0'], num_header=0, num_idx=0)

    df_1_0_expected = pd.read_excel(f, sheet_name='1_0', header=0, index_col=None, engine='openpyxl')
    df_1_0_result = util.pyxl.ws_to_df(wb['1_0'], num_header=1, num_idx=0)

    df_1_1_expected = pd.read_excel(f, sheet_name='1_1', header=0, index_col=0, engine='openpyxl')
    df_1_1_result = util.pyxl.ws_to_df(wb['1_1'], num_header=1, num_idx=1)

    # pandas.read_excel must have a bug with header=None and index_col=0
    # because it's not returning the expected result, so creating expect result another way
    # df_0_1_expected = pd.read_excel(f, sheet_name='0_1', header=None, index_col=0, engine='openpyxl')
    df_0_1_expected = df_1_1_expected.copy()
    df_0_1_expected.columns = list(range(9))
    df_0_1_result = util.pyxl.ws_to_df(wb['0_1'], num_header=0, num_idx=1)

    df_2_1_expected = pd.read_excel(f, sheet_name='2_1', header=[0, 1], index_col=0, engine='openpyxl')
    df_2_1_result = util.pyxl.ws_to_df(wb['2_1'], num_header=2, num_idx=1)

    df_2_2_expected = pd.read_excel(f, sheet_name='2_2', header=[0, 1], index_col=[0, 1], engine='openpyxl')
    df_2_2_result = util.pyxl.ws_to_df(wb['2_2'], num_header=2, num_idx=2)

    util.testing.assert_dfs_equal(df_0_0_result, df_0_0_expected)
    util.testing.assert_dfs_equal(df_1_0_result, df_1_0_expected)
    util.testing.assert_dfs_equal(df_1_1_result, df_1_1_expected)
    util.testing.assert_dfs_equal(df_0_1_result, df_0_1_expected)
    util.testing.assert_dfs_equal(df_2_1_result, df_2_1_expected)
    util.testing.assert_dfs_equal(df_2_2_result, df_2_2_expected)
