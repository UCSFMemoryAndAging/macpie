from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pytest

from macpie import util
from macpie.cli.main import main


current_dir = Path("tests/cli/merge/merge_again").resolve()

# output_dir = current_dir
output_dir = None


@pytest.mark.slow
def test_merge_again(helpers, tmp_path):
    # macpie merge tests/cli/merge/merge_again/full_merged_once.xlsx

    expected_result = helpers.read_merged_results(current_dir / "expected_results.xlsx")

    runner = CliRunner()

    # the full_merged_once.xlsx file was created from the result
    # of the tests.cli.merge.test_full.test_full_no_merge test,
    # and then removing the first duplicate in each set of duplicates for the
    # instr2_all data object
    cli_args = ['merge', str((current_dir / "full_merged_once.xlsx").resolve())]

    with runner.isolated_filesystem():
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob('**/result*xlsx'))

        # copy file to current dir if you want to debug more
        if output_dir is not None:
            copy(results_path, current_dir)

        results = helpers.read_merged_results(results_path)
        util.testing.assert_dfs_equal(results, expected_result, output_dir=output_dir)
