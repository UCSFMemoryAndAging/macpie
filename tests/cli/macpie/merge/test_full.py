from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import openpyxl as pyxl
import pandas as pd
import pytest

from macpie import DatasetFields, MACPieExcelWriter, MergeableAnchoredList
from macpie.io.excel import (
    DATASETS_SHEET_NAME,
    COLLECTION_SHEET_NAME,
)
from macpie.testing import assert_dfs_equal

from macpie.cli.macpie.main import main


current_dir = Path(__file__).parent.absolute()

# output_dir = current_dir
output_dir = None


def create_available_fields(filepath):
    # manually create some fields to merge and test
    # obviously these fields should be available from the link results file
    available_fields_rows = [
        ("full", "Col1"),
        ("full", "Col2"),
        ("full", "Col3"),
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
    available_fields.append_col_fill("x", header=MergeableAnchoredList.to_merge_column_name)

    wb = pyxl.load_workbook(filepath)
    del wb[MergeableAnchoredList.available_fields_sheetname]
    wb.save(filepath)

    with MACPieExcelWriter(filepath, mode="a", engine="mp_openpyxl") as writer:
        available_fields.to_excel(writer)


@pytest.mark.slow
def test_full_no_merge(cli_link_full_no_merge, tmp_path):
    cli_link_full_no_merge_copy = Path(copy(cli_link_full_no_merge, tmp_path))

    expected_result = pd.read_excel(
        current_dir / "full_expected_results.xlsx",
        sheet_name=MergeableAnchoredList.merged_dsetname,
        header=[0, 1],
        index_col=None,
    )

    create_available_fields(cli_link_full_no_merge_copy)

    runner = CliRunner()
    cli_args = ["merge", str(cli_link_full_no_merge_copy.resolve())]

    with runner.isolated_filesystem(temp_dir=tmp_path):
        results = runner.invoke(main, cli_args)
        assert results.exit_code == 0

        # get the results file
        results_path = next(Path(".").glob("**/result*xlsx"))

        # copy file to current dir if you want to debug more
        if output_dir is not None:
            copy(results_path, current_dir)

        results_wb = pyxl.load_workbook(results_path, read_only=True, data_only=True)
        # expected_results_wb = pyxl.load_workbook(current_dir / "full_expected_results.xlsx")

        expected_sheetnames = [
            "instr2_all_DUPS",
            "instr3_all_DUPS",
            COLLECTION_SHEET_NAME,
            DATASETS_SHEET_NAME,
            MergeableAnchoredList.available_fields_sheetname,
            MergeableAnchoredList.merged_dsetname,
        ]

        assert all(sheetname in results_wb.sheetnames for sheetname in expected_sheetnames)

        results = pd.read_excel(
            results_path,
            sheet_name=MergeableAnchoredList.merged_dsetname,
            header=[0, 1],
            index_col=None,
        )

        assert_dfs_equal(results, expected_result, output_dir=output_dir)
