from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd
import pytest

from macpie import MergeableAnchoredList
from macpie._config import get_option
from macpie.cli.macpie.main import main
from macpie.testing import assert_dfs_equal

current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

cols_ignore = [
    ("instr2_all", "InstrID_x"),
]
cols_ignore_pat = "^" + get_option("column.system.prefix")


@pytest.mark.slow
def test_merge_again(tmp_path):
    # macpie merge tests/cli/macpie/merge/merge_again/full_merged_once.xlsx

    expected_result = pd.read_excel(
        current_dir / "expected_results.xlsx",
        sheet_name=MergeableAnchoredList.merged_dsetname,
        header=[0, 1],
        index_col=None,
    )

    runner = CliRunner()

    # the full_merged_once.xlsx file was created from the result
    # of the tests.cli.merge.test_full.test_full_no_merge test,
    # and then removing the first duplicate in each set of duplicates for the
    # instr2_all dataset
    cli_args = ["merge", str((current_dir / "full_merged_once.xlsx").resolve())]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob("**/result*xlsx"))

        # copy file to current dir if you want to debug more
        if output_dir is not None:
            copy(results_path, current_dir)

        results = pd.read_excel(
            results_path,
            sheet_name=MergeableAnchoredList.merged_dsetname,
            header=[0, 1],
            index_col=None,
        )

        assert_dfs_equal(
            results,
            expected_result,
            cols_ignore=cols_ignore,
            cols_ignore_pat=cols_ignore_pat,
            output_dir=output_dir,
        )
