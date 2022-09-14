from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest


THIS_DIR = Path(__file__).parent.absolute()


def test_compare():
    d1 = {"col1": [1, 2, 3], "col2": [4, 5, 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col3": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)
    assert df1.mac.compare(df2, subset_pair_kwargs={"items": ["col2"], "invert": True}).empty


def test_diff_cols_equality():
    d1 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df2 = pd.DataFrame(data=d2)

    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2)

    assert [] == left_only_cols
    assert [] == right_only_cols


def test_diff_cols_different():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2)

    assert ["col2", "col3"] == left_only_cols
    assert ["col4"] == right_only_cols


def test_diff_cols_ignore():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    filter_kwargs = {"items": ["col2", "col3", "col4"], "invert": True}
    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2, filter_kwargs)
    assert [] == left_only_cols
    assert [] == right_only_cols

    filter_kwargs = {"items": ["col2"], "invert": True}
    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2, filter_kwargs)
    assert ["col3"] == left_only_cols
    assert ["col4"] == right_only_cols


def test_diff_rows():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    with pytest.raises(KeyError):
        df1.mac.diff_rows(df2)

    # same number of columns but different columns
    d1 = {"col1": [1, 2, 3], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    with pytest.raises(KeyError):
        df1.mac.diff_rows(df2)


def test_diff_rows_2():
    d1 = {"col1": [1, 2, 3], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 4], "col3": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    expected_data = {
        "col1": [3, 4],
        "col3": [9, 9],
        "_mp_diff_rows_merge": ["left_only", "right_only"],
    }
    expected_result = pd.DataFrame(data=expected_data, index=[2, 3])

    result = df1.mac.diff_rows(df2)
    assert result.compare(expected_result).empty


def test_equals():
    d1 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [7, 8, 9],
        "col4": [4, 5, 6],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [7, 8, 9],
        "col4": [7, 8, 9],
    }
    df2 = pd.DataFrame(data=d2)

    assert df1.mac.equals(df2, subset_pair_kwargs={"items": ["col4"], "invert": True})
