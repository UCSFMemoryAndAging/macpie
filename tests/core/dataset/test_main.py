from pathlib import Path

import dateutil
import numpy as np
import pytest

import macpie as mp

from tests.data.data import primary_data


DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path(__file__).parent.absolute()


def test_dataset():
    data = {
        "col1": [1, 2, 3],
        "col2": [4, "5", 6],
        "col3": [7, 8, 9],
        "date": ["1/1/2001", "2/2/2002", "3/3/2003"],
        "date_bad": ["bad_date", "2/2/2002", "3/3/2003"],
        "misc": ["john", "paul", "mary"],
        "col6": [10, "11", 12],
        "ids": [1, 2, 3],
        "id_col_with_dups": [1, 1, 3],
        "id_col_with_nan": [np.nan, np.nan, 3],
        "id_col_with_none": [None, None, 3],
    }
    # df = pd.DataFrame(data=data)

    # invalid id_col_name raises ValueError
    with pytest.raises(ValueError):
        dset = mp.Dataset(
            data=data, id_col_name="doesnt_exist", date_col_name="col3", name="test_name"
        )

    # invalid date_col_name raises ParserError
    with pytest.raises(dateutil.parser._parser.ParserError):
        dset = mp.Dataset(
            data=data,
            id_col_name="ids",
            date_col_name="date_bad",
            id2_col_name="col2",
            name="test_name",
        )

    # dataframe with date_col_name created without error
    dset = mp.Dataset(data=data, id_col_name="COL1", date_col_name="col3", name="test_name")
    assert dset.mac.is_date_col(dset.date_col_name) is True

    # invalid id2_col_name raises DatasetID2ColError
    with pytest.raises(ValueError):
        dset = mp.Dataset(
            data=data,
            id_col_name="COL1",
            date_col_name="col3",
            id2_col_name="doesnt_exist",
            name="test_name",
        )

    dset_copy = dset.copy()
    assert dset.equals(dset_copy)

    # create_id_col creates id_col_name if none exists
    dset = mp.Dataset(data=data, name="test_name")
    dset.create_id_col()
    assert dset.id_col_name == "mp_id_col"

    # now that id_col_name exists, trying to create another should raise error
    with pytest.raises(ValueError):
        dset.create_id_col()

    # dataset lacks date_col_name but created without error
    dset = mp.Dataset(data=data, id_col_name="COL1", name="test_name")
    # id_col_name is converted to the correct case (in dataframe)
    assert dset.id_col_name == "col1"


def test_dataset_from_file():
    # dataframe lacks date column but created without error
    p = THIS_DIR / "basic.csv"

    dset = mp.Dataset.from_file(p, id_col_name="misc", name="test_name")
    assert dset.name == "test_name"
    assert dset.row_count == 3
    assert dset.col_count == 6

    dset = mp.Dataset.from_file(p, id_col_name="misc", date_col_name="date", name="test_name")
    assert dset.name == "test_name"
    assert dset.row_count == 3


def test_dataset_constructor_and_file():

    primary_from_constructor = mp.Dataset(data=primary_data)
    primary_from_file = mp.Dataset.from_file(DATA_DIR / "primary.xlsx")

    assert primary_from_constructor.name != primary_from_file.name
    assert primary_from_constructor.equals(primary_from_file) is False

    primary_from_constructor = mp.Dataset(
        data=primary_data, date_col_name="DCDate", name="primary"
    )
    primary_from_file = mp.Dataset.from_file(DATA_DIR / "primary.xlsx", date_col_name="DCDate")

    assert primary_from_constructor.equals(primary_from_file) is True


def test_display_name_generator():
    df = mp.Dataset({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})
    assert df.display_name == df.name

    df2 = mp.Dataset(
        {"A": [1, 2, 3], "albert": [4, 5, 6], "C": [7, 8, 9]},
        id_col_name="albert",
        name="renee",
        tags=["a", "b"],
    )
    assert df2.display_name == "renee_a_b"


def test_lava_dataset():

    primary_from_file = mp.LavaDataset.from_file(DATA_DIR / "primary.xlsx")
    assert primary_from_file.id_col_name == "InstrID"
    assert primary_from_file.date_col_name == "DCDate"
    assert primary_from_file.id2_col_name == "PIDN"
    assert primary_from_file.name == "primary"
