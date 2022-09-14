from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd
import pytest

import macpie as mp
from macpie.cli.macpie.main import main
from macpie.testing import DebugDir

THIS_DIR = Path(__file__).parent.absolute()

COL_FILTER_KWARGS = {
    "items": [("instr2_all", "InstrID_x")],
    "regex": "^" + mp.get_option("column.system.prefix"),
    "invert": True,
}


@pytest.mark.slow
def test_merge_again(tmp_path, debugdir):
    # macpie merge tests/cli/macpie/merge/merge_again/full_merged_once.xlsx

    expected_result = pd.read_excel(
        THIS_DIR / "expected_results.xlsx",
        sheet_name=mp.MergeableAnchoredList.merged_dsetname,
        header=[0, 1],
        index_col=None,
    )

    runner = CliRunner()

    # the full_merged_once.xlsx file was created from the result
    # of the tests.cli.merge.test_full.test_full_no_merge test,
    # and then removing the first duplicate in each set of duplicates for the
    # instr2_all dataset
    cli_args = ["merge", str((THIS_DIR / "full_merged_once.xlsx").resolve())]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob("**/*.xlsx"))

        # copy file to debugdir if you want to debug more
        if debugdir:
            with DebugDir(debugdir):
                copy(results_path, debugdir)

        results = pd.read_excel(
            results_path,
            sheet_name=mp.MergeableAnchoredList.merged_dsetname,
            header=[0, 1],
            index_col=None,
        )

        (left, right) = results.mac.conform(expected_result, subset_pair_kwargs=COL_FILTER_KWARGS)
        pd.testing.assert_frame_equal(left, right)
