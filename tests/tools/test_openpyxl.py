from pathlib import Path

import openpyxl as pyxl
import pandas as pd
from pandas._testing import assert_frame_equal

from macpie import openpyxltools

data_dir = Path("tests/data/").resolve()
io_data_dir = Path("tests/io/data/").resolve()

f = io_data_dir / "multi_index.xlsx"
wb = pyxl.load_workbook(str(f), read_only=True, data_only=True)


def test():
    df_1_0_expected = pd.read_excel(f, sheet_name="1_0", header=0, index_col=None)
    # print("\n", df_1_0_expected, "\n", df_1_0_expected.index, "\n", df_1_0_expected.columns)
    df_1_0_result = openpyxltools.to_df(wb["1_0"], num_header=1, num_idx=0)
    # print("\n", df_1_0_result, "\n", df_1_0_result.index, "\n", df_1_0_result.columns)
    assert_frame_equal(df_1_0_result, df_1_0_expected)

    df_1_1_expected = pd.read_excel(f, sheet_name="1_1", header=0, index_col=0)
    # print("\n", df_1_1_expected, "\n", df_1_1_expected.index, "\n", df_1_1_expected.columns)
    df_1_1_result = openpyxltools.to_df(wb["1_1"], num_header=1, num_idx=1)
    # print("\n", df_1_1_result, "\n", df_1_1_result.index, "\n", df_1_1_result.columns)
    assert_frame_equal(df_1_1_result, df_1_1_expected)

    df_1_2_expected = pd.read_excel(f, sheet_name="1_2", header=0, index_col=[0, 1])
    # print("\n", df_1_2_expected, "\n", df_1_2_expected.index, "\n", df_1_2_expected.columns)
    df_1_2_result = openpyxltools.to_df(wb["1_2"], num_header=1, num_idx=2)
    # print("\n", df_1_2_result, "\n", df_1_2_result.index, "\n", df_1_2_result.columns)
    assert_frame_equal(df_1_2_result, df_1_2_expected)

    df_2_0_expected = pd.read_excel(f, sheet_name="2_0", header=[0, 1], index_col=None)
    # print("\n", df_2_0_expected, "\n", df_2_0_expected.index, "\n", df_2_0_expected.columns)
    df_2_0_result = openpyxltools.to_df(wb["2_0"], num_header=2, num_idx=0)
    # print("\n", df_2_0_result, "\n", df_2_0_result.index, "\n", df_2_0_result.columns)
    assert_frame_equal(df_2_0_result, df_2_0_expected)

    df_2_1_expected = pd.read_excel(f, sheet_name="2_1", header=[0, 1], index_col=0)
    # print("\n", df_2_1_expected, "\n", df_2_1_expected.index, "\n", df_2_1_expected.columns)
    df_2_1_result = openpyxltools.to_df(wb["2_1"], num_header=2, num_idx=1)
    # print("\n", df_2_1_result, "\n", df_2_1_result.index, "\n", df_2_1_result.columns)
    assert_frame_equal(df_2_1_result, df_2_1_expected)

    df_2_2_expected = pd.read_excel(f, sheet_name="2_2", header=[0, 1], index_col=[0, 1])
    # print("\n", df_2_2_expected, "\n", df_2_2_expected.index, "\n", df_2_2_expected.columns)
    df_2_2_result = openpyxltools.to_df(wb["2_2"], num_header=2, num_idx=2)
    # print("\n", df_2_2_result, "\n", df_2_2_result.index, "\n", df_2_2_result.columns)
    assert_frame_equal(df_2_2_result, df_2_2_expected)


def test_no_headers():
    # DataFrames with no headers have integers auto-created for their column labels.
    # Since the column labels are integers and not strings, we can't use
    # assert_dfs_equal to compare because it uses the .str accessor, which can only
    # be used with strings values. Therefore, use the natiive pandas equals method
    # to do the assertion check.

    df_0_0_expected = pd.read_excel(f, sheet_name="0_0", header=None, index_col=None)
    # print("\n", df_0_0_expected, "\n", df_0_0_expected.index, "\n", df_0_0_expected.columns)
    df_0_0_result = openpyxltools.to_df(wb["0_0"], num_header=0, num_idx=0)
    # print("\n", df_0_0_result, "\n", df_0_0_result.index, "\n", df_0_0_result.columns)
    assert_frame_equal(df_0_0_result, df_0_0_expected)

    df_0_1_expected = pd.read_excel(f, sheet_name="0_1", header=None, index_col=0)
    # print("\n", df_0_1_expected, "\n", df_0_1_expected.index, "\n", df_0_1_expected.columns)
    df_0_1_result = openpyxltools.to_df(wb["0_1"], num_header=0, num_idx=1)
    # print("\n", df_0_1_result, "\n", df_0_1_result.index, "\n", df_0_1_result.columns)
    assert_frame_equal(df_0_1_result, df_0_1_expected)

    df_0_2_expected = pd.read_excel(f, sheet_name="0_2", header=None, index_col=[0, 1])
    # print("\n", df_0_2_expected, "\n", df_0_2_expected.index, "\n", df_0_2_expected.columns)
    df_0_2_result = openpyxltools.to_df(wb["0_2"], num_header=0, num_idx=2)
    # print("\n", df_0_2_result, "\n", df_0_2_result.index, "\n", df_0_2_result.columns)
    assert_frame_equal(df_0_2_expected, df_0_2_expected)
