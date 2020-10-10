from datetime import datetime

import pandas as pd
import pytest


def test_keep():

    d = {
        'PIDN': [1, 2, 3],
        'DCDate': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'Col3': [7, 8, 9]
    }
    df = pd.DataFrame(data=d)

    # invalid keep option should raise error
    with pytest.raises(ValueError):
        df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='hello')


def test_id_col_1():

    d = {
        'PIDN': [1, 2, 3],
        'DCDate': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'Col3': [7, 8, 9]
    }
    df = pd.DataFrame(data=d)

    # invalid id_col column should raise KeyError error
    with pytest.raises(KeyError):
        df.mac.group_by_keep_one(
            group_by_col='pidn',
            date_col='dcdate',
            id_col='instrid',
            keep='all'
        )


def test_id_col_2():

    d = {
        'PIDN': [2, 2, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'InstrID': [7, 8, 9]
    }
    df = pd.DataFrame(data=d)

    result = df.mac.group_by_keep_one(
        group_by_col='pidn',
        date_col='dcdate',
        id_col='instrid',
        keep='all'
    )

    assert df.equals(result)

    result = df.mac.group_by_keep_one(
        group_by_col='pidn',
        date_col='dcdate',
        id_col='instrid',
        keep='all',
        drop_duplicates=True
    )

    assert df.equals(result)

    result = df.mac.group_by_keep_one(
        group_by_col='pidn',
        date_col='dcdate',
        keep='all',
        drop_duplicates=True
    )

    assert result.mac.num_rows() == 2


def test_2():

    d = {
        'PIDN': [1, 2, 3],
        'DCDate': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'Col3': [7, 8, 9]
    }
    df = pd.DataFrame(data=d)

    # 'all' should return sorted df with rows containing a NaT date removed

    result = df.mac.group_by_keep_one(group_by_col='pidn', date_col='dcdate', keep='all')

    expected_result_dict = {
        'PIDN': [1, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'Col3': [7, 9]
    }
    expected_result = pd.DataFrame(data=expected_result_dict)

    assert result.equals(expected_result)
