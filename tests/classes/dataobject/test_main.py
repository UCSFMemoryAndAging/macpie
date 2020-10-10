from pathlib import Path

import pandas as pd
import pytest

from macpie.classes import DataObject


current_dir = Path("tests/classes/dataobject/")


def test_dataobject():
    d = {
        'col1': [1, 2, 3],
        'col2': [4, '5', 6],
        'col3': [7, 8, 9],
        'date': ['1/1/2001', '2/2/2002', '3/3/2003'],
        'misc': ['john', 'paul', 'mary'],
        'col6': [10, '11', 12]
    }
    df = pd.DataFrame(data=d)

    # no dataframe raises ValueError
    with pytest.raises(ValueError):
        do = DataObject(
            "test_name",
            None
        )

    # invalid id_col raises KeyError
    with pytest.raises(KeyError):
        do = DataObject(
            name="test_name",
            id_col="doesnt_exist",
            date_col="col3",
            df=df
        )

    # invalid id2_col raises KeyError
    with pytest.raises(KeyError):
        do = DataObject(
            name="test_name",
            id_col="COL1",
            date_col="col3",
            id2_col="doesnt_exist",
            df=df
        )

    # blank id_col is fine
    do = DataObject(
        name="test_name",
        date_col="col3",
        df=df
    )

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
