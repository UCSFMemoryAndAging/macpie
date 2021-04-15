from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd

from macpie._config import get_option, reset_option, set_option
from macpie.cli.main import main
from macpie.testing import assert_dfs_equal

data_dir = Path("tests/data/").resolve()
current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

cols_ignore = []
cols_ignore_pat = '^' + get_option("column.system.prefix")


def test_small_with_merge(cli_link_small_with_merge, helpers):
    expected_result = helpers.read_merged_results(current_dir / "small_with_merge_expected_result.xlsx")

    # copy file to current dir if you want to debug more
    if output_dir is not None:
        copy(cli_link_small_with_merge, current_dir)

    results = helpers.read_merged_results(cli_link_small_with_merge)

    assert_dfs_equal(results,
                     expected_result,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)


def test_small_no_merge(cli_link_small_no_merge):
    expected_dict = pd.read_excel(
        current_dir / "small.xlsx",
        sheet_name=[
            'LINK_INSTR1',
            'INSTR2_linked',
            'INSTR3_linked'
        ]
    )

    expected_primary = expected_dict['LINK_INSTR1']
    expected_secondary_instr2 = expected_dict['INSTR2_linked']
    expected_secondary_instr3 = expected_dict['INSTR3_linked']

    # copy file to current dir if you want to debug more
    if output_dir is not None:
        copy(cli_link_small_no_merge, current_dir)

    results_dict = pd.read_excel(
        cli_link_small_no_merge,
        sheet_name=[
            'small_anchor',
            'instr2_all_linked',
            'instr3_all_linked'
        ]
    )

    result_primary = results_dict['small_anchor']
    result_secondary_instr2 = results_dict['instr2_all_linked']
    result_secondary_instr3 = results_dict['instr3_all_linked']

    assert_dfs_equal(result_primary,
                     expected_primary,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)

    cols_ignore2 = [get_option("column.system.abs_diff_days"),
                    get_option("column.system.diff_days"),
                    'PIDN', 'VType', '_merge']

    assert_dfs_equal(result_secondary_instr2,
                     expected_secondary_instr2,
                     cols_ignore=cols_ignore2,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)

    assert_dfs_equal(result_secondary_instr3,
                     expected_secondary_instr3,
                     cols_ignore=cols_ignore2,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)


def test_small_no_link_id(helpers):
    # macpie link -g closest tests/cli/link/small_no_link_id.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv  # noqa: E501
    expected_result = helpers.read_merged_results(current_dir / "small_no_link_id_expected_result.xlsx")

    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'link',
        '--primary-keep', 'all',
        '--secondary-get', 'closest',
        '--secondary-days', 90,
        '--secondary-when', 'earlier_or_later',
        str((current_dir / "small_no_link_id.xlsx").resolve()),
        str((data_dir / "instr2_all.csv").resolve()),
        str((data_dir / "instr3_all.csv").resolve())
    ]

    with runner.isolated_filesystem():
        results = runner.invoke(main, cli_args)

        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob('**/result*xlsx'))

        # copy file to current dir if you want to debug more
        if output_dir is not None:
            copy(results_path, current_dir)

        results = helpers.read_merged_results(results_path)

        assert_dfs_equal(results,
                         expected_result,
                         cols_ignore=cols_ignore,
                         cols_ignore_pat=cols_ignore_pat,
                         output_dir=output_dir)


def test_small_link_suffixes(helpers):
    # macpie link -g closest tests/cli/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv  # noqa: E501

    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'link',
        '--primary-keep', 'all',
        '--secondary-get', 'closest',
        '--secondary-days', 90,
        '--secondary-when', 'earlier_or_later',
        str((current_dir / "small.xlsx").resolve()),
        str((data_dir / "instr2_all.csv").resolve()),
        str((data_dir / "instr3_all.csv").resolve())
    ]

    set_option("operators.binary.column_suffixes", ("_link", "_y"))

    with runner.isolated_filesystem():
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0
        # get the results file
        results_path = next(Path(".").glob('**/result*xlsx')).resolve()

        expected_result = helpers.read_merged_results(current_dir / "small_link_suffixes_expected_result.xlsx")

        # copy file to current dir if you want to debug more
        if output_dir is not None:
            copy(results_path, current_dir)

        results = helpers.read_merged_results(results_path)

        assert_dfs_equal(results,
                         expected_result,
                         cols_ignore=cols_ignore,
                         cols_ignore_pat=cols_ignore_pat,
                         output_dir=output_dir)

    reset_option("operators.binary.column_suffixes")
