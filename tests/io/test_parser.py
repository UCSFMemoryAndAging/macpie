from pathlib import Path

import pytest

from macpie.exceptions import FileImportError
from macpie.io import allowed_file, import_file

data_dir = Path("tests/data/")
current_dir = Path('tests/io/data/')


def test_allowed_file():
    temp_files = current_dir / '~$test.csv'
    assert allowed_file(temp_files) is False

    results_file = current_dir / 'results_test.csv'
    assert allowed_file(results_file) is False

    bad_suffix = current_dir / 'test.zzz'
    assert allowed_file(bad_suffix) is False


def test_import_file():
    bad_file = current_dir / 'badfile.csv'

    with pytest.raises(FileImportError):
        import_file(bad_file)

    bad_suffix = current_dir / 'badfile.zzz'

    with pytest.raises(FileImportError):
        import_file(bad_suffix)


def test_import_csv():

    empty_file = current_dir / 'empty.csv'
    with pytest.raises(FileImportError):
        import_file(empty_file)

    p1 = current_dir / 'test.csv'
    df1 = import_file(p1)

    # test column count and headers
    assert len(df1.columns) == 2
    assert df1.columns[0] == 'pidn'
    assert df1.columns[1] == 'date'

    # test row count
    assert len(df1.index) == 4


def test_import_xl():
    bad_file = current_dir / 'bad_xl.xlsx'
    with pytest.raises(FileImportError):
        import_file(bad_file)

    p1 = current_dir / 'test.xlsx'
    df1 = import_file(p1)

    # test column count and headers
    assert len(df1.columns) == 9
    assert df1.columns[0] == 'PIDN'
    assert df1.columns[1] == 'InstrType'
    assert df1.columns[2] == 'DCDate'

    # test row count
    assert len(df1.index) == 5


def test_import_csv_medium():
    p1 = data_dir / 'instr1_primaryall.csv'
    df1 = import_file(p1)

    # test column count and headers
    assert df1.mac.num_cols() == 60
    assert df1.columns[0] == 'PIDN'
    assert df1.columns[3] == 'DCDate'

    # test row count
    assert df1.mac.num_rows() == 13808


@pytest.mark.slow
def test_import_xl_medium():
    p1 = data_dir / 'instr1_primaryall.xlsx'
    df1 = import_file(p1)

    # test column count and headers
    assert df1.mac.num_cols() == 58
    assert df1.columns[0] == 'PIDN'
    assert df1.columns[1] == 'DCDate'

    # test row count
    assert df1.mac.num_rows() == 13808
