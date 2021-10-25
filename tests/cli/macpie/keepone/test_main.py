from pathlib import Path
from shutil import copy

import pytest

from macpie.pandas.io import file_to_dataframe
from macpie.testing import assert_dfs_equal


data_dir = Path("tests/data/").resolve()
current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None


@pytest.mark.slow
def test_cli_keepone(cli_keepone_big, helpers):

    # copy file to current dir if you want to debug more
    if output_dir is not None:
        copy(cli_keepone_big, current_dir)

    result = file_to_dataframe(cli_keepone_big)
    expected_result = file_to_dataframe(current_dir / "expected_result.xlsx")

    assert_dfs_equal(result, expected_result, output_dir=output_dir)
