import pandas as pd

import macpie as mp


def test_keep_cols():

    data = [[1, 4, 7, "1/1/2001", 1], [2, "5", 8, "2/2/2002", 2], [3, 6, 9, "3/3/2003", 3]]

    columns = ["col1", "col2", "col3", "date", "ids"]
    mi_columns = pd.MultiIndex.from_product([["level"], columns])

    df = pd.DataFrame(data, columns=columns)
    mi_df = pd.DataFrame(data=data, columns=mi_columns)

    mi_dset = mp.Dataset(
        mi_df, id_col_name=("level", "ids"), date_col_name=("level", "date"), name="mi_test_name"
    )

    assert len(mi_dset.columns) == 5

    mi_dset.keep_cols([("level", "ids")], inplace=False)

    assert len(mi_dset.columns) == 5

    mi_dset.keep_cols([("level", "ids")], inplace=True)

    assert len(mi_dset.columns) == 2


def test_prepend_level():

    data = [[1, 4, 7, "1/1/2001", 1], [2, "5", 8, "2/2/2002", 2], [3, 6, 9, "3/3/2003", 3]]

    columns = ["col1", "col2", "col3", "date", "ids"]

    df = pd.DataFrame(data, columns=columns)

    dset = mp.Dataset(df, id_col_name="ids", date_col_name="date")

    new_dset = dset.prepend_level("level")

    assert new_dset.columns.nlevels == 2

    dset.prepend_level("level", inplace=True)

    assert dset.columns.nlevels == 2


def test_rename_col():

    data = [[1, 4, 7, "1/1/2001", 1], [2, "5", 8, "2/2/2002", 2], [3, 6, 9, "3/3/2003", 3]]

    columns = ["col1", "col2", "col3", "date", "ids"]

    df = pd.DataFrame(data, columns=columns)

    dset = mp.Dataset(df, id_col_name="ids", date_col_name="date")

    new_dset = dset.prepend_level("level")

    assert new_dset.columns.nlevels == 2

    dset.prepend_level("level", inplace=True)

    assert dset.columns.nlevels == 2
