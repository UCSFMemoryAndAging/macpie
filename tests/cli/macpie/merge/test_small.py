from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import openpyxl as pyxl
import pandas as pd

from macpie import DatasetFields, MACPieExcelWriter, MergeableAnchoredList
from macpie._config import get_option
from macpie.testing import assert_dfs_equal

from macpie.cli.macpie.main import main

current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None

cols_ignore = [("instr2_all", "InstrID_x"), ("instr3_all", "InstrID_x")]
cols_ignore_pat = "^" + get_option("column.system.prefix")


def create_available_fields(filepath):
    # manually create some fields to merge and test
    # obviously these fields should be available from the link results file
    available_fields_rows = [
        ("small", "Col1"),
        ("small", "Col2"),
        ("small", "Col3"),
        ("instr2_all", "Col1"),
        ("instr2_all", "Col2"),
        ("instr2_all", "Col3"),
        ("instr3_all", "Col1"),
        ("instr3_all", "Col2"),
        ("instr3_all", "Col3"),
    ]

    available_fields = DatasetFields(
        *available_fields_rows, title=MergeableAnchoredList.available_fields_sheetname
    )

    # mark them as selected
    available_fields.append_col_fill("x", header=MergeableAnchoredList.to_merge_column_name)

    wb = pyxl.load_workbook(filepath)
    del wb[MergeableAnchoredList.available_fields_sheetname]
    wb.save(filepath)

    with MACPieExcelWriter(filepath, mode="a", engine="mp_openpyxl") as writer:
        available_fields.to_excel(writer)


def test_small_with_merge(cli_link_small_with_merge, tmp_path):
    run(cli_link_small_with_merge, tmp_path)


def test_small_no_merge(cli_link_small_no_merge, tmp_path):
    run(cli_link_small_no_merge, tmp_path)


def run(filepath, tmp_path):
    expected_result = pd.read_excel(
        current_dir / "small_expected_results.xlsx",
        sheet_name=MergeableAnchoredList.merged_dsetname,
        header=[0, 1],
        index_col=None,
    )

    create_available_fields(filepath)

    runner = CliRunner()
    cli_args = ["merge", str(filepath.resolve())]

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
