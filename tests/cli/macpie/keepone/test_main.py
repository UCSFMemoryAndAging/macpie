from pathlib import Path
from shutil import copy

import pandas as pd
import pytest

from macpie.pandas.io import file_to_dataframe
from macpie.testing import DebugDir

THIS_DIR = Path(__file__).parent.absolute()


@pytest.mark.slow
def test_cli_keepone(cli_keepone_big, debugdir):
    if debugdir:
        with DebugDir(debugdir):
            copy(cli_keepone_big, debugdir)

    result = file_to_dataframe(cli_keepone_big)
    expected_result = file_to_dataframe(THIS_DIR / "expected_result.xlsx")

    pd.testing.assert_frame_equal(result, expected_result)
