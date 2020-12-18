from pathlib import Path

from click.testing import CliRunner
import pytest

from macpie.cli.main import main

data_dir = Path("tests/data/").resolve()
current_dir = Path("tests/cli/link/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = ['PIDN', 'VType', '_merge', '_abs_diff_days', '_duplicates']


@pytest.fixture(scope="session")
def link_small_with_merge():
    # macpie link -g closest tests/cli/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv
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
        yield results_path.resolve()


@pytest.fixture(scope="session")
def link_small_no_merge():
    # macpie link -g closest --no-merge-results tests/cli/link/small.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv
    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'link',
        '--no-merge-results',
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
        yield results_path.resolve()


@pytest.fixture(scope="session")
def link_full_no_merge():
    # macpie link -g closest --no-merge-results tests/cli/link/full.xlsx tests/data/instr2_all.csv tests/data/instr3_all.csv
    runner = CliRunner()

    cli_args = [
        '--id2-col', 'pidn',
        '--date-col', 'dcdate',
        'link',
        '--no-merge-results',
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
        yield results_path.resolve()
