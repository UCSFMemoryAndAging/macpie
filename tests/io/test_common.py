from pathlib import Path

import pytest

from macpie.exceptions import WriteError
from macpie.io import create_output_dir, get_files_from_dir


def test_create_output_dir(tmp_path):
    # not a valid path
    with pytest.raises(WriteError):
        create_output_dir("non_dir")

    # not a valid directory
    with pytest.raises(WriteError):
        create_output_dir(Path('tests/io/data/test.csv'))

    none_param_test_dir = create_output_dir()
    assert str(none_param_test_dir.name).startswith("results_")
    none_param_test_dir.rmdir()

    with_param_test_dir = create_output_dir(tmp_path)
    assert str(with_param_test_dir.name).startswith("results_")
    with_param_test_dir.rmdir()


def test_get_files_from_dir():
    p = Path('tests/io/data')
    files = get_files_from_dir(p)

    file_names = [f.name for f in files]

    assert 'badfile.csv' in file_names
    assert 'test.txt' in file_names
