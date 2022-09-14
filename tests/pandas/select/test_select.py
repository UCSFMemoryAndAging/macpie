import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import macpie as mp


THIS_DIR = Path(__file__).parent.absolute()


def test_filter_labels():
    d = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df = pd.DataFrame(data=d)
    assert df.mac.filter_labels(items=["col7"]) == []
    assert df.mac.filter_labels(items=["col7"], invert=True) == [
        "col1",
        "col2",
        "col3",
        "date",
        "misc",
        "col6",
    ]
    assert df.mac.filter_labels(regex="^albert") == []
    assert df.mac.filter_labels(items=["col7"], regex="^albert") == []
    assert df.mac.filter_labels(items=["col2", "col1"]) == ["col1", "col2"]
    assert df.mac.filter_labels(items=["col1", "col2"], invert=True) == [
        "col3",
        "date",
        "misc",
        "col6",
    ]
    assert df.mac.filter_labels(like="ol") == ["col1", "col2", "col3", "col6"]
    assert df.mac.filter_labels(like="ol", invert=True) == ["date", "misc"]
    assert df.mac.filter_labels(regex="^da") == ["date"]
    assert df.mac.filter_labels(regex="^col", invert=True) == ["date", "misc"]
    assert df.mac.filter_labels(like="ol", regex="^da") == ["col1", "col2", "col3", "date", "col6"]
    assert df.mac.filter_labels(items=["col1", "misc"], like="ol", regex="^da") == [
        "col1",
        "col2",
        "col3",
        "date",
        "misc",
        "col6",
    ]


def test_filter_labels_mi():
    d = {
        "PIDN": [2, 2, 3],
        "DCDate": [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        "InstrID": [7, 8, 9],
    }
    df = pd.DataFrame(data=d)
    df.columns = pd.MultiIndex.from_product([["CDR"], df.columns])

    assert df.mac.filter_labels(items=[("CDR", "PIDN")]) == [("CDR", "PIDN")]
    assert df.mac.filter_labels(items=[("CDR", "PIDN")], result_level=1) == ["PIDN"]
    assert df.mac.filter_labels(regex=re.compile("cdr", re.IGNORECASE), filter_level=0) == [
        ("CDR", "PIDN"),
        ("CDR", "DCDate"),
        ("CDR", "InstrID"),
    ]
    assert df.mac.filter_labels(regex=re.compile("cdr", re.IGNORECASE), filter_level=1) == []
    assert df.mac.filter_labels(regex=re.compile("id", re.IGNORECASE)) == [
        ("CDR", "PIDN"),
        ("CDR", "InstrID"),
    ]
    assert df.mac.filter_labels(regex=re.compile("id", re.IGNORECASE), invert=True) == [
        ("CDR", "DCDate")
    ]
    assert df.mac.filter_labels(regex=re.compile("id$", re.IGNORECASE)) == [("CDR", "InstrID")]


def test_filter_labels_pair():
    d1 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc1": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc2": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df2 = pd.DataFrame(data=d2)

    assert df1.mac.filter_labels_pair(df2, intersection=True) == (
        (["col1", "col2", "col3", "date", "col6"], ["col1", "col2", "col3", "date", "col6"]),
        (["misc1"], ["misc2"]),
    )

    assert df1.mac.filter_labels_pair(df2, left_filter_seq_kwargs={"like": "col"}) == (
        (["col1", "col2", "col3", "col6"], ["col1", "col2", "col3", "date", "misc2", "col6"]),
        (["date", "misc1"], []),
    )

    assert df1.mac.filter_labels_pair(df2, regex="^col", invert=True) == (
        (["date", "misc1"], ["date", "misc2"]),
        (["col1", "col2", "col3", "col6"], ["col1", "col2", "col3", "col6"]),
    )

    assert df1.mac.filter_labels_pair(df2, regex="^col", invert=True, intersection=True) == (
        (["date"], ["date"]),
        (["col1", "col2", "col3", "misc1", "col6"], ["col1", "col2", "col3", "misc2", "col6"]),
    )


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


def test_remove_trailers():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    with pytest.raises(ValueError):
        mp.pandas.remove_trailers(ser1, remove_na=False, remove_empty_string=False)

    expected = pd.Series([1, "2", 3, ""])
    assert ser1.mac.remove_trailers(remove_empty_string=False).equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser1.mac.remove_trailers().equals(expected)

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])

    expected = pd.Series([1, "2", 3, None, 4])
    assert ser2.mac.remove_trailers().equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser2.mac.remove_trailers(predicates=lambda x: x == 4).equals(expected)


def test_rtrim():
    ser1 = pd.Series([1, "2", 3, "", None, np.nan])

    expected = pd.Series([1, "2", 3, ""])
    assert ser1.mac.rtrim(trim_empty_string=False).equals(expected)

    expected = pd.Series([1, "2", 3])
    assert ser1.mac.rtrim(trim_empty_string=True).equals(expected)

    ser2 = pd.Series([1, "2", 3, None, 4, np.nan])

    expected = pd.Series([1, "2", 3, None, 4])
    assert ser2.mac.rtrim().equals(expected)


def test_subset():
    d1 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc1": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df1 = pd.DataFrame(data=d1, index=["zero", "one", "two"])

    d2 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc2": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df2 = pd.DataFrame(data=d2, index=["one", "two", "three"])

    expected_df1 = df1.drop(columns=["col1", "col2", "col3"])
    expected_df2 = df2.drop(columns=["col1", "col2", "col3"])

    results = list(mp.pandas.subset(df1, df2, items=["col1", "col2", "col3"]))

    assert results[0].equals(expected_df1)
    assert results[1].equals(expected_df2)


def test_subset_pair():
    d1 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc1": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df1 = pd.DataFrame(data=d1, index=["zero", "one", "two"])

    d2 = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "misc2": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
    }
    df2 = pd.DataFrame(data=d2, index=["one", "two", "three"])

    expected_df1 = df1.drop(columns="misc1")
    expected_df2 = df2.drop(columns="misc2")
    result_df1, result_df2 = df1.mac.subset_pair(df2, axis=1, intersection=True)
    assert result_df1.equals(expected_df1)
    assert result_df2.equals(expected_df2)
