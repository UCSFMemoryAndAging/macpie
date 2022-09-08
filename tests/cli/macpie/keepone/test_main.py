from pathlib import Path
from shutil import copy

import pandas as pd
import pytest

import macpie as mp
from macpie.testing import DebugDir

THIS_DIR = Path(__file__).parent.absolute()


@pytest.mark.slow
def test_cli_keepone(cli_keepone_big, debugdir):
    if debugdir:
        with DebugDir(debugdir):
            copy(cli_keepone_big, debugdir)

    result = mp.pandas.read_file(cli_keepone_big)
    expected_result = mp.pandas.read_file(THIS_DIR / "expected_result.xlsx")

    pd.testing.assert_frame_equal(result, expected_result)
