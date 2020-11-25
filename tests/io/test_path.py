from pathlib import Path

import pytest

from macpie import errors, io


def test_create_output_dir(tmp_path):
    # not a valid path
    with pytest.raises(errors.PathError):
        io.create_output_dir("non_dir")

    # not a valid directory
    with pytest.raises(errors.PathError):
        io.create_output_dir(Path('tests/io/data/test.csv'))

    none_param_test_dir = io.create_output_dir()
    assert str(none_param_test_dir.name).startswith("new_folder_")
    none_param_test_dir.rmdir()

    with_param_test_dir = io.create_output_dir(tmp_path)
    assert str(with_param_test_dir.name).startswith("new_folder_")
    with_param_test_dir.rmdir()

    with_param_test_dir = io.create_output_dir(tmp_path, 'something_else')
    assert str(with_param_test_dir.name).startswith("something_else_")
    with_param_test_dir.rmdir()


def test_get_files_from_dir():
    p = Path('tests/io/data')
    files = io.get_files_from_dir(p)

    file_names = [f.name for f in files]

    assert 'badfile.csv' in file_names
    assert 'test.txt' in file_names


def test_validate_filepaths():
    p = Path('tests/io/data')

    (valid, invalid) = io.validate_filepaths([p])

    assert len(valid) == 7
    assert len(invalid) == 0

    def allowed_file(p):
        if p.stem.startswith('test'):
            return False
        return True

    (valid, invalid) = io.validate_filepaths([p], allowed_file)

    assert len(valid) == 4
    assert len(invalid) == 3


def test_validate_filepaths_2():
    ps = [
        Path('tests/io/data/test.txt'),
        Path('tests/io/data/not_there.txt'),
        Path('tests/io/data/test.csv')
    ]

    (valid, invalid) = io.validate_filepaths(ps)

    assert len(valid) == 2
    assert len(invalid) == 1
