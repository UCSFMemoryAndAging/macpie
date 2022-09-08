from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import macpie as mp


THIS_DIR = Path(__file__).parent.absolute()


def test_add_diff_days():
    d = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [datetime(2002, 3, 2), datetime(2001, 3, 1), datetime(2001, 8, 2)],
    }
    df = pd.DataFrame(data=d)

    with pytest.raises(KeyError):
        df.mac.add_diff_days("col2", "col2")

    df = df.mac.add_diff_days("col2", "col3")

    assert mp.get_option("column.system.diff_days") in df.columns
    assert df[mp.get_option("column.system.diff_days")].equals(pd.Series([365.0, 28.0, 1.0]))


def test_any_duplicates():
    d = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [datetime(2002, 3, 2), datetime(2001, 3, 1), datetime(2001, 8, 2)],
    }
    df = pd.DataFrame(data=d)

    # no col4 column raises KeyError
    with pytest.raises(KeyError):
        df.mac.any_duplicates("col4")

    d = {
        mp.get_option("column.system.duplicates"): [False, False, False],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [datetime(2002, 3, 2), datetime(2001, 3, 1), datetime(2001, 8, 2)],
    }
    df = pd.DataFrame(data=d)

    assert not df[mp.get_option("column.system.duplicates")].any()

    d = {
        mp.get_option("column.system.duplicates"): [True, False, False],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [datetime(2002, 3, 2), datetime(2001, 3, 1), datetime(2001, 8, 2)],
    }
    df = pd.DataFrame(data=d)

    assert df.mac.any_duplicates(mp.get_option("column.system.duplicates"))

    d = {"col1": ["a", "b", "c"], "col2": [None, None, 6], "col3": [np.nan, np.nan, 8]}
    df = pd.DataFrame(data=d)

    # nulls by default count as duplicates
    assert df.mac.any_duplicates("col2")
    assert df.mac.any_duplicates("col3")

    # don't count nulls as duplicates
    assert not df.mac.any_duplicates("col2", ignore_nan=True)
    assert not df.mac.any_duplicates("col3", ignore_nan=True)


def test_count_trailers():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    with pytest.raises(ValueError):
        mp.pandas.count_trailers(ser1, count_na=False, count_empty_string=False)

    assert ser1.mac.count_trailers(count_empty_string=False) == 2

    assert ser1.mac.count_trailers() == 3

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])

    assert ser2.mac.count_trailers() == 1

    assert ser2.mac.count_trailers(predicates=lambda x: x == 4) == 3


def test_is_date_col():
    d = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date1": [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        "date2": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df = pd.DataFrame(data=d)

    assert df.mac.is_date_col("col1") is False
    assert df.mac.is_date_col("date1") is True
    assert df.mac.is_date_col("date2") is False
