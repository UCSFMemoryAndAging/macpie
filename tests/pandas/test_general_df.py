from datetime import datetime

import dateutil
import numpy as np
import pandas as pd
import pytest

from macpie._config import get_option


def test_equals():
    d1 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [7, 8, 9],
        "col4": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "col1": ["a", "b", "c"],
        "col2": ["3/2/2001", "2/1/2001", "8/1/2001"],
        "col3": ["7", "8", "9"],
    }
    df2 = pd.DataFrame(data=d2)

    assert df1.mac.equals(df2, cols_ignore=["col4"])


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

    assert get_option("column.system.diff_days") in df.columns
    assert df[get_option("column.system.diff_days")].equals(pd.Series([365.0, 28.0, 1.0]))


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
        get_option("column.system.duplicates"): [False, False, False],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [datetime(2002, 3, 2), datetime(2001, 3, 1), datetime(2001, 8, 2)],
    }
    df = pd.DataFrame(data=d)

    assert not df[get_option("column.system.duplicates")].any()

    d = {
        get_option("column.system.duplicates"): [True, False, False],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [datetime(2002, 3, 2), datetime(2001, 3, 1), datetime(2001, 8, 2)],
    }
    df = pd.DataFrame(data=d)

    assert df.mac.any_duplicates(get_option("column.system.duplicates"))

    d = {"col1": ["a", "b", "c"], "col2": [None, None, 6], "col3": [np.nan, np.nan, 8]}
    df = pd.DataFrame(data=d)

    # nulls by default count as duplicates
    assert df.mac.any_duplicates("col2")
    assert df.mac.any_duplicates("col3")

    # don't count nulls as duplicates
    assert not df.mac.any_duplicates("col2", ignore_nan=True)
    assert not df.mac.any_duplicates("col3", ignore_nan=True)


def test_assimilate():
    d1 = {
        "col1": ["a", "b", "c"],
        "col2": [datetime(2001, 3, 2), datetime(2001, 2, 1), datetime(2001, 8, 1)],
        "col3": [7, 8, 9],
        "col4": [7, 8, 9],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "col1": ["a", "b", "c"],
        "col2": ["3/2/2001", "2/1/2001", "8/1/2001"],
        "col3": ["7", "8", "9"],
    }
    df2 = pd.DataFrame(data=d2)

    assert df1["col2"].dtype != df2["col2"].dtype
    assert df1["col3"].dtype != df2["col3"].dtype

    df2 = df1.mac.assimilate(df2)

    assert df1["col2"].dtype == df2["col2"].dtype
    assert df1["col3"].dtype == df2["col3"].dtype


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

    assert set() == left_only_cols
    assert set() == right_only_cols


def test_diff_cols_different():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2)

    assert {"col2", "col3"} == left_only_cols
    assert {"col4"} == right_only_cols


def test_diff_cols_ignore():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    ignore_cols = ["col2", "col3", "col4"]
    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2, ignore_cols)
    assert set() == left_only_cols
    assert set() == right_only_cols

    ignore_cols = ["col2"]
    (left_only_cols, right_only_cols) = df1.mac.diff_cols(df2, ignore_cols)
    assert {"col3"} == left_only_cols
    assert {"col4"} == right_only_cols


def test_diff_rows():
    d1 = {"col1": [1, 2, 3], "col2": [4, "5", 6], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    with pytest.raises(KeyError):
        df1.mac.diff_rows(df2)


def test_diff_rows_2():
    # same number of columns but different columns
    d1 = {"col1": [1, 2, 3], "col3": [7, 8, 9]}
    df1 = pd.DataFrame(data=d1)

    d2 = {"col1": [1, 2, 3], "col4": [7, 8, 9]}
    df2 = pd.DataFrame(data=d2)

    with pytest.raises(KeyError):
        df1.mac.diff_rows(df2)


def test_get_col_name():
    d = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df = pd.DataFrame(data=d)

    assert df.mac.get_col_name("col1") == "col1"
    assert df.mac.get_col_name("COL1") == "col1"

    with pytest.raises(KeyError):
        df.mac.get_col_name("colZZZ")

    with pytest.raises(KeyError):
        df.mac.get_col_name(None)


def test_get_cols_by_prefixes():
    d = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df = pd.DataFrame(data=d)

    result = df.mac.get_cols_by_prefixes("col1")
    assert result["col1"][0].equals(df["col1"])

    result = df.mac.get_cols_by_prefixes(["col1"])
    assert result["col1"][0].equals(df["col1"])

    result = df.mac.get_cols_by_prefixes(["col1", "col2"])
    assert len(result) == 2
    assert result["col1"][0].equals(df["col1"])
    assert result["col2"][0].equals(df["col2"])

    with pytest.raises(KeyError):
        result = df.mac.get_cols_by_prefixes("col")

    result = df.mac.get_cols_by_prefixes("col", one_match_only=False)
    assert len(result) == 1
    assert len(result["col"]) == 4
    assert result["col"][0].equals(df["col1"])
    assert result["col"][3].equals(df["col6"])

    # modifying original dataframe should not affect the result
    df["col6"] = df["col6"].replace(["11"], 18)
    assert not result["col"][3].equals(df["col6"])


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
