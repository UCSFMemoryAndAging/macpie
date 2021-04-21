from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import openpyxl as pyxl

from macpie._config import get_option
from macpie.io.excel import MACPieExcelWriter
from macpie.testing import assert_dfs_equal
from macpie.util.datasetfields import DatasetFields

from macpie.cli.main import main

current_dir = Path("tests/cli/merge/").resolve()

# output_dir = current_dir
output_dir = None

cols_ignore = [('instr2_all', 'InstrID_x'), ('instr3_all', 'InstrID_x')]
cols_ignore_pat = '^' + get_option("column.system.prefix")


def create_available_fields(filepath):
    # manually create some fields to merge and test
    # obviously these fields should be available from the link results file
    available_fields_rows = [
        ('small', 'Col1'),
        ('small', 'Col2'),
        ('small', 'Col3'),
        ('instr2_all', 'Col1'),
        ('instr2_all', 'Col2'),
        ('instr2_all', 'Col3'),
        ('instr3_all', 'Col1'),
        ('instr3_all', 'Col2'),
        ('instr3_all', 'Col3')
    ]

    available_fields = DatasetFields(*available_fields_rows, title=get_option("sheet.name.available_fields"))

    # mark them as selected
    available_fields.append_col_fill("x", header=get_option("column.to_merge"))

    wb = pyxl.load_workbook(filepath)
    del wb[get_option("sheet.name.available_fields")]
    wb.save(filepath)

    with MACPieExcelWriter(filepath, mode='a') as writer:
        available_fields.to_excel(writer)


def test_small_with_merge(cli_link_small_with_merge, helpers):
    run(cli_link_small_with_merge, helpers)


def test_small_no_merge(cli_link_small_no_merge, helpers):
    run(cli_link_small_no_merge, helpers)


def run(filepath, helpers):
    expected_result = helpers.read_merged_results(current_dir / "small_expected_results.xlsx")

    create_available_fields(filepath)

    runner = CliRunner()
    cli_args = ['merge', str(filepath.resolve())]

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
