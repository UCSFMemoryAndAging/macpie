from datetime import datetime

import pandas as pd


def test_diff_rows_multiindex():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)
    df1.columns = pd.MultiIndex.from_product([["CDR"], df1.columns])

    d2 = {"col1": [1, 2, 3], "col3": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)
    df2.columns = pd.MultiIndex.from_product([["CDR"], df2.columns])

    result = df1.mac.diff_rows(
        df2,
        subset_pair_kwargs={"items": [("CDR", "col2")], "invert": True},
    )
    assert result.empty


def test_flatten_multiindex():
    d = {
        "PIDN": [2, 2, 3],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        "InstrID": [7, 8, 9],
    }
    df = pd.DataFrame(data=d)

    # test flattening row index
    df.index = pd.MultiIndex.from_product([["CDR"], df.index])
    df.mac.flatten_multiindex(axis=0)
    assert list(df.index) == ["CDR_0", "CDR_1", "CDR_2"]

    # test flattening col index
    df.columns = pd.MultiIndex.from_product([["CDR"], df.columns])
    df.mac.flatten_multiindex(axis=1)
    assert list(df.columns) == ["CDR_PIDN", "CDR_DCDate", "CDR_InstrID"]


def test_mimic_dtypes_mi():
    d1 = {
        "PIDN": [2, 2, 3],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        "InstrID": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1)
    df1.columns = pd.MultiIndex.from_product([["CDR"], df1.columns])

    d2 = {"PIDN": [2, 2, 3], "DCDate": ["3/2/2001", "2/1/2001", "8/1/2001"], "InstrID": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    df2.columns = pd.MultiIndex.from_product([["CDR"], df2.columns])

    assert df1[("CDR", "DCDate")].dtype != df2[("CDR", "DCDate")].dtype
    df2 = df1.mac.mimic_dtypes(df2)
    assert df1[("CDR", "DCDate")].dtype == df2[("CDR", "DCDate")].dtype


def test_mimic_index_order_mi():
    d1 = {
        "PIDN": [2, 2, 3],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        "InstrID": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1)
    df1.columns = pd.MultiIndex.from_product([["CDR"], df1.columns])
    df1.index = [1, 2, 3]

    d2 = {
        "PIDN": [2, 2, 3],
        "InstrID": [7, 8, 9],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
    }
    df2 = pd.DataFrame(data=d2)
    df2.columns = pd.MultiIndex.from_product([["CDR"], df2.columns])
    df2.index = [1, 3, 2]

    # test column axis
    result_df2 = df1.mac.mimic_index_order(df2, axis="columns")

    expected_d2 = {
        "PIDN": [2, 2, 3],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        "InstrID": [7, 8, 9],
    }
    expected_df2 = pd.DataFrame(data=expected_d2)
    expected_df2.columns = pd.MultiIndex.from_product([["CDR"], expected_df2.columns])
    expected_df2.index = [1, 3, 2]

    assert result_df2.equals(expected_df2)


def test_sort_values_pair():
    d1 = {
        "PIDN": [1, 2, 3],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        "InstrID": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1)
    df1.columns = pd.MultiIndex.from_product([["CDR"], df1.columns])

    d2 = {"PIDN": [1, 3, 2], "DCDate": ["3/2/2001", "8/1/2001", "2/1/2001"], "InstrID": [7, 9, 8]}
    df2 = pd.DataFrame(data=d2)
    df2.columns = pd.MultiIndex.from_product([["CDR"], df2.columns])

    expected_d2 = {
        "PIDN": [1, 2, 3],
        "DCDate": ["3/2/2001", "2/1/2001", "8/1/2001"],
        "InstrID": [7, 8, 9],
    }
    expected_df2 = pd.DataFrame(data=expected_d2)
    expected_df2.columns = pd.MultiIndex.from_product([["CDR"], expected_df2.columns])

    result_df1, result_df2 = df1.mac.sort_values_pair(df2, ignore_index=True)
    assert result_df1.equals(df1)
    assert result_df2.equals(expected_df2)
