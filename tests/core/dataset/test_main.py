from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from macpie import Dataset
from macpie.exceptions import (
    DatasetIDColError,
    DatasetDateColError,
    DatasetID2ColError
)

current_dir = Path("tests/core/dataset/").resolve()


def test_dataset():
    d = {
        'col1': [1, 2, 3],
        'col2': [4, '5', 6],
        'col3': [7, 8, 9],
        'date': ['1/1/2001', '2/2/2002', '3/3/2003'],
        'date_bad': ['bad_date', '2/2/2002', '3/3/2003'],
        'misc': ['john', 'paul', 'mary'],
        'col6': [10, '11', 12],
        'id_col': [1, 2, 3],
        'id_col_with_dups': [1, 1, 3],
        'id_col_with_nan': [np.nan, np.nan, 3],
        'id_col_with_none': [None, None, 3],
    }
    df = pd.DataFrame(data=d)

    # no dataframe raises ValueError
    with pytest.raises(ValueError):
        dset = Dataset(
            None,
            name="test_name"
        )

    # invalid id_col raises DatasetIDColError
    with pytest.raises(DatasetIDColError):
        dset = Dataset(
            df,
            id_col="doesnt_exist",
            date_col="col3",
            name="test_name"
        )

    # duplicate ids raises DatasetIDColDuplicateError
    # TODO: Determine whether Datsets should allow duplicate IDs
    # When doing a date_proximity join, duplicate IDs can definitely
    # be created when the primary dataset has records that match the
    # same secondary record.
    """
    with pytest.raises(DatasetIDColDuplicateError):
        dset = Dataset(
            df,
            id_col="id_col_with_dups",
            date_col="col3",
            name="test_name"
        )
    """

    # id_col with nan values raises DatasetIDColError
    # TODO: Determine whether Datasets should allow nan IDs
    """
    with pytest.raises(DatasetIDColError):
       dset = Dataset(
           df,
           id_col="id_col_with_nan",
           date_col="col3",
           name="test_name"
       )
    """

    # id_col with None values raises DatasetIDColError
    # TODO: Determine whether Datasets should allow null IDs
    """
    with pytest.raises(DatasetIDColError):
        dset = Dataset(
            df,
            id_col="id_col_with_none",
            date_col="col3",
            name="test_name"
        )
    """

    # invalid date_col raises KeyError
    with pytest.raises(DatasetDateColError):
        dset = Dataset(
            df,
            id_col="id_col",
            date_col="date_bad",
            id2_col="col2",
            name="test_name"
        )

    # dataframe with date_col created without error
    dset = Dataset(
        df,
        id_col="COL1",
        date_col="col3",
        name="test_name"
    )
    assert dset.df.mac.is_date_col(dset.date_col) is True

    # original dataframe is same as current df
    assert dset.df.equals(dset.df_orig)
    assert repr(dset) == "Dataset(name='test_name', id_col='col1', date_col='col3', id2_col=None, tags=[])"

    # invalid id2_col raises DatasetID2ColError
    with pytest.raises(DatasetID2ColError):
        dset = Dataset(
            df,
            id_col="COL1",
            date_col="col3",
            id2_col="doesnt_exist",
            name="test_name"
        )

    # dataset lacks id_col, date_col, id2_col but created without error
    dset = Dataset(
        df.copy()
    )
    assert dset.df.equals(df)

    # create_id_col creates id_col if none exists
    dset.create_id_col()
    assert dset.id_col == 'mp_id_col'

    # now that id_col exists, trying to create another should raise error
    with pytest.raises(ValueError):
        dset.create_id_col()

    # dataset lacks date_col but created without error
    dset = Dataset(
        df,
        id_col="COL1",
        name="test_name"
    )
    # id_col is converted to the correct case (in dataframe)
    assert dset.id_col == "col1"


def test_dataset_from_file():

    # dataframe lacks date column but created without error
    p = current_dir / "basic.csv"

    dset = Dataset.from_file(p, id_col="misc", name="test_name")
    assert dset.name == "test_name"

    dset = Dataset.from_file(p, id_col="misc", date_col="date", name="test_name")
    assert dset.name == "test_name"
