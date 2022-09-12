from pathlib import Path
from shutil import copy

import pandas as pd
from click.testing import CliRunner

import macpie as mp
from macpie.cli.mppair.main import main
from macpie.testing import DebugDir

THIS_DIR = Path(__file__).parent.absolute()


def test_conform_replace_compare(tmp_path, debugdir):
    # mppair -n "DCDate" -i left.xlsx right.xlsx conform -i replace -r "c" -v "b" replace -r "CDR[MZ]" -v CDR --regex compare
    # 1. conform will drop the DCDate column (where there is one difference)
    # 2. replace values such that right values are identical to left values
    # 3. compare should result in no differences

    runner = CliRunner()

    cli_args = [
        "--sheet",
        "Sheet1",
        "--filter-name",
        "DCDate",
        "--filter-invert",
        str(Path(THIS_DIR / "left.xlsx").resolve()),
        str(Path(THIS_DIR / "right.xlsx").resolve()),
        "conform",
        "--index-order",
        "replace",
        "--to-replace",
        "c",
        "--value",
        "b",
        "replace",
        "--regex",
        "--to-replace",
        "CDR[MZ]",
        "--value",
        "CDR",
        "compare",
    ]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)

        assert results.exit_code == 0

        # get results files
        result_paths = list(Path(".").glob("**/*.xlsx"))

        # 2 results files (one for conformed left, one for conformed right,
        # and no diffs file meaning no differences found)
        assert len(result_paths) == 2
