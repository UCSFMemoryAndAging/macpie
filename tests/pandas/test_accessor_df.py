from datetime import datetime

import pandas as pd


def test_is_date_col():
    d = {
        'col1': [1, 2, 3],
        'col2': [4, '5', 6],
        'col3': [7, 8, 9],
        'date1': [datetime(2001, 3, 2), None, datetime(2001, 8, 1)],
        'date2': ['1/1/2001', '2/2/2002', '3/3/2003'],
        'misc': ['john', 'paul', 'mary'],
        'col6': [10, '11', 12]
    }
    df = pd.DataFrame(data=d)

    assert df.mac.is_date_col('col1') is False
    assert df.mac.is_date_col('date1') is True
    assert df.mac.is_date_col('date2') is False
