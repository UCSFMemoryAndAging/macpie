from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import openpyxl as pyxl
import pandas as pd
import pytest

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
        ('full', 'link_date', 'x'),
        ('full', 'link_id', 'x'),
        ('full', 'DCStatus', 'x'),
        ('full', 'Col1', 'x'),
        ('full', 'Col2', 'x'),
        ('full', 'Col3', 'x'),
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


@pytest.mark.slow
def test_full_no_merge(link_full_no_merge, helpers, tmp_path):
    expected_result = helpers.read_merged_results(current_dir / "full_expected_results.xlsx")

    copied_file = Path(copy(link_full_no_merge, tmp_path))
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

        results_wb = pyxl.load_workbook(results_path)
        expected_results_wb = pyxl.load_workbook(current_dir / "full_expected_results.xlsx")

        assert set(results_wb.sheetnames) == set(expected_results_wb.sheetnames)

        results = helpers.read_merged_results(results_path)
        util.testing.assert_dfs_equal(results, expected_result, output_dir=output_dir)
