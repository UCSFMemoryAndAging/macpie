from pathlib import Path

import pytest

from macpie import pathtools


DATA_DIR = Path("tests/io/data/").resolve()


def test_create_dir_with_datetime(tmp_path):
    # not a valid path
    with pytest.raises(TypeError):
        pathtools.create_dir_with_datetime(where="non_dir")

    # not a valid directory
    with pytest.raises(NotADirectoryError):
        pathtools.create_dir_with_datetime(where=Path("tests/io/data/test.csv").resolve())

    none_param_test_dir = pathtools.create_dir_with_datetime()
    assert str(none_param_test_dir.name).startswith("new_folder")
    none_param_test_dir.rmdir()

    with_param_test_dir = pathtools.create_dir_with_datetime(where=tmp_path)
    assert str(with_param_test_dir.name).startswith("new_folder")
    with_param_test_dir.rmdir()

    with_param_test_dir = pathtools.create_dir_with_datetime("something_else", where=tmp_path)
    assert str(with_param_test_dir.name).startswith("something_else")
    with_param_test_dir.rmdir()


def test_get_files_from_dir():
    files = pathtools.get_files_from_dir(DATA_DIR)

    file_names = [f.name for f in files]

    assert "badfile.csv" in file_names
    assert "test.txt" in file_names


def test_validate_paths():
    (valid, invalid) = pathtools.validate_paths([DATA_DIR])

    assert len(valid) == 8
    assert len(invalid) == 0

    def allowed_path(p):
        if p.stem.startswith("test"):
            return False
        return True

    (valid, invalid) = pathtools.validate_paths([DATA_DIR], allowed_path=allowed_path)

    assert len(valid) == 5
    assert len(invalid) == 3


def test_validate_paths_2():
    ps = [DATA_DIR / "test.txt", DATA_DIR / "not_there.txt", DATA_DIR / "test.csv"]

    (valid, invalid) = pathtools.validate_paths(ps)

    assert len(valid) == 2
    assert len(invalid) == 1
