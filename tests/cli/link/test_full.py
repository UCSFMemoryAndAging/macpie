from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import pandas as pd
import pytest

from macpie._config import get_option
from macpie.testing import assert_dfs_equal
from macpie.cli.main import main


data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/cli/link/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = [
    'PIDN', 'VType', 'InstrID_x', 'link_id_x'
]
cols_ignore_pat = '^' + get_option("column.system.prefix")

expected_dict = pd.read_excel(
    current_dir / "full.xlsx",
    sheet_name=[
        'LINK_INSTR1',
        'INSTR2_linked',
        'INSTR3_linked'
    ]
)

expected_primary = expected_dict['LINK_INSTR1']
expected_secondary_instr2 = expected_dict['INSTR2_linked']
expected_secondary_instr3 = expected_dict['INSTR3_linked']


@pytest.mark.slow
def test_full_no_merge(cli_link_full_no_merge):
    # copy file to current dir if you want to debug more
    if output_dir is not None:
        copy(cli_link_full_no_merge, current_dir)

    results_dict = pd.read_excel(
        cli_link_full_no_merge,
        sheet_name=[
            'full_anchor',
            'instr2_all_DUPS',
            'instr3_all_DUPS'
        ]
    )

    result_primary = results_dict['full_anchor']
    result_secondary_instr2 = results_dict['instr2_all_DUPS']
    result_secondary_instr3 = results_dict['instr3_all_DUPS']

    assert_dfs_equal(result_primary, expected_primary, output_dir=output_dir)

    assert_dfs_equal(result_secondary_instr2,
                     expected_secondary_instr2,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)

    assert_dfs_equal(result_secondary_instr3,
                     expected_secondary_instr3,
                     cols_ignore=cols_ignore,
                     cols_ignore_pat=cols_ignore_pat,
                     output_dir=output_dir)


@pytest.mark.slow
def test_full_no_link_id():
    # macpie link -g closest tests/cli/link/full_no_link_id.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv

    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'link',
        '--primary-keep', 'all',
        '--secondary-get', 'closest',
        '--secondary-days', 90,
        '--secondary-when', 'earlier_or_later',
        str((current_dir / "full_no_link_id.xlsx").resolve()),
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
                'instr2_all_DUPS',
                'instr3_all_DUPS'
            ]
        )

        result_secondary_instr2 = results_dict['instr2_all_DUPS']
        result_secondary_instr3 = results_dict['instr3_all_DUPS']

        assert_dfs_equal(result_secondary_instr2,
                         expected_secondary_instr2,
                         cols_ignore=cols_ignore,
                         cols_ignore_pat=cols_ignore_pat,
                         output_dir=output_dir)

        assert_dfs_equal(result_secondary_instr3,
                         expected_secondary_instr3,
                         cols_ignore=cols_ignore,
                         cols_ignore_pat=cols_ignore_pat,
                         output_dir=output_dir)
