from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from macpie import errors
from macpie.core import DataObject


current_dir = Path("tests/core/dataobject/").resolve()


def test_dataobject():
    d = {
        'col1': [1, 2, 3],
        'col2': [4, '5', 6],
        'col3': [7, 8, 9],
        'date': ['1/1/2001', '2/2/2002', '3/3/2003'],
        'misc': ['john', 'paul', 'mary'],
        'col6': [10, '11', 12],
        'id_col': [1, 1, 3],
        'id_col_with_nan': [np.nan, np.nan, 3],
        'id_col_with_none': [None, None, 3],
    }
    df = pd.DataFrame(data=d)

    # no dataframe raises ValueError
    with pytest.raises(ValueError):
        do = DataObject(
            "test_name",
            None
        )

    # invalid id_col raises KeyError
    with pytest.raises(errors.DataObjectIDColKeyError):
        do = DataObject(
            name="test_name",
            id_col="doesnt_exist",
            date_col="col3",
            df=df
        )

    # duplicate ids raises DataObjectIDColDuplicateKeyError
    with pytest.raises(errors.DataObjectIDColDuplicateKeyError):
        do = DataObject(
            name="test_name",
            id_col="id_col",
            date_col="col3",
            df=df
        )

    # invalid id2_col raises KeyError
    with pytest.raises(errors.DataObjectID2ColKeyError):
        do = DataObject(
            name="test_name",
            id_col="COL1",
            date_col="col3",
            id2_col="doesnt_exist",
            df=df
        )

    # id_col with nan values raises KeyError
    with pytest.raises(errors.DataObjectIDColKeyError):
        do = DataObject(
            name="test_name",
            id_col="id_col_with_nan",
            date_col="col3",
            df=df
        )

    # id_col with None values raises KeyError
    with pytest.raises(errors.DataObjectIDColKeyError):
        do = DataObject(
            name="test_name",
            id_col="id_col_with_none",
            date_col="col3",
            df=df
        )

    # blank id_col creates an id_col called 'mp_id_col' with index starting from 1
    do = DataObject(
        name="test_name",
        date_col="col3",
        df=df
    )
    assert do.id_col == 'mp_id_col'
    assert do.df[do.id_col].equals(pd.Series([1, 2, 3]))

    # blank id_col AND blank date_col
    # creates an id_col called 'mp_id_col' with index starting from 1
    do = DataObject(
        name="test_name",
        df=df
    )
    assert do.id_col == 'mp_id_col'
    assert do.df[do.id_col].equals(pd.Series([1, 2, 3]))

    # dataframe lacks date column but created without error
    do = DataObject(
        name="test_name",
        id_col="COL1",
        df=df
    )
    # id_col is converted to the correct case (in dataframe)
    assert do.id_col == "col1"

    # dataframe with date_col created without error
    do = DataObject(
        name="test_name",
        id_col="COL1",
        date_col="col3",
        df=df
    )

    assert do.df.mac.is_date_col(do.date_col) is True

    # original dataframe is same as current df
    assert do.df.equals(do.df_orig)

    assert repr(do) == "DataObject(name='test_name', id_col='col1', date_col='col3', id2_col=None)"


def test_localdataobject():

    # dataframe lacks date column but created without error
    p = current_dir / "basic.csv"

    do = DataObject.from_file(p, "test_name", id_col="misc")
    assert do.name == "test_name"

    do = DataObject.from_file(p, "test_name", id_col="misc", date_col="date")
    assert do.name == "test_name"
