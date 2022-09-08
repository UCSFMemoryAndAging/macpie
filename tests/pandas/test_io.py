from pathlib import Path

import pytest

from macpie.pandas import read_file


DATA_DIR = Path("tests/data/").resolve()

THIS_DIR = Path("tests/io/data/").resolve()


def test_read_file():
    bad_file = THIS_DIR / "badfile.csv"

    with pytest.raises(Exception):
        read_file(bad_file)

    bad_suffix = THIS_DIR / "badfile.zzz"

    with pytest.raises(Exception):
        read_file(bad_suffix)


def test_read_csv():

    empty_file = THIS_DIR / "empty.csv"
    with pytest.raises(Exception):
        read_file(empty_file)

    p1 = THIS_DIR / "test.csv"
    df1 = read_file(p1)

    # test column count and headers
    assert len(df1.columns) == 2
    assert df1.columns[0] == "pidn"
    assert df1.columns[1] == "date"

    # test row count
    assert len(df1.index) == 4


def test_import_xl():
    bad_file = THIS_DIR / "bad_xl.xlsx"
    with pytest.raises(Exception):
        read_file(bad_file)

    p1 = THIS_DIR / "test.xlsx"
    df1 = read_file(p1)

    # test column count and headers
    assert len(df1.columns) == 9
    assert df1.columns[0] == "PIDN"
    assert df1.columns[1] == "InstrType"
    assert df1.columns[2] == "DCDate"

    # test row count
    assert len(df1.index) == 5


def test_read_csv_medium():
    p1 = DATA_DIR / "instr1_primaryall.csv"
    df1 = read_file(p1)

    # test column count and headers
    assert df1.mac.col_count() == 60
    assert df1.columns[0] == "PIDN"
    assert df1.columns[3] == "DCDate"

    # test row count
    assert df1.mac.row_count() == 13808


@pytest.mark.slow
def test_read_excel_medium():
    p1 = DATA_DIR / "instr1_primaryall.xlsx"
    df1 = read_file(p1)

    # test column count and headers
    assert df1.mac.col_count() == 58
    assert df1.columns[0] == "PIDN"
    assert df1.columns[1] == "DCDate"

    # test row count
    assert df1.mac.row_count() == 13808
