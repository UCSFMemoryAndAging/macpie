import dateutil
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest


THIS_DIR = Path(__file__).parent.absolute()


def test_mimic_dtypes():
    d1 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [7, 8, 9],
        "col4": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "col1": ["a", "b", "c"],
        "col3": ["7", "8", "9"],
        "col2": ["3/2/2001", "2/1/2001", "8/1/2001"],
    }
    df2 = pd.DataFrame(data=d2)

    assert df1["col2"].dtype != df2["col2"].dtype
    assert df1["col3"].dtype != df2["col3"].dtype

    df2 = df1.mac.mimic_dtypes(df2)

    assert df1["col2"].dtype == df2["col2"].dtype
    assert df1["col3"].dtype == df2["col3"].dtype


def test_mimic_index_order():
    d1 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [7, 8, 9],
        "col4": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1, index=[1, 2, 3])

    d2 = {
        "col1": ["a", "b", "c"],
        "col3": ["7", "8", "9"],
        "col2": ["3/2/2001", "2/1/2001", "8/1/2001"],
    }
    df2 = pd.DataFrame(data=d2, index=[1, 3, 2])

    # test column axis
    result_df2 = df1.mac.mimic_index_order(df2, axis="columns")

    expected_d2 = {
        "col1": ["a", "b", "c"],
        "col2": ["3/2/2001", "2/1/2001", "8/1/2001"],
        "col3": ["7", "8", "9"],
    }
    expected_df2 = pd.DataFrame(data=expected_d2, index=[1, 3, 2])

    assert result_df2.equals(expected_df2)

    # test row axis
    result_df2 = df1.mac.mimic_index_order(df2, axis="index")

    expected_d2 = {
        "col1": ["a", "c", "b"],
        "col3": ["7", "9", "8"],
        "col2": ["3/2/2001", "8/1/2001", "2/1/2001"],
    }
    expected_df2 = pd.DataFrame(data=expected_d2, index=[1, 2, 3])

    assert result_df2.equals(expected_df2)


def test_to_datetime():
    d1 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), "asdf"],
        "col3": [True, True, False],
        "col4": [7, 8, 9],
        "col5": [datetime(3100, 3, 2), datetime(2001, 2, 1), datetime(2001, 2, 1)],
    }
    df1 = pd.DataFrame(data=d1)

    with pytest.raises(KeyError):
        df1.mac.to_datetime("doesnt_exit")

    with pytest.raises(ValueError):
        df1.mac.to_datetime("col1")

    # bool's not convertible due to invalid type
    with pytest.raises(TypeError):
        df1.mac.to_datetime("col3")

    # 'asdf' in col2 should generate ParserError
    with pytest.raises(dateutil.parser.ParserError):
        df1.mac.to_datetime("col2")

    # date is out of bounds
    with pytest.raises(pd.errors.OutOfBoundsDatetime):
        df1.mac.to_datetime("col5")
