from pathlib import Path

import pytest

from macpie import pathtools
from macpie.exceptions import PathError

current_dir = Path("tests/io/data/").resolve()


def test_create_output_dir(tmp_path):
    # not a valid path
    with pytest.raises(PathError):
        pathtools.create_output_dir("non_dir")

    # not a valid directory
    with pytest.raises(PathError):
        pathtools.create_output_dir(Path('tests/io/data/test.csv').resolve())

    none_param_test_dir = pathtools.create_output_dir()
    assert str(none_param_test_dir.name).startswith("new_folder_")
    none_param_test_dir.rmdir()

    with_param_test_dir = pathtools.create_output_dir(tmp_path)
    assert str(with_param_test_dir.name).startswith("new_folder_")
    with_param_test_dir.rmdir()

    with_param_test_dir = pathtools.create_output_dir(tmp_path, 'something_else')
    assert str(with_param_test_dir.name).startswith("something_else_")
    with_param_test_dir.rmdir()


def test_get_files_from_dir():
    files = pathtools.get_files_from_dir(current_dir)

    file_names = [f.name for f in files]

    assert 'badfile.csv' in file_names
    assert 'test.txt' in file_names


def test_validate_filepath():
    with pytest.raises(PathError):
        pathtools.validate_filepath(current_dir)

    p = pathtools.validate_filepath(current_dir / "test.txt")
    assert p.stem == "test"


def test_validate_filepaths():
    (valid, invalid) = pathtools.validate_filepaths([current_dir])

    assert len(valid) == 7
    assert len(invalid) == 0

    def allowed_file(p):
        if p.stem.startswith('test'):
            return False
        return True

    (valid, invalid) = pathtools.validate_filepaths([current_dir], allowed_file)

    assert len(valid) == 4
    assert len(invalid) == 3


def test_validate_filepaths_2():
    ps = [
        current_dir / "test.txt",
        current_dir / "not_there.txt",
        current_dir / "test.csv"
    ]

    (valid, invalid) = pathtools.validate_filepaths(ps)

    assert len(valid) == 2
    assert len(invalid) == 1
