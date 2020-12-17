from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import openpyxl as pyxl
import pandas as pd

from macpie import util

from macpie.cli.main import main
from macpie.cli.subcommands import link


current_dir = Path("tests/cli/merge/").resolve()

# output_dir = current_dir
output_dir = None


def create_fields_available(filepath):
    # manually create some fields to merge and test
    # obviously these fields should be available from the link results file
    new_fields_available = [
        ('small', 'link_date', 'x'),
        ('small', 'link_id', 'x'),
        ('small', 'DCStatus', 'x'),
        ('small', 'Col1', 'x'),
        ('small', 'Col2', 'x'),
        ('small', 'Col3', 'x'),
        ('instr2_all', 'PIDN', 'x'),
        ('instr2_all', 'DCDate', 'x'),
        ('instr2_all', 'DCStatus', 'x'),
        ('instr2_all', 'InstrID', 'x'),
        ('instr2_all', 'Col1', 'x'),
        ('instr2_all', 'Col2', 'x'),
        ('instr2_all', 'Col3', 'x'),
        ('instr3_all', 'PIDN', 'x'),
        ('instr3_all', 'DCDate', 'x'),
        ('instr3_all', 'DCStatus', 'x'),
        ('instr3_all', 'InstrID', 'x'),
        ('instr3_all', 'Col1', 'x'),
        ('instr3_all', 'Col2', 'x'),
        ('instr3_all', 'Col3', 'x')
    ]
    fields_available_ds = link.LinkQuery.create_fields_available_sheet(new_fields_available)

    wb = pyxl.load_workbook(filepath)
    del wb[link.SHEETNAME_FIELDS_AVAILABLE]
    wb.save(filepath)

    writer = pd.ExcelWriter(str(filepath), engine='openpyxl', mode='a')
    fields_available_ds.to_excel(writer)
    writer.save()


def test_small_with_merge(link_small_with_merge, helpers, tmp_path):
    expected_result = helpers.read_merged_results(current_dir / "small_expected_results.xlsx")

    copied_file = Path(copy(link_small_with_merge, tmp_path))
    create_fields_available(copied_file)

    runner = CliRunner()
    cli_args = ['merge', str(copied_file.resolve())]

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


def test_small_no_merge(link_small_no_merge, helpers, tmp_path):
    expected_result = helpers.read_merged_results(current_dir / "small_expected_results.xlsx")

    copied_file = tmp_path / Path(copy(link_small_no_merge, tmp_path))
    create_fields_available(copied_file)

    runner = CliRunner()
    cli_args = ['merge', str(copied_file.resolve())]

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
