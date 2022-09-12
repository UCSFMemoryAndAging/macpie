from pathlib import Path
from shutil import copy

import pandas as pd
from click.testing import CliRunner

import macpie as mp
from macpie.cli.mppair.main import main
from macpie.testing import DebugDir

THIS_DIR = Path(__file__).parent.absolute()


def test_compare(tmp_path, debugdir):
    # mppair left.xlsx right.xlsx compare

    runner = CliRunner()

    cli_args = [
        str(Path(THIS_DIR / "left.xlsx").resolve()),
        str(Path(THIS_DIR / "right.xlsx").resolve()),
        "compare",
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)

        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob("**/*.xlsx"))

        # copy file to current dir if you want to debug more
        if debugdir:
            with DebugDir(debugdir):
                copy(results_path, debugdir)

        result = pd.read_excel(results_path, sheet_name=[0, 1])
        expected_result = pd.read_excel(THIS_DIR / "expected_result.xlsx", sheet_name=[0, 1])

        pd.testing.assert_frame_equal(result[0], expected_result[0])
        pd.testing.assert_frame_equal(result[1], expected_result[1])
