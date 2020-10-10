from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd
import pytest

from macpie.cli import main
from macpie.testing import assert_dfs_equal


data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/cli/link/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = ['PIDN', 'VType', '_merge', '_abs_diff_days', '_duplicates']


def test_small():
    # macpie -j pidn -d dcdate link -k all -g closest -d 90 -w earlier_or_later tests/cli/link/instr1_primaryall.csv
    expected_dict = pd.read_excel(
        current_dir / "small.xlsx",
        sheet_name=[
            'LINK_INSTR1',
            'INSTR2_linked',
            'INSTR3_linked'
        ],
        engine='openpyxl'
    )

    expected_primary = expected_dict['LINK_INSTR1']
    expected_secondary_instr2 = expected_dict['INSTR2_linked']
    expected_secondary_instr3 = expected_dict['INSTR3_linked']

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

    with runner.isolated_filesystem():
        results = runner.invoke(main, cli_args)

        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob('**/result*xlsx'))

        # copy file to current dir if you want to debug more
        if output_dir is not None:
            copy(results_path, current_dir)

        results_dict = pd.read_excel(
            results_path,
            sheet_name=[
                'small',
                'instr2_all_linked',
                'instr3_all_linked'
            ],
            engine='openpyxl'
        )

        result_primary = results_dict['small']
        result_secondary_instr2 = results_dict['instr2_all_linked']
        result_secondary_instr3 = results_dict['instr3_all_linked']

        assert_dfs_equal(result_primary, expected_primary, output_dir=output_dir)
        assert_dfs_equal(result_secondary_instr2, expected_secondary_instr2, cols_ignore=cols_ignore, output_dir=output_dir)
        assert_dfs_equal(result_secondary_instr3, expected_secondary_instr3, cols_ignore=cols_ignore, output_dir=output_dir)


@pytest.mark.slow
def test_full():
    # macpie -j pidn -d dcdate link -k all -g closest -d 90 -w earlier_or_later tests/cli/link/instr1_primaryall.csv
    expected_dict = pd.read_excel(
        current_dir / "full.xlsx",
        sheet_name=[
            'LINK_INSTR1',
            'INSTR2_linked',
            'INSTR3_linked'
        ],
        engine='openpyxl'
    )

    expected_primary = expected_dict['LINK_INSTR1']
    expected_secondary_instr2 = expected_dict['INSTR2_linked']
    expected_secondary_instr3 = expected_dict['INSTR3_linked']

    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'link',
        '--primary-keep', 'all',
        '--secondary-get', 'closest',
        '--secondary-days', 90,
        '--secondary-when', 'earlier_or_later',
        str((current_dir / "full.xlsx").resolve()),
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

        results_dict = pd.read_excel(
            results_path,
            sheet_name=[
                'full',
                'instr2_all_linked(DUPS)',
                'instr3_all_linked(DUPS)'
            ],
            engine='openpyxl'
        )

        result_primary = results_dict['full']
        result_secondary_instr2 = results_dict['instr2_all_linked(DUPS)']
        result_secondary_instr3 = results_dict['instr3_all_linked(DUPS)']

        assert_dfs_equal(result_primary, expected_primary, output_dir=output_dir)
        assert_dfs_equal(result_secondary_instr2, expected_secondary_instr2, cols_ignore=cols_ignore, output_dir=output_dir)
        assert_dfs_equal(result_secondary_instr3, expected_secondary_instr3, cols_ignore=cols_ignore, output_dir=output_dir)
