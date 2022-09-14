from pathlib import Path
from shutil import copy

from click.testing import CliRunner
import openpyxl as pyxl
import pandas as pd

import macpie as mp
from macpie.testing import DebugDir
from macpie.cli.macpie.main import main


THIS_DIR = Path(__file__).parent.absolute()

COL_FILTER_KWARGS = {
    "items": [("instr2_all", "InstrID_x"), ("instr3_all", "InstrID_x")],
    "regex": "^" + mp.get_option("column.system.prefix"),
    "invert": True,
}


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

    available_fields = mp.DatasetFields(
        *available_fields_rows, title=mp.MergeableAnchoredList.available_fields_sheetname
    )

    # mark them as selected
    available_fields.append_col_fill("x", header=mp.MergeableAnchoredList.to_merge_column_name)

    wb = pyxl.load_workbook(filepath)
    del wb[mp.MergeableAnchoredList.available_fields_sheetname]
    wb.save(filepath)

    with mp.MACPieExcelWriter(filepath, mode="a", engine="mp_openpyxl") as writer:
        available_fields.to_excel(writer)


def test_small_with_merge(cli_link_small_with_merge, tmp_path, debugdir):
    run(cli_link_small_with_merge, tmp_path, debugdir)


def test_small_no_merge(cli_link_small_no_merge, tmp_path, debugdir):
    run(cli_link_small_no_merge, tmp_path, debugdir)


def run(filepath, tmp_path, debugdir):
    expected_result = pd.read_excel(
        THIS_DIR / "small_expected_results.xlsx",
        sheet_name=mp.MergeableAnchoredList.merged_dsetname,
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
        results_path = next(Path(".").glob("**/*.xlsx"))

        # copy file to current dir if you want to debug more
        if debugdir:
            with DebugDir(debugdir):
                copy(results_path, debugdir)

        results = pd.read_excel(
            results_path,
            sheet_name=mp.MergeableAnchoredList.merged_dsetname,
            header=[0, 1],
            index_col=None,
        )

        (left, right) = results.mac.conform(
            expected_result, subset_pair_kwargs=COL_FILTER_KWARGS, values_order=True
        )
        pd.testing.assert_frame_equal(left, right)
