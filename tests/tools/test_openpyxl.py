from pathlib import Path

import openpyxl as pyxl
import pandas as pd

from macpie import openpyxltools


DATA_DIR = Path("tests/io/data/").resolve()

f = DATA_DIR / "multi_index.xlsx"
wb = pyxl.load_workbook(str(f))


def test():
    df_1_0_expected = pd.read_excel(f, sheet_name="1_0", header=0, index_col=None)
    # print("\n", df_1_0_expected, "\n", df_1_0_expected.index, "\n", df_1_0_expected.columns)
    df_1_0_result = openpyxltools.worksheet_to_dataframe(wb["1_0"], num_header=1, num_idx=0)
    # print("\n", df_1_0_result, "\n", df_1_0_result.index, "\n", df_1_0_result.columns)
    pd.testing.assert_frame_equal(df_1_0_result, df_1_0_expected)

    df_1_1_expected = pd.read_excel(f, sheet_name="1_1", header=0, index_col=0)
    # print("\n", df_1_1_expected, "\n", df_1_1_expected.index, "\n", df_1_1_expected.columns)
    df_1_1_result = openpyxltools.worksheet_to_dataframe(wb["1_1"], num_header=1, num_idx=1)
    # print("\n", df_1_1_result, "\n", df_1_1_result.index, "\n", df_1_1_result.columns)
    pd.testing.assert_frame_equal(df_1_1_result, df_1_1_expected)

    df_1_2_expected = pd.read_excel(f, sheet_name="1_2", header=0, index_col=[0, 1])
    # print("\n", df_1_2_expected, "\n", df_1_2_expected.index, "\n", df_1_2_expected.columns)
    df_1_2_result = openpyxltools.worksheet_to_dataframe(wb["1_2"], num_header=1, num_idx=2)
    # print("\n", df_1_2_result, "\n", df_1_2_result.index, "\n", df_1_2_result.columns)
    pd.testing.assert_frame_equal(df_1_2_result, df_1_2_expected)

    df_2_0_expected = pd.read_excel(f, sheet_name="2_0", header=[0, 1], index_col=None)
    # print("\n", df_2_0_expected, "\n", df_2_0_expected.index, "\n", df_2_0_expected.columns)
    df_2_0_result = openpyxltools.worksheet_to_dataframe(wb["2_0"], num_header=2, num_idx=0)
    # print("\n", df_2_0_result, "\n", df_2_0_result.index, "\n", df_2_0_result.columns)
    pd.testing.assert_frame_equal(df_2_0_result, df_2_0_expected)

    df_2_1_expected = pd.read_excel(f, sheet_name="2_1", header=[0, 1], index_col=0)
    # print("\n", df_2_1_expected, "\n", df_2_1_expected.index, "\n", df_2_1_expected.columns)
    df_2_1_result = openpyxltools.worksheet_to_dataframe(wb["2_1"], num_header=2, num_idx=1)
    # print("\n", df_2_1_result, "\n", df_2_1_result.index, "\n", df_2_1_result.columns)
    pd.testing.assert_frame_equal(df_2_1_result, df_2_1_expected)

    df_2_2_expected = pd.read_excel(f, sheet_name="2_2", header=[0, 1], index_col=[0, 1])
    # print("\n", df_2_2_expected, "\n", df_2_2_expected.index, "\n", df_2_2_expected.columns)
    df_2_2_result = openpyxltools.worksheet_to_dataframe(wb["2_2"], num_header=2, num_idx=2)
    # print("\n", df_2_2_result, "\n", df_2_2_result.index, "\n", df_2_2_result.columns)
    pd.testing.assert_frame_equal(df_2_2_result, df_2_2_expected)


def test_no_headers():
    # Note: DataFrames with no headers have integers auto-created for their column labels.

    df_0_0_expected = pd.read_excel(f, sheet_name="0_0", header=None, index_col=None)
    # print("\n", df_0_0_expected, "\n", df_0_0_expected.index, "\n", df_0_0_expected.columns)
    df_0_0_result = openpyxltools.worksheet_to_dataframe(wb["0_0"], num_header=0, num_idx=0)
    # print("\n", df_0_0_result, "\n", df_0_0_result.index, "\n", df_0_0_result.columns)
    pd.testing.assert_frame_equal(df_0_0_result, df_0_0_expected)

    df_0_1_expected = pd.read_excel(f, sheet_name="0_1", header=None, index_col=0)
    # print("\n", df_0_1_expected, "\n", df_0_1_expected.index, "\n", df_0_1_expected.columns)
    df_0_1_result = openpyxltools.worksheet_to_dataframe(wb["0_1"], num_header=0, num_idx=1)
    # print("\n", df_0_1_result, "\n", df_0_1_result.index, "\n", df_0_1_result.columns)
    pd.testing.assert_frame_equal(df_0_1_result, df_0_1_expected)

    df_0_2_expected = pd.read_excel(f, sheet_name="0_2", header=None, index_col=[0, 1])
    # print("\n", df_0_2_expected, "\n", df_0_2_expected.index, "\n", df_0_2_expected.columns)
    df_0_2_result = openpyxltools.worksheet_to_dataframe(wb["0_2"], num_header=0, num_idx=2)
    # print("\n", df_0_2_result, "\n", df_0_2_result.index, "\n", df_0_2_result.columns)
    pd.testing.assert_frame_equal(df_0_2_expected, df_0_2_expected)
